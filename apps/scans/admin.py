from django.contrib import admin

from .models import Scan


@admin.register(Scan)
class ScanAdmin(admin.ModelAdmin):
    list_display = ("filename", "status", "sha256", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("filename", "sha256", "sha512")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        ("Basic Information", {"fields": ("id", "filename", "status")}),
        ("Hash Information", {"fields": ("sha256", "sha512")}),
        ("Results", {"fields": ("result",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
