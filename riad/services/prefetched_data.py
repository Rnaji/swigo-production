"""
Helpers de lecture des attributs Prefetch(to_attr=...).

Module indépendant : n'importe aucun autre service métier.
Ne déclenche jamais de requête SQL.
"""

from django.conf import settings


class PrefetchMissingError(RuntimeError):
    """Attribut to_attr attendu absent — le chemin lecture n'a pas préchargé les données."""


def _log_missing(attr, obj):
    label = type(obj).__name__ if obj is not None else "None"
    object_id = getattr(obj, "pk", None) or getattr(obj, "id", None)
    message = f"PREFETCH MISSING attr={attr} object={label} id={object_id}"
    if settings.DEBUG:
        print(message)
    return message


def get_prefetched_guests(order):
    if order is None:
        return []
    if hasattr(order, "prefetched_guests"):
        return order.prefetched_guests
    raise PrefetchMissingError(_log_missing("prefetched_guests", order))


def get_prefetched_guest_choices(guest):
    if guest is None:
        return []
    if hasattr(guest, "prefetched_choices"):
        return guest.prefetched_choices
    raise PrefetchMissingError(_log_missing("prefetched_choices", guest))


def get_prefetched_table_extras(order):
    if order is None:
        return []
    if hasattr(order, "prefetched_table_extras"):
        return order.prefetched_table_extras
    raise PrefetchMissingError(_log_missing("prefetched_table_extras", order))


def get_prefetched_payments(order):
    if order is None:
        return []
    if hasattr(order, "prefetched_payments"):
        return order.prefetched_payments
    raise PrefetchMissingError(_log_missing("prefetched_payments", order))


def get_prefetched_workflow_items(order):
    if order is None:
        return None
    if hasattr(order, "prefetched_workflow_items"):
        return order.prefetched_workflow_items
    raise PrefetchMissingError(_log_missing("prefetched_workflow_items", order))
