"""
Contexte de lecture workflow : charge tickets, choix et phases une seule fois
par requête HTTP / par service.
"""

from riad.services.order_content import (
    CLEARING_STATUSES,
    SERVE_PRODUCT_SEQUENCE,
    SERVE_PHASE_SECTION_FLAGS,
    WORKFLOW_PRODUCT_SECTIONS,
    _choice_section_name,
)
from riad.services.prefetched_data import (
    PrefetchMissingError,
    get_prefetched_workflow_items,
)
from riad.services.service_category_readiness import (
    CATEGORY_CLEARED_STATUS,
    CATEGORY_SECTIONS,
    CATEGORY_SERVE_PHASE_STATUS,
    CATEGORY_SERVED_STATUS,
    SERVICE_CATEGORIES,
    WORKFLOW_TICKET_STATUSES,
    PHASE_CLEARED,
    PHASE_NOT_APPLICABLE,
    PHASE_READY_TO_CLEAR,
    PHASE_READY_TO_SERVE,
    PHASE_SERVED_WAITING_CLEAR,
    PHASE_WAITING_KITCHEN,
    _category_has_clear_step,
    _status_index,
    build_served_since_info,
    get_category_phase_display,
    kitchen_item_belongs_to_category,
)


class WorkflowReadContext:
    __slots__ = (
        "service",
        "order",
        "_prefetched_items",
        "_items_by_category",
        "_items_loaded",
        "_order_sections",
        "_category_has_choices",
        "_category_states",
        "_category_phases",
        "_workflow_status",
        "_order_flags",
    )

    def __init__(self, service, order, *, prefetched_items=None):
        self.service = service
        self.order = order
        if prefetched_items is None:
            try:
                prefetched_items = get_prefetched_workflow_items(order)
            except PrefetchMissingError:
                prefetched_items = None
        self._prefetched_items = prefetched_items
        self._items_by_category = None
        self._items_loaded = False
        self._order_sections = None
        self._category_has_choices = {}
        self._category_states = {}
        self._category_phases = {}
        self._workflow_status = None
        self._order_flags = None

    def _load_items(self):
        if self._items_loaded:
            return

        self._items_loaded = True
        self._items_by_category = {category: [] for category in SERVICE_CATEGORIES}

        if not self.order:
            return

        if self._prefetched_items is not None:
            items = self._prefetched_items
        else:
            from riad.models import KitchenTicketItem

            items = (
                KitchenTicketItem.objects
                .filter(
                    ticket__order=self.order,
                    ticket__status__in=WORKFLOW_TICKET_STATUSES,
                    ticket__service=self.service,
                )
                .select_related("section", "product", "product__category", "ticket")
            )

        for item in items:
            for category in SERVICE_CATEGORIES:
                if kitchen_item_belongs_to_category(item, category):
                    self._items_by_category[category].append(item)

    def get_category_workflow_items(self, category):
        self._load_items()
        return self._items_by_category.get(category, [])

    def _load_order_sections(self):
        if self._order_sections is not None:
            return

        self._order_sections = set()
        if not self.order:
            return

        from riad.services.summary import iter_billable_choices

        for choice in iter_billable_choices(self.order):
            section_name = _choice_section_name(choice)
            if section_name:
                self._order_sections.add(section_name)

    def order_has_category_choices(self, category):
        if category not in self._category_has_choices:
            self._load_order_sections()
            sections = CATEGORY_SECTIONS.get(category, frozenset())
            self._category_has_choices[category] = bool(self._order_sections & sections)
        return self._category_has_choices[category]

    def get_order_flags(self):
        if self._order_flags is None:
            self._load_order_sections()
            if not self.order:
                self._order_flags = {
                    "has_drinks": False,
                    "has_starters": False,
                    "has_mains": False,
                    "has_desserts": False,
                    "has_coffee": False,
                }
            else:
                from riad.services.order_content import (
                    COFFEE_SECTIONS,
                    DESSERT_SECTIONS,
                    DRINK_SECTIONS,
                    MAIN_SECTIONS,
                    STARTER_SECTIONS,
                )

                self._order_flags = {
                    "has_drinks": bool(self._order_sections & DRINK_SECTIONS),
                    "has_starters": bool(self._order_sections & STARTER_SECTIONS),
                    "has_mains": bool(self._order_sections & MAIN_SECTIONS),
                    "has_desserts": bool(self._order_sections & DESSERT_SECTIONS),
                    "has_coffee": bool(self._order_sections & COFFEE_SECTIONS),
                }
        return self._order_flags

    def get_category_items_state(self, category):
        if category not in self._category_states:
            from riad.services.service_category_readiness import count_category_progress

            items = self.get_category_workflow_items(category)
            progress = count_category_progress(items)
            self._category_states[category] = {
                "has_items": bool(items),
                "all_done": bool(items) and all(item.is_done for item in items),
                "all_served": bool(items) and all(item.is_served for item in items),
                "ready_count": progress["ready_count"],
                "served_count": progress["served_count"],
                "preparing_count": progress["preparing_count"],
                "items": items,
            }
        return self._category_states[category]

    def is_clear_task_allowed(self):
        from riad.services.service_category_readiness import CLEARING_STATUS_TO_CATEGORY

        category = CLEARING_STATUS_TO_CATEGORY.get(self.service.status)
        if not category or not self.order:
            return False

        if not _category_has_clear_step(category):
            return False

        if not self.order_has_category_choices(category):
            return False

        expected_served_status = CATEGORY_SERVED_STATUS.get(category)
        if self.service.status != expected_served_status:
            return False

        cleared_status = CATEGORY_CLEARED_STATUS.get(category)
        if not cleared_status:
            return False

        if _status_index(self.service.status) >= _status_index(cleared_status):
            return False

        state = self.get_category_items_state(category)
        if not state["has_items"]:
            return False

        if not state["all_done"] or not state["all_served"]:
            return False

        return True

    def get_category_phase(self, category):
        if category in self._category_phases:
            return self._category_phases[category]

        if not self.order or category not in CATEGORY_SECTIONS:
            phase = PHASE_NOT_APPLICABLE
        elif not self.order_has_category_choices(category):
            phase = PHASE_NOT_APPLICABLE
        else:
            cleared_status = CATEGORY_CLEARED_STATUS.get(category)
            if cleared_status and _status_index(self.service.status) >= _status_index(cleared_status):
                phase = PHASE_CLEARED
            else:
                state = self.get_category_items_state(category)

                if not state["has_items"]:
                    phase = PHASE_WAITING_KITCHEN
                elif state["all_served"]:
                    served_status = CATEGORY_SERVED_STATUS.get(category)
                    if not served_status:
                        phase = PHASE_NOT_APPLICABLE
                    elif not _category_has_clear_step(category):
                        if _status_index(self.service.status) >= _status_index(served_status):
                            phase = PHASE_CLEARED
                        else:
                            phase = PHASE_SERVED_WAITING_CLEAR
                    elif (
                        self.service.status == served_status
                        and self.is_clear_task_allowed_for_category(category)
                    ):
                        phase = PHASE_READY_TO_CLEAR
                    elif (
                        cleared_status
                        and _status_index(self.service.status) >= _status_index(cleared_status)
                    ):
                        phase = PHASE_CLEARED
                    else:
                        phase = PHASE_SERVED_WAITING_CLEAR
                elif state["ready_count"] > 0:
                    phase = PHASE_READY_TO_SERVE
                else:
                    phase = PHASE_WAITING_KITCHEN

        self._category_phases[category] = phase
        return phase

    def is_clear_task_allowed_for_category(self, category):
        from riad.services.service_category_readiness import CLEARING_STATUS_TO_CATEGORY

        mapped = CLEARING_STATUS_TO_CATEGORY.get(self.service.status)
        if mapped != category:
            return False

        expected_served_status = CATEGORY_SERVED_STATUS.get(category)
        if self.service.status != expected_served_status:
            return False

        if not _category_has_clear_step(category):
            return False

        state = self.get_category_items_state(category)
        if not state["has_items"] or not state["all_done"] or not state["all_served"]:
            return False

        return True

    def build_category_phases(self):
        phases = {}
        if self.order:
            for category in SERVICE_CATEGORIES:
                if self.order_has_category_choices(category):
                    phases[category] = self.get_category_phase(category)
        return phases

    def get_workflow_status(self):
        if self._workflow_status is None:
            if not self.order:
                self._workflow_status = self.service.status
            elif self.service.status in CLEARING_STATUSES:
                self._workflow_status = self.service.status
            elif self.service.status not in SERVE_PRODUCT_SEQUENCE:
                self._workflow_status = self.service.status
            else:
                status = self.service.status
                flags = self.get_order_flags()
                self._load_order_sections()
                for _ in range(len(SERVE_PRODUCT_SEQUENCE)):
                    sections = WORKFLOW_PRODUCT_SECTIONS.get(status)
                    if not sections:
                        break
                    if self._order_sections & frozenset(sections):
                        break
                    next_status = None
                    try:
                        current_index = SERVE_PRODUCT_SEQUENCE.index(status)
                    except ValueError:
                        break
                    for candidate in SERVE_PRODUCT_SEQUENCE[current_index + 1:]:
                        flag_name = SERVE_PHASE_SECTION_FLAGS.get(candidate)
                        if flag_name and flags.get(flag_name):
                            next_status = candidate
                            break
                    if not next_status:
                        break
                    status = next_status
                self._workflow_status = status
        return self._workflow_status

    def category_table_action_applies(self, category):
        if not self.order or not self.order_has_category_choices(category):
            return False

        serve_phase = CATEGORY_SERVE_PHASE_STATUS[category]
        workflow_status = self.get_workflow_status()
        if _status_index(workflow_status) < _status_index(serve_phase):
            return False

        cleared_status = CATEGORY_CLEARED_STATUS.get(category)
        served_status = CATEGORY_SERVED_STATUS[category]

        if cleared_status:
            if _status_index(self.service.status) > _status_index(cleared_status):
                return False
        elif _status_index(self.service.status) > _status_index(served_status):
            return False

        return True

    def get_category_table_action(self, category):
        if not self.category_table_action_applies(category):
            return None

        phase = self.get_category_phase(category)
        if phase in (PHASE_NOT_APPLICABLE, PHASE_CLEARED):
            return None

        state = self.get_category_items_state(category)
        action = get_category_phase_display(category, phase, state)
        if action and phase == PHASE_READY_TO_CLEAR:
            served_info = build_served_since_info(category, state["items"])
            if served_info:
                action = {**action, **served_info}

        return action

    def get_active_category_table_action(self):
        if not self.order:
            return None

        for category in SERVICE_CATEGORIES:
            action = self.get_category_table_action(category)
            if action:
                return action

        return None

    def get_active_workflow_category_and_phase(self):
        if not self.order:
            return None, PHASE_NOT_APPLICABLE

        for category in SERVICE_CATEGORIES:
            if not self.category_table_action_applies(category):
                continue
            phase = self.get_category_phase(category)
            if phase not in (PHASE_NOT_APPLICABLE, PHASE_CLEARED):
                return category, phase

        return None, PHASE_NOT_APPLICABLE
