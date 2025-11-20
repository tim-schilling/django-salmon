"""App configuration for testapp."""

from __future__ import annotations

from django.apps import AppConfig


class TestappConfig(AppConfig):
    """Configuration for testapp."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "testapp"

    def ready(self) -> None:
        from testapp.receivers import connect_signals

        connect_signals()
