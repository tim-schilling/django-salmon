"""App configuration for testapp."""

from __future__ import annotations

from django.apps import AppConfig

from django_salmon.hacks import patch


class DjangoSalmonConfig(AppConfig):
    name = "django_salmon"

    def ready(self) -> None:
        patch()
