from django.conf import settings
from ninja import NinjaAPI

if settings.REQUIRE_AUTH:
    from ninja.security import django_auth

    api = NinjaAPI(auth=django_auth, csrf=True)
else:
    api = NinjaAPI()

api.add_router("/scans/", "apps.scans.api.router")
