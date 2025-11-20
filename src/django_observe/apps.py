"""App configuration for testapp."""

from __future__ import annotations

from django.apps import AppConfig

from django_observe.hacks import patch


class DjangoObserveConfig(AppConfig):
    """Configuration for django_observe."""

    name = "django_observe"

    def ready(self) -> None:
        patch()
