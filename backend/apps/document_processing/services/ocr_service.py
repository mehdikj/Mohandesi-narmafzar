
import logging
from pathlib import Path

import pymupdf
import pytesseract
from django.utils import timezone
from PIL import Image

from apps.resources.models import ResourceFile
from apps.document_processing.models import OCRJob


logger = logging.getLogger(__name__)


class OCRProcessingError(Exception):
    pass


def extract_pdf_text(file_path, language="fas+eng", dpi=200):
    file_path = Path(file_path)

    if not file_path.exists() or not file_path.is_file():
        raise OCRProcessingError("PDF file does not exist.")

    if file_path.suffix.lower() != ".pdf":
        raise OCRProcessingError("OCR currently supports PDF files only.")

    extracted_pages = []

    try:
        with pymupdf.open(file_path) as document:
            if document.is_encrypted:
                raise OCRProcessingError(
                    "Encrypted PDF files are not supported."
                )

            for page_number, page in enumerate(document, start=1):
                text = page.get_text("text").strip()

                if len(text) < 30:
                    pixmap = page.get_pixmap(
                        dpi=dpi,
                        colorspace=pymupdf.csRGB,
                        alpha=False,
                    )

                    image = Image.frombytes(
                        "RGB",
                        (pixmap.width, pixmap.height),
                        pixmap.samples,
                    )

                    text = pytesseract.image_to_string(
                        image,
                        lang=language,
                        config="--psm 3",
                    ).strip()

                if text:
                    extracted_pages.append(
                        f"--- Page {page_number} ---\n{text}"
                    )

    except OCRProcessingError:
        raise
    except Exception as exc:
        raise OCRProcessingError(
            f"PDF processing failed: {exc}"
        ) from exc

    return "\n\n".join(extracted_pages)


def process_ocr_job(job):
    job.status = OCRJob.Status.PROCESSING
    job.started_at = timezone.now()
    job.completed_at = None
    job.error_message = ""
    job.extracted_text = ""
    job.save(
        update_fields=[
            "status",
            "started_at",
            "completed_at",
            "error_message",
            "extracted_text",
        ]
    )

    try:
        resource_file = job.resource_file

        if resource_file.file_type != ResourceFile.FileType.PDF:
            raise OCRProcessingError(
                "OCR processing is available for PDF files only."
            )

        if not resource_file.file:
            raise OCRProcessingError("No file is attached to this resource.")

        extracted_text = extract_pdf_text(
            resource_file.file.path,
            language=job.language,
        )

        if not extracted_text.strip():
            raise OCRProcessingError(
                "No readable text could be extracted from this PDF."
            )

        job.extracted_text = extracted_text
        job.status = OCRJob.Status.COMPLETED
        job.completed_at = timezone.now()
        job.error_message = ""

        job.save(
            update_fields=[
                "extracted_text",
                "status",
                "completed_at",
                "error_message",
            ]
        )

    except Exception as exc:
        logger.exception("OCR processing failed for job %s", job.pk)

        job.status = OCRJob.Status.FAILED
        job.error_message = str(exc)
        job.completed_at = timezone.now()

        job.save(
            update_fields=[
                "status",
                "error_message",
                "completed_at",
            ]
        )

    return job
