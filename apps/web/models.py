from django.contrib.auth.models import AbstractUser
from django.db import transaction


class CustomUser(AbstractUser):
    def create_api_key(self, label: str) -> str:
        from ninja_apikey.models import APIKey
        from ninja_apikey.security import generate_key

        with transaction.atomic():
            obj = APIKey.objects.filter(user=self, label=label).first()
            if obj:
                raise ValueError("API key already exists with this label.")
            key = generate_key()
            APIKey.objects.create(
                user=self, label=label, prefix=key.prefix, hashed_key=key.hashed_key
            )

            return f"{key.prefix}.{key.key}"
