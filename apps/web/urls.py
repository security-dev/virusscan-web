from django.urls import path

from .views import index, settings

urlpatterns = [
    path("", index, name="index"),
    path("settings", settings, name="settings"),
]
