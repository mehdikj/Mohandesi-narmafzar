import io, pytest
from rest_framework.test import APIClient
from apps.identity.models import User
from apps.resources.models import Resource
from types import SimpleNamespace

from rest_framework.exceptions import ValidationError

from apps.resources.validators import (
    MAX_RESOURCE_FILE_SIZE,
    validate_resource_file,
)
@pytest.mark.django_db
def test_register_and_login():
    c=APIClient(); r=c.post("/api/v1/auth/register/",{"username":"aria","password":"strong-pass-123"},format="json"); assert r.status_code==201
    r=c.post("/api/v1/auth/login/",{"username":"aria","password":"strong-pass-123"},format="json"); assert r.status_code==200 and "access" in r.data
@pytest.mark.django_db
def test_guest_only_gets_public_published():
    u=User.objects.create_user(username="lib",password="strong-pass-123",role=User.Role.LIBRARIAN)
    Resource.objects.create(title="Public",status="PUBLISHED",access_policy="PUBLIC",created_by=u)
    Resource.objects.create(title="Draft",status="DRAFT",access_policy="PUBLIC",created_by=u)
    Resource.objects.create(title="Private",status="PUBLISHED",access_policy="REGISTERED_ONLY",created_by=u)
    r=APIClient().get("/api/v1/resources/"); assert r.status_code==200 and [x["title"] for x in r.data]==["Public"]
@pytest.mark.django_db
def test_librarian_can_register_pdf():
    u=User.objects.create_user(username="lib2",password="strong-pass-123",role=User.Role.LIBRARIAN); c=APIClient(); c.force_authenticate(u)
    f=io.BytesIO(b"%PDF-1.7\nminimal"); f.name="book.pdf"
    r=c.post("/api/v1/resources/",{"title":"Book","file":f},format="multipart"); assert r.status_code==201
@pytest.mark.django_db
def test_public_file_download_requires_published_resource():
    librarian = User.objects.create_user(
        username="download_librarian",
        password="strong-pass-123",
        role=User.Role.LIBRARIAN,
    )

    librarian_client = APIClient()
    librarian_client.force_authenticate(librarian)

    pdf_file = io.BytesIO(b"%PDF-1.7\nminimal test pdf")
    pdf_file.name = "download-test.pdf"

    response = librarian_client.post(
        "/api/v1/resources/",
        {
            "title": "Download Test Book",
            "file": pdf_file,
        },
        format="multipart",
    )

    assert response.status_code == 201

    resource = Resource.objects.get(pk=response.data["id"])
    resource_file = resource.files.get(is_active=True)

    download_url = (
        f"/api/v1/resources/{resource.id}/files/"
        f"{resource_file.id}/download/"
    )

    guest_client = APIClient()

    # Draft resources must not be downloadable by guests.
    response = guest_client.get(download_url)
    assert response.status_code == 404

    # Published public resources must be downloadable by guests.
    resource.status = Resource.Status.PUBLISHED
    resource.access_policy = Resource.AccessPolicy.PUBLIC
    resource.save()

    response = guest_client.get(download_url)

    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert b"".join(response.streaming_content) == b"%PDF-1.7\nminimal test pdf"
@pytest.mark.django_db
def test_invalid_file_extension_is_rejected():
    user = User.objects.create_user(
        username="invalid_extension_user",
        password="strong-pass-123",
        role=User.Role.LIBRARIAN,
    )

    client = APIClient()
    client.force_authenticate(user)

    file = io.BytesIO(b"not a supported document")
    file.name = "program.exe"

    response = client.post(
        "/api/v1/resources/",
        {"title": "Invalid Extension", "file": file},
        format="multipart",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_invalid_pdf_content_is_rejected():
    user = User.objects.create_user(
        username="invalid_pdf_user",
        password="strong-pass-123",
        role=User.Role.LIBRARIAN,
    )

    client = APIClient()
    client.force_authenticate(user)

    file = io.BytesIO(b"This is not a PDF file")
    file.name = "invalid.pdf"

    response = client.post(
        "/api/v1/resources/",
        {"title": "Invalid PDF", "file": file},
        format="multipart",
    )

    assert response.status_code == 400


def test_file_larger_than_limit_is_rejected():
    oversized_file = SimpleNamespace(
        name="large.pdf",
        size=MAX_RESOURCE_FILE_SIZE + 1,
    )

    with pytest.raises(ValidationError):
        validate_resource_file(oversized_file)


@pytest.mark.django_db
def test_duplicate_file_content_is_rejected():
    user = User.objects.create_user(
        username="duplicate_user",
        password="strong-pass-123",
        role=User.Role.LIBRARIAN,
    )

    client = APIClient()
    client.force_authenticate(user)

    first_file = io.BytesIO(b"%PDF-1.7\nsame document content")
    first_file.name = "first.pdf"

    first_response = client.post(
        "/api/v1/resources/",
        {"title": "First Book", "file": first_file},
        format="multipart",
    )

    assert first_response.status_code == 201

    second_file = io.BytesIO(b"%PDF-1.7\nsame document content")
    second_file.name = "second.pdf"

    second_response = client.post(
        "/api/v1/resources/",
        {"title": "Second Book", "file": second_file},
        format="multipart",
    )

    assert second_response.status_code == 400