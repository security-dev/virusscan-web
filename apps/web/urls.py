from django.urls import path

from .views import index, settings_view

urlpatterns = [
    path("", index, name="index"),
    path("settings", settings_view, name="settings"),
]
