"""URL configuration for testapp."""

from __future__ import annotations

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "cache-api-operations/", views.cache_api_operations, name="cache_api_operations"
    ),
    path(
        "cached-template-fragments/",
        views.cached_template_fragments,
        name="cached_template_fragments",
    ),
    path("cached-view/", views.cached_view, name="cached_view"),
]
