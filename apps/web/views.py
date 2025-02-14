from django.conf import settings
from django.shortcuts import render


def index(request):
    return render(request, "index.html", {"REQUIRE_AUTH": settings.REQUIRE_AUTH})


def settings_view(request):
    return render(request, "settings.html", {"REQUIRE_AUTH": settings.REQUIRE_AUTH})
