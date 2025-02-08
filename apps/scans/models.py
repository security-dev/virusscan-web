import uuid

from django.db import models


class Scan(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SCANNING = "scanning", "Scanning"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CLEAN = "clean", "Clean"
        FOUND = "found", "Found"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=1024)
    sha256 = models.CharField(max_length=64)
    sha512 = models.CharField(max_length=128)
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.PENDING,
    )
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.filename} ({self.sha256})"
