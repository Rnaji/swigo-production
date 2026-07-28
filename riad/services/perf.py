"""
Instrumentation temporaire des endpoints (DEBUG uniquement).
"""

import functools
import time

from django.conf import settings
from django.db import connection, reset_queries


def log_endpoint_perf(endpoint_name):
    """Log PERF endpoint=… duration_ms=… queries=… payload_bytes=… en DEBUG."""

    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            if not settings.DEBUG:
                return view_func(*args, **kwargs)

            reset_queries()
            started = time.perf_counter()
            response = view_func(*args, **kwargs)
            duration_ms = (time.perf_counter() - started) * 1000
            queries = len(connection.queries)
            payload_bytes = (
                len(response.content)
                if hasattr(response, "content") and response.content is not None
                else 0
            )
            print(
                f"PERF endpoint={endpoint_name} duration_ms={duration_ms:.1f} "
                f"queries={queries} payload_bytes={payload_bytes}"
            )
            return response

        return wrapper

    return decorator


def measure_call(label):
    """Context manager : PERF call=… duration_ms=… queries=…"""

    class _MeasureCall:
        def __init__(self, name):
            self.name = name
            self.started = None
            self.query_start = None

        def __enter__(self):
            if settings.DEBUG:
                reset_queries()
                self.query_start = 0
                self.started = time.perf_counter()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if settings.DEBUG and self.started is not None:
                duration_ms = (time.perf_counter() - self.started) * 1000
                queries = len(connection.queries)
                print(
                    f"PERF call={self.name} duration_ms={duration_ms:.1f} queries={queries}"
                )
            return False

    return _MeasureCall(label)
