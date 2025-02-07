from ninja import NinjaAPI

api = NinjaAPI()

api.add_router("/scans/", "apps.scans.api.router")
