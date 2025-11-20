from __future__ import annotations

from functools import cache
from typing import Any

from django.conf import settings

CONFIG_DEFAULTS = {
    "enabled": True,
    "cache": [
        "django_observe.decorators.prevent_nested_observe",
        "django_observe.decorators.with_args",
        "django_observe.decorators.with_result",
        "django_observe.decorators.with_stacktrace",
        "django_observe.decorators.with_timing",
    ],
}


@cache
def get_config() -> dict[str, Any]:
    USER_CONFIG = getattr(settings, "OBSERVING", {})
    CONFIG = CONFIG_DEFAULTS.copy()
    CONFIG.update(USER_CONFIG)
    return CONFIG
