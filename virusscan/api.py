from typing import Any, Optional

from django.conf import settings
from django.http import HttpRequest
from ninja import NinjaAPI
from ninja.security import SessionAuth
from ninja.security.base import AuthBase
from ninja_apikey.security import APIKeyAuth

from apps.scans.api import router as scans_router
from apps.web.api import router as web_router


class DynamicAuth(AuthBase):
    openapi_type: str = "apiKey"
    openapi_in: list = ["cookie", "header"]

    api_key_auth = APIKeyAuth()
    django_auth = SessionAuth()

    def __call__(self, request: HttpRequest) -> Optional[Any]:
        if not settings.REQUIRE_AUTH:
            return True

        result = self.api_key_auth(request)
        if result:
            return result

        result = self.django_auth(request)
        if result:
            return result

        return None


api = NinjaAPI(auth=DynamicAuth())

api.add_router("/scans/", scans_router)
api.add_router("/user/api_keys/", web_router)
