from __future__ import annotations

from functools import cache
from typing import Any

from django.conf import settings

CONFIG_DEFAULTS = {
    "enabled": True,
    "cache": [
        "django_salmon.decorators.prevent_nested_observe",
        "django_salmon.decorators.with_args",
        "django_salmon.decorators.with_result",
        "django_salmon.decorators.with_stacktrace",
        "django_salmon.decorators.with_timing",
    ],
}


@cache
def get_config() -> dict[str, Any]:
    USER_CONFIG = getattr(settings, "OBSERVING", {})
    CONFIG = CONFIG_DEFAULTS.copy()
    CONFIG.update(USER_CONFIG)
    return CONFIG
