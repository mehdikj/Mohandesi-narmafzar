
from rest_framework import generics, permissions

from apps.resources.services import get_accessible_resources
from .models import Favorite
from .serializers import FavoriteSerializer


class FavoriteListCreateView(generics.ListCreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        accessible_resource_ids = get_accessible_resources(
            self.request.user
        ).values("id")

        return (
            Favorite.objects
            .filter(
                user=self.request.user,
                resource_id__in=accessible_resource_ids,
            )
            .select_related("resource")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteDeleteView(generics.DestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "resource_id"
    lookup_url_kwarg = "resource_id"

    def get_queryset(self):
        return Favorite.objects.filter(
            user=self.request.user
        )
