from __future__ import annotations

from django.core.cache.backends.db import DatabaseCache
from django.core.cache.backends.dummy import DummyCache
from django.core.cache.backends.filebased import FileBasedCache
from django.core.cache.backends.locmem import LocMemCache
from django.core.cache.backends.memcached import PyLibMCCache, PyMemcacheCache
from django.core.cache.backends.redis import RedisCache

from django_observe.cache import observe_cache

WRAPPED_CACHE_METHODS = [
    "add",
    "get",
    "set",
    "get_or_set",
    "touch",
    "delete",
    "clear",
    "get_many",
    "set_many",
    "delete_many",
    "has_key",
    "incr",
    "decr",
    "incr_version",
    "decr_version",
]


def patch_cache() -> None:
    for cache_class in [
        DummyCache,
        PyMemcacheCache,
        PyLibMCCache,
        FileBasedCache,
        PyLibMCCache,
        DatabaseCache,
        RedisCache,
        LocMemCache,
    ]:
        for method in WRAPPED_CACHE_METHODS:
            setattr(cache_class, method, observe_cache(getattr(cache_class, method)))


# Update CacheHandler.create_connection to pass alias to backend
# Update django.core.cache.backends.base.BaseCache.__init__ to accept and store alias
