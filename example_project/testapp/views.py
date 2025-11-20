"""Views for testapp."""

from __future__ import annotations

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


def cache_api_operations(request: HttpRequest) -> HttpResponse:
    if not cache.get("key"):
        cache.set("key", "value")
    return render(request, "cache/cache_api_operations.html")


def cached_template_fragments(request: HttpRequest) -> HttpResponse:
    return render(request, "cache/cached_template_fragments.html")


@cache_page(5, key_prefix="cached_view")
def cached_view(request: HttpRequest) -> HttpResponse:
    return render(request, "cache/cached_view.html")
