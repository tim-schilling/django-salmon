from __future__ import annotations


def patch() -> None:
    from django_observe.hacks.cache import patch_cache

    patch_cache()
