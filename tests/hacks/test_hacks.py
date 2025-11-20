from __future__ import annotations

from django.core.cache.backends.locmem import LocMemCache

from django_observe.hacks import patch as hacks_patch


class TestHacksInit:
    """Test the hacks/__init__.py patch function."""

    def test_patch_function_calls_patch_cache(self):
        """Test that patch() function calls patch_cache."""
        original_get = LocMemCache.get

        hacks_patch()

        assert LocMemCache.get is not original_get

    def test_patch_function_is_callable(self):
        """Test that patch() function is callable."""
        assert callable(hacks_patch)

    def test_patch_function_no_errors(self):
        """Test that patch() function runs without errors."""
        hacks_patch()
