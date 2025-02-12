from django.conf import settings
from ninja import NinjaAPI

if settings.REQUIRE_AUTH:
    from ninja.security import django_auth
    from ninja_apikey.security import APIKeyAuth

    api = NinjaAPI(auth=[django_auth, APIKeyAuth()], csrf=True)
else:
    api = NinjaAPI()

api.add_router("/scans/", "apps.scans.api.router")
