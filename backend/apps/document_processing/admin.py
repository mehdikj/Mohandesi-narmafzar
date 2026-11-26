
from django.contrib import admin
from .models import OCRJob


@admin.register(OCRJob)
class OCRJobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "resource_file",
        "status",
        "language",
        "created_by",
        "created_at",
        "completed_at",
    )

    list_filter = (
        "status",
        "language",
        "created_at",
    )

    search_fields = (
        "resource_file__resource__title",
        "extracted_text",
        "error_message",
        "created_by__username",
    )

    readonly_fields = (
        "created_at",
        "started_at",
        "completed_at",
    )
