from rest_framework import serializers
from apps.resources.services import get_accessible_resources

from .models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    resource_title = serializers.CharField(
        source="resource.title",
        read_only=True,
    )

    class Meta:
        model = Favorite
        fields = (
            "id",
            "resource",
            "resource_title",
            "created_at",
        )
        read_only_fields = (
            "id",
            "created_at",
        )

    def validate_resource(self, resource):
        

        user = self.context["request"].user

        if not get_accessible_resources(user).filter(
            pk=resource.pk
        ).exists():
            raise serializers.ValidationError(
                "You cannot add this resource to favorites."
            )

        return resource

    def validate(self, attrs):
        user = self.context["request"].user
        resource = attrs.get("resource")

        if Favorite.objects.filter(
            user=user,
            resource=resource,
        ).exists():
            raise serializers.ValidationError(
                "This resource is already in your favorites."
            )

        return attrs
