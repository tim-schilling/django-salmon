from __future__ import annotations

from collections.abc import Callable
from typing import Any

from django_observe import registry
from django_observe.decorators import observe
from django_observe.signals import observe_cache_operation


def observe_cache(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Custom decorator factory that emits the ``observe_cache_operation`` signal
    for all cache operations.

    Usage:
        @observe_cache
        def my_cache_method(self, key):
            pass
    """
    return observe(observe_cache_operation)(registry.apply_decorators("cache", func))
