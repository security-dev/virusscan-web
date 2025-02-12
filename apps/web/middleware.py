import re

from django.conf import settings
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.shortcuts import redirect
from django.urls import NoReverseMatch, resolve, reverse

IGNORE_PATHS = [re.compile(settings.LOGIN_URL)]

IGNORE_PATHS += [
    re.compile(url) for url in getattr(settings, "LOGIN_REQUIRED_IGNORE_PATHS", [])
]

IGNORE_VIEW_NAMES = [
    name for name in getattr(settings, "LOGIN_REQUIRED_IGNORE_VIEW_NAMES", [])
]


class LoginRequiredMiddleware(AuthenticationMiddleware):
    """
    If REQUIRE_AUTH is True, redirect all non-authenticated users to the login page.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path

        # let django-ninja handle the authentication for the API
        if (
            path.startswith(f"/{settings.API_PREFIX}/")
            or getattr(view_func, "__module__", "") == "ninja.operation"
        ):
            return

        if not settings.REQUIRE_AUTH or request.user.is_authenticated:
            return

        resolver = resolve(path)
        view_found = (True for name in IGNORE_VIEW_NAMES if name == resolver.view_name)

        path = path.split("?next=")[0]

        if not any(view_found) and not any(
            re.search(url, path) for url in IGNORE_PATHS
        ):
            try:
                login_url = reverse(settings.LOGIN_URL)
            except NoReverseMatch:
                login_url = settings.LOGIN_URL
            return redirect(f"{login_url}?next={path}")
