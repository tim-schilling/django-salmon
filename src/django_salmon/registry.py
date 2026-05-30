from __future__ import annotations

from collections.abc import Callable
from typing import Any

from django.utils.module_loading import import_string

from django_salmon.config import get_config


class ObserveRegistry:
    def __init__(self) -> None:
        self._decorators: dict[str, list[Callable[..., Any]]] = {}

    def register(self, component: str, decorator: Callable[..., Any]) -> None:
        self._decorators.setdefault(component, []).append(decorator)

    def get_decorators(self, component: str) -> list[Callable[..., Any]]:
        """Get all decorators for a component (from settings + registry)."""
        decorators: list[Callable[..., Any]] = []

        paths = get_config().get(component, [])
        if isinstance(paths, list):
            for path in paths:
                decorators.append(import_string(path))

        decorators.extend(self._decorators.get(component, []))

        return decorators

    def apply_decorators(
        self, component: str, func: Callable[..., Any]
    ) -> Callable[..., Any]:
        decorators = self.get_decorators(component)
        # The registry_wrapped_index needs to be the index of the decorator
        # being applied which is the reverse of what's defined in the settings.
        count = len(decorators) - 1
        for decorator_index, decorator in enumerate(decorators):
            func = decorator(func, registry_wrapped_index=count - decorator_index)
        return func


registry = ObserveRegistry()
