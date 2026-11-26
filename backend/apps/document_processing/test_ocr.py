import tempfile
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.document_processing.models import OCRJob
from apps.document_processing.services.ocr_service import (
    OCRProcessingError,
    process_ocr_job,
)
from apps.identity.models import User
from apps.resources.models import Resource, ResourceFile


class OCRJobTests(TestCase):

    def setUp(self):
        self.temp_media = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_media.cleanup)

        self.media_settings = override_settings(
            MEDIA_ROOT=self.temp_media.name
        )
        self.media_settings.enable()
        self.addCleanup(self.media_settings.disable)

        self.client = APIClient()

        self.user = User.objects.create_user(
            username="ocr_test_user",
            password="TestPassword123",
            role=User.Role.USER,
        )

        self.librarian = User.objects.create_user(
            username="ocr_librarian",
            password="TestPassword123",
            role=User.Role.LIBRARIAN,
        )

        self.admin = User.objects.create_user(
            username="ocr_admin",
            password="TestPassword123",
            role=User.Role.ADMIN,
        )

        self.resource = Resource.objects.create(
            title="OCR Test Resource",
            created_by=self.librarian,
        )

    def create_resource_file(
        self,
        file_type="PDF",
        filename="sample.pdf",
        is_active=True,
    ):
        uploaded_file = SimpleUploadedFile(
            filename,
            b"Test file content",
            content_type="application/pdf",
        )

        return ResourceFile.objects.create(
            resource=self.resource,
            file=uploaded_file,
            file_type=file_type,
            size_bytes=uploaded_file.size,
            sha256="a" * 64,
            version=1,
            is_active=is_active,
        )

    def test_successful_ocr_processing(self):
        resource_file = self.create_resource_file()

        job = OCRJob.objects.create(
            resource_file=resource_file,
            created_by=self.user,
        )

        expected_text = "This is extracted text from the PDF document."

        with patch(
            "apps.document_processing.services.ocr_service.extract_pdf_text",
            return_value=expected_text,
        ):
            result = process_ocr_job(job)

        result.refresh_from_db()

        self.assertEqual(result.status, OCRJob.Status.COMPLETED)
        self.assertEqual(result.extracted_text, expected_text)
        self.assertEqual(result.error_message, "")
        self.assertIsNotNone(result.started_at)
        self.assertIsNotNone(result.completed_at)

    def test_epub_file_is_rejected(self):
        resource_file = self.create_resource_file(
            file_type="EPUB",
            filename="sample.epub",
        )

        job = OCRJob.objects.create(
            resource_file=resource_file,
            created_by=self.user,
        )

        result = process_ocr_job(job)
        result.refresh_from_db()

        self.assertEqual(result.status, OCRJob.Status.FAILED)
        self.assertIn("PDF files only", result.error_message)
        self.assertIsNotNone(result.completed_at)

    def test_ocr_processing_error_is_saved(self):
        resource_file = self.create_resource_file()

        job = OCRJob.objects.create(
            resource_file=resource_file,
            created_by=self.user,
        )

        with patch(
            "apps.document_processing.services.ocr_service.extract_pdf_text",
            side_effect=OCRProcessingError("Test OCR failure"),
        ):
            result = process_ocr_job(job)

        result.refresh_from_db()

        self.assertEqual(result.status, OCRJob.Status.FAILED)
        self.assertEqual(result.error_message, "Test OCR failure")
        self.assertIsNotNone(result.started_at)
        self.assertIsNotNone(result.completed_at)

    def test_librarian_can_create_ocr_job(self):
        resource_file = self.create_resource_file()

        self.client.force_authenticate(user=self.librarian)

        response = self.client.post(
            f"/api/v1/resources/{resource_file.id}/ocr/",
            {"language": "fas+eng"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        job = OCRJob.objects.get(id=response.data["id"])

        self.assertEqual(job.status, OCRJob.Status.PENDING)
        self.assertEqual(job.resource_file, resource_file)
        self.assertEqual(job.created_by, self.librarian)
        self.assertEqual(job.language, "fas+eng")

    def test_admin_can_create_ocr_job(self):
        resource_file = self.create_resource_file()

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f"/api/v1/resources/{resource_file.id}/ocr/",
            {"language": "eng"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        job = OCRJob.objects.get(id=response.data["id"])

        self.assertEqual(job.created_by, self.admin)
        self.assertEqual(job.status, OCRJob.Status.PENDING)

    def test_regular_user_cannot_create_ocr_job(self):
        resource_file = self.create_resource_file()

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f"/api/v1/resources/{resource_file.id}/ocr/",
            {"language": "fas+eng"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(OCRJob.objects.count(), 0)

    def test_anonymous_user_cannot_create_ocr_job(self):
        resource_file = self.create_resource_file()

        response = self.client.post(
            f"/api/v1/resources/{resource_file.id}/ocr/",
            {"language": "fas+eng"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(OCRJob.objects.count(), 0)

    def test_epub_cannot_create_ocr_job(self):
        resource_file = self.create_resource_file(
            file_type="EPUB",
            filename="sample.epub",
        )

        self.client.force_authenticate(user=self.librarian)

        response = self.client.post(
            f"/api/v1/resources/{resource_file.id}/ocr/",
            {"language": "fas+eng"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(OCRJob.objects.count(), 0)

    def test_inactive_pdf_cannot_create_ocr_job(self):
        resource_file = self.create_resource_file(
            is_active=False,
        )

        self.client.force_authenticate(user=self.librarian)

        response = self.client.post(
            f"/api/v1/resources/{resource_file.id}/ocr/",
            {"language": "fas+eng"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(OCRJob.objects.count(), 0)

    def test_librarian_can_view_ocr_job(self):
        resource_file = self.create_resource_file()

        job = OCRJob.objects.create(
            resource_file=resource_file,
            created_by=self.librarian,
            extracted_text="متن استخراج شده",
        )

        self.client.force_authenticate(user=self.librarian)

        response = self.client.get(
            f"/api/v1/ocr/{job.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], job.id)
        self.assertEqual(
            response.data["extracted_text"],
            "متن استخراج شده",
        )

    def test_regular_user_cannot_view_ocr_job(self):
        resource_file = self.create_resource_file()

        job = OCRJob.objects.create(
            resource_file=resource_file,
            created_by=self.librarian,
            extracted_text="Private OCR result",
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f"/api/v1/ocr/{job.id}/"
        )

        self.assertEqual(response.status_code, 403)