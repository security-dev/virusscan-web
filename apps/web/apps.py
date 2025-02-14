import string

from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.utils.crypto import get_random_string


def create_default_superuser(sender, **kwargs):  # noqa
    User = get_user_model()
    if User.objects.count() != 0:
        return
    password = get_random_string(
        length=12, allowed_chars=f"{string.ascii_letters}{string.digits}"
    )
    u = User.objects.create_superuser(  # noqa
        username="admin",
        password=password,
    )

    print("\n\033[93m!!! ADMIN CREDENTIALS !!!\033[0m")
    print("\033[92m╔═════════════════════════╗")
    print("║ Username: admin         ║")
    print(f"║ Password: {password}  ║")
    print("╚═════════════════════════╝\033[0m")


class WebConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.web"
    label = "web"

    def ready(self):
        post_migrate.connect(create_default_superuser, sender=self)
