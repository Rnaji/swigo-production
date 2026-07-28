"""
Point d'entrée unique pour la phase courante du workflow service.

Tous les écrans consommateurs (Salle, Tâches, timeline) doivent s'appuyer
sur get_service_workflow_snapshot() ou get_category_phase() — jamais recalculer
un workflow parallèle à partir du seul service.status.

Les transitions normales de statut après mutation des lignes passent par
advance_service_status_from_line_state(). Les réparations exceptionnelles
passent par repair_workflow_inconsistencies().
"""

import logging
import time

from django.conf import settings

from riad.services.service_category_readiness import (
    CATEGORY_CLEARED_STATUS,
    CATEGORY_SERVE_PHASE_STATUS,
    CATEGORY_SERVED_STATUS,
    PHASE_CLEARED,
    PHASE_NOT_APPLICABLE,
    PHASE_READY_TO_CLEAR,
    PHASE_READY_TO_SERVE,
    PHASE_SERVED_WAITING_CLEAR,
    PHASE_WAITING_KITCHEN,
    SERVICE_CATEGORIES,
    SERVICE_STEPS,
    _category_has_clear_step,
    get_category_items_state,
    get_category_phase,
    is_clear_task_allowed,
    order_has_category_choices,
    reconcile_clearing_service_status,
    reconcile_served_category_status,
)
from riad.services.workflow_context import WorkflowReadContext

logger = logging.getLogger(__name__)

STAGE_TO_CATEGORY = {
    "drinks": "drinks",
    "starters": "starters",
    "mains": "mains",
    "desserts": "desserts",
    "coffee": "coffee",
}

PHASE_TO_TIMELINE_STATE = {
    PHASE_WAITING_KITCHEN: "active",
    PHASE_READY_TO_SERVE: "active",
    PHASE_SERVED_WAITING_CLEAR: "waiting_clear",
    PHASE_READY_TO_CLEAR: "waiting_clear",
    PHASE_CLEARED: "completed",
}

_inconsistency_log_cache = {}
_INCONSISTENCY_LOG_TTL_SECONDS = 60


def _status_index(status):
    try:
        return SERVICE_STEPS.index(status)
    except ValueError:
        return -1


def _log_workflow_transition(*, service, category, old_status, new_status, source):
    message = (
        f"WORKFLOW TRANSITION service={service.id} category={category} "
        f"old_status={old_status} new_status={new_status} source={source}"
    )
    if settings.DEBUG:
        print(message)
    logger.info(message)


def _log_workflow_repair(*, service, old_status, new_status, reason, source):
    message = (
        f"WORKFLOW REPAIR service={service.id} old_status={old_status} "
        f"new_status={new_status} reason={reason} source={source}"
    )
    if settings.DEBUG:
        print(message)
    logger.warning(message)


def _resolve_context(service, order, ctx=None, *, prefetched_items=None):
    if ctx is not None:
        return ctx
    return WorkflowReadContext(service, order, prefetched_items=prefetched_items)


def get_active_workflow_category_and_phase(service, order, *, ctx=None):
    """
    Première catégorie métier pertinente et sa phase courante,
    dérivées uniquement de l'état des lignes + service.status.
    """
    context = _resolve_context(service, order, ctx)
    return context.get_active_workflow_category_and_phase()


def detect_workflow_inconsistencies(service, order, *, ctx=None):
    if not order:
        return []

    context = _resolve_context(service, order, ctx)
    issues = []

    for category in SERVICE_CATEGORIES:
        if not context.order_has_category_choices(category):
            continue

        state = context.get_category_items_state(category)
        served_status = CATEGORY_SERVED_STATUS.get(category)
        cleared_status = CATEGORY_CLEARED_STATUS.get(category)
        phase = context.get_category_phase(category)

        if served_status and service.status == served_status:
            if state["has_items"] and not state["all_served"]:
                issues.append(
                    f"{category}: status={served_status} but not all items served"
                )

        if cleared_status and service.status == cleared_status:
            if state["has_items"] and not state["all_served"]:
                issues.append(
                    f"{category}: status={cleared_status} but not all items served"
                )

        if state["all_served"] and served_status:
            if _status_index(service.status) < _status_index(served_status):
                issues.append(
                    f"{category}: all items served but status={service.status} "
                    f"< {served_status}"
                )

        if cleared_status and _status_index(service.status) >= _status_index(cleared_status):
            if state["has_items"] and not state["all_served"]:
                issues.append(
                    f"{category}: status={cleared_status} but items not all served"
                )

        for item in state["items"]:
            if item.is_served and not item.is_done:
                issues.append(
                    f"{category}: item {item.id} is_served=True but is_done=False"
                )

        if phase == PHASE_READY_TO_SERVE and state["all_served"]:
            issues.append(f"{category}: serve phase but all items already served")

        if phase == PHASE_READY_TO_CLEAR and not state["all_served"]:
            issues.append(f"{category}: clear phase but items not all served")

        serve_phase = CATEGORY_SERVE_PHASE_STATUS.get(category)
        if (
            serve_phase
            and _status_index(service.status) >= _status_index(served_status or serve_phase)
            and state["has_items"]
            and not state["all_done"]
            and phase not in (PHASE_NOT_APPLICABLE, PHASE_CLEARED)
        ):
            issues.append(
                f"{category}: status past serve phase but kitchen items not all done"
            )

    return issues


def log_workflow_inconsistencies(service, order, *, context="read", ctx=None):
    issues = detect_workflow_inconsistencies(service, order, ctx=ctx)
    if not issues:
        return issues

    if not settings.DEBUG:
        return issues

    details = "; ".join(issues)
    cache_key = (service.id, service.status, details)
    now = time.monotonic()
    last_logged = _inconsistency_log_cache.get(cache_key)
    if last_logged and (now - last_logged) < _INCONSISTENCY_LOG_TTL_SECONDS:
        return issues

    _inconsistency_log_cache[cache_key] = now
    message = (
        f"WORKFLOW INCONSISTENCY service={service.id} status={service.status} "
        f"details={details} context={context}"
    )
    print(message)
    logger.warning(message)
    return issues


def get_service_workflow_snapshot(
    service,
    order,
    *,
    context="read",
    ctx=None,
    prefetched_items=None,
):
    """
    Snapshot lecture seule — source de vérité partagée Salle / Tâches / timeline.
    Un seul WorkflowReadContext par appel : pas de requêtes par catégorie.
    """
    read_ctx = _resolve_context(service, order, ctx, prefetched_items=prefetched_items)
    inconsistencies = log_workflow_inconsistencies(
        service,
        order,
        context=context,
        ctx=read_ctx,
    )
    active_category, phase = read_ctx.get_active_workflow_category_and_phase()
    category_phases = read_ctx.build_category_phases()

    return {
        "active_category": active_category,
        "phase": phase,
        "category_phases": category_phases,
        "table_action": read_ctx.get_active_category_table_action(),
        "should_show_serve_task": {
            category: category_phases.get(category) == PHASE_READY_TO_SERVE
            for category in category_phases
        },
        "is_clear_task_allowed": read_ctx.is_clear_task_allowed() if order else False,
        "inconsistencies": inconsistencies,
        "_ctx": read_ctx,
    }


def get_timeline_stage_state(
    stage_key,
    service,
    order,
    *,
    workflow_snapshot=None,
    ctx=None,
):
    """
    État visuel timeline dérivé du snapshot workflow déjà calculé.
    """
    read_ctx = None
    category_phases = {}
    active_category = None

    if workflow_snapshot:
        read_ctx = workflow_snapshot.get("_ctx")
        category_phases = workflow_snapshot.get("category_phases", {})
        active_category = workflow_snapshot.get("active_category")
    elif ctx is not None:
        read_ctx = ctx
        category_phases = ctx.build_category_phases()
        active_category, _ = ctx.get_active_workflow_category_and_phase()

    category = STAGE_TO_CATEGORY.get(stage_key)
    if category:
        if read_ctx:
            if not order or not read_ctx.order_has_category_choices(category):
                return "pending"

            state = read_ctx.get_category_items_state(category)
        else:
            if not order or not order_has_category_choices(order, category):
                return "pending"

            state = get_category_items_state(service, order, category)

        served_status = CATEGORY_SERVED_STATUS.get(category)
        cleared_status = CATEGORY_CLEARED_STATUS.get(category)

        if not state["has_items"]:
            status_idx = _status_index(service.status)
            if cleared_status and status_idx >= _status_index(cleared_status):
                return "completed"
            if served_status and service.status == served_status:
                if not _category_has_clear_step(category):
                    return "completed"
                return "waiting_clear"
            if served_status and status_idx >= _status_index(served_status):
                return "completed"
            serve_phase = CATEGORY_SERVE_PHASE_STATUS.get(category)
            if serve_phase and status_idx >= _status_index(serve_phase):
                if active_category is None and read_ctx:
                    active_category, _ = read_ctx.get_active_workflow_category_and_phase()
                elif active_category is None:
                    active_category, _ = get_active_workflow_category_and_phase(service, order)
                return "active" if active_category == category else "pending"
            return "pending"

        if read_ctx:
            phase = category_phases.get(category) or read_ctx.get_category_phase(category)
        else:
            phase = get_category_phase(service, order, category)

        if phase == PHASE_NOT_APPLICABLE:
            return "pending"

        mapped = PHASE_TO_TIMELINE_STATE.get(phase)
        if phase in (PHASE_WAITING_KITCHEN, PHASE_READY_TO_SERVE):
            if active_category is None:
                if read_ctx:
                    active_category, _ = read_ctx.get_active_workflow_category_and_phase()
                else:
                    active_category, _ = get_active_workflow_category_and_phase(service, order)
            return "active" if active_category == category else "pending"

        return mapped or "pending"

    if stage_key == "installed":
        if _status_index(service.status) >= _status_index("ordering"):
            return "completed"
        return "active" if service.status == "installed" else "pending"

    if stage_key == "ordered":
        if _status_index(service.status) >= _status_index("ordered"):
            return "completed"
        return "active" if service.status in ("installed", "ordering") else "pending"

    if stage_key == "payment":
        if service.status == "paid":
            return "completed"
        if service.status == "bill_requested":
            return "active"
        return "pending"

    return "pending"


def advance_service_status_from_line_state(service, order, *, source="write"):
    """
    Transition normale : avance service.status vers *_served lorsque les lignes
    de la catégorie sont entièrement servies.
    """
    if not order:
        return False

    changed = False

    for category in SERVICE_CATEGORIES:
        if not order_has_category_choices(order, category):
            continue

        old_status = service.status
        if not reconcile_served_category_status(service, order, category):
            continue

        changed = True
        _log_workflow_transition(
            service=service,
            category=category,
            old_status=old_status,
            new_status=service.status,
            source=source,
        )

    if changed:
        service.refresh_from_db()

    return changed


def repair_workflow_inconsistencies(service, order, *, source="repair"):
    """
    Réparation exceptionnelle : corrige un statut de débarrassage avancé trop tôt,
    ou rattrape un statut *_served manquant lorsque les lignes sont déjà servies.
    """
    if not order:
        return False

    changed = False

    old_status = service.status
    if reconcile_clearing_service_status(service, order):
        changed = True
        _log_workflow_repair(
            service=service,
            old_status=old_status,
            new_status=service.status,
            reason="premature_clearing_status",
            source=source,
        )

    for category in SERVICE_CATEGORIES:
        if not order_has_category_choices(order, category):
            continue

        old_status = service.status
        if not reconcile_served_category_status(service, order, category):
            continue

        changed = True
        _log_workflow_repair(
            service=service,
            old_status=old_status,
            new_status=service.status,
            reason=f"lagging_served_status_for_{category}",
            source=source,
        )

    if changed:
        service.refresh_from_db()

    return changed
