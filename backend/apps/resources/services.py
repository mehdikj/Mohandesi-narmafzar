from django.db import transaction
from rest_framework import serializers
from .models import Resource, ResourceFile
from .validators import validate_resource_file, sha256
@transaction.atomic
def register_resource(*, user, resource_data, uploaded_file):
    file_type=validate_resource_file(uploaded_file); fingerprint=sha256(uploaded_file)
    if ResourceFile.objects.filter(sha256=fingerprint).exists():
        raise serializers.ValidationError({"file":"A resource with the same file content already exists."})
    resource=Resource.objects.create(created_by=user,**resource_data)
    ResourceFile.objects.create(resource=resource,file=uploaded_file,file_type=file_type,size_bytes=uploaded_file.size,sha256=fingerprint,version=1,is_active=True)
    return resource
def get_accessible_resources(user):
    queryset = (
        Resource.objects
        .prefetch_related("authors", "files")
        .select_related("category", "created_by")
    )

    if user.is_authenticated and user.is_librarian():
        return queryset

    queryset = queryset.filter(status=Resource.Status.PUBLISHED)

    if user.is_authenticated:
        return queryset.filter(
            access_policy__in=[
                Resource.AccessPolicy.PUBLIC,
                Resource.AccessPolicy.REGISTERED_ONLY,
            ]
        )

    return queryset.filter(
        access_policy=Resource.AccessPolicy.PUBLIC
    )