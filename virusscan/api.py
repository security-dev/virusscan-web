from django.conf import settings
from django.http import HttpRequest
from ninja import NinjaAPI
from ninja.security import django_auth
from ninja.security.base import AuthBase
from ninja_apikey.security import APIKeyAuth


class DynamicAuth(AuthBase):
    openapi_type: str = "apiKey"
    openapi_in: list = ["cookie", "header"]

    def __call__(self, request: HttpRequest):
        if not settings.REQUIRE_AUTH:
            return True

        # Try API key auth
        api_key_auth = APIKeyAuth()
        result = api_key_auth(request)
        if result:
            return result

        # Try Django auth
        result = django_auth(request)
        if result:
            return result

        return None


api = NinjaAPI(auth=DynamicAuth())

api.add_router("/scans/", "apps.scans.api.router")
