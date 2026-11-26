
from django.conf import settings
from django.db import models


class OCRJob(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    resource_file = models.ForeignKey(
        "resources.ResourceFile",
        on_delete=models.CASCADE,
        related_name="ocr_jobs"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    language = models.CharField(
        max_length=20,
        default="fas+eng"
    )

    extracted_text = models.TextField(blank=True)

    error_message = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ocr_jobs"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    started_at = models.DateTimeField(null=True, blank=True)

    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"OCR Job {self.id} - {self.status}"
