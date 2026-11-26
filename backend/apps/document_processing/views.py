from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from apps.resources.models import ResourceFile

from .models import OCRJob
from .serializers import OCRJobCreateSerializer, OCRJobSerializer


class IsLibrarian(BasePermission):
    message = "Only librarians and administrators can access OCR operations."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_librarian()
        )


class OCRJobCreateView(generics.CreateAPIView):
    serializer_class = OCRJobCreateSerializer
    permission_classes = [IsAuthenticated, IsLibrarian]

    def perform_create(self, serializer):
        resource_file = get_object_or_404(
            ResourceFile,
            pk=self.kwargs["resource_file_id"],
            is_active=True,
            file_type=ResourceFile.FileType.PDF,
        )

        serializer.save(
            resource_file=resource_file,
            created_by=self.request.user,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        output_serializer = OCRJobSerializer(serializer.instance)

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class OCRJobDetailView(generics.RetrieveAPIView):
    queryset = OCRJob.objects.select_related(
        "resource_file",
        "resource_file__resource",
        "created_by",
    )
    serializer_class = OCRJobSerializer
    permission_classes = [IsAuthenticated, IsLibrarian]