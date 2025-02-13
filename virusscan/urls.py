from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from .api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.web.urls")),
    path(f"{settings.API_PREFIX}/", api.urls),
    path("accounts/", include("django.contrib.auth.urls")),
]
