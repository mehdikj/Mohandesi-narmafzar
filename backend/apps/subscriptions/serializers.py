
from rest_framework import serializers

from .models import SubscriptionPlan, UserSubscription


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = (
            "id",
            "name",
            "description",
            "duration_days",
            "price",
        )


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserSubscription
        fields = (
            "id",
            "plan",
            "start_date",
            "end_date",
            "status",
            "is_valid",
            "created_at",
        )
