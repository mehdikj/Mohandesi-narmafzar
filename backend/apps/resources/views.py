from pathlib import Path

from django.http import FileResponse, Http404
from rest_framework import generics, permissions
from rest_framework.views import APIView
from .services import get_accessible_resources

from .models import Author, Category, Resource, ResourceFile
from .permissions import ResourceAccessPermission
from .serializers import (
    AuthorSerializer,
    CategorySerializer,
    ResourceSerializer,
)

class AuthorListCreateView(generics.ListCreateAPIView):
    queryset = Author.objects.all().order_by("name")
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if not self.request.user.is_librarian():
            self.permission_denied(self.request)

        serializer.save()


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if not self.request.user.is_librarian():
            self.permission_denied(self.request)

        serializer.save()


class ResourceListCreateView(generics.ListCreateAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [ResourceAccessPermission]

    def get_queryset(self):
        return get_accessible_resources(self.request.user)


class ResourceDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [ResourceAccessPermission]

    def get_queryset(self):
        return get_accessible_resources(self.request.user)
class ResourceFileDownloadView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, resource_id, file_id):
        resource = get_accessible_resources(request.user).filter(
            pk=resource_id
        ).first()

        if resource is None:
            raise Http404

        resource_file = ResourceFile.objects.filter(
            pk=file_id,
            resource=resource,
            is_active=True,
        ).first()

        if resource_file is None:
            raise Http404

        try:
            file_handle = resource_file.file.open("rb")
        except (OSError, ValueError):
            raise Http404

        filename = Path(resource_file.file.name).name

        content_types = {
            ResourceFile.FileType.PDF: "application/pdf",
            ResourceFile.FileType.EPUB: "application/epub+zip",
        }

        return FileResponse(
            file_handle,
            as_attachment=True,
            filename=filename,
            content_type=content_types.get(
                resource_file.file_type,
                "application/octet-stream",
            ),
        )