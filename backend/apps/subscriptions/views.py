
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import SubscriptionPlan, UserSubscription
from .serializers import (
    SubscriptionPlanSerializer,
    UserSubscriptionSerializer,
)


class SubscriptionPlanListView(generics.ListAPIView):
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return SubscriptionPlan.objects.filter(is_active=True)


class MySubscriptionListView(generics.ListAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            UserSubscription.objects
            .filter(user=self.request.user)
            .select_related("plan")
        )


class CancelSubscriptionView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSubscriptionSerializer

    def post(self, request, *args, **kwargs):
        subscription = generics.get_object_or_404(
            UserSubscription,
            pk=kwargs["subscription_id"],
            user=request.user,
        )

        if subscription.status != UserSubscription.Status.ACTIVE:
            raise ValidationError(
                "Only active subscriptions can be cancelled."
            )

        subscription.status = UserSubscription.Status.CANCELLED
        subscription.save(update_fields=["status"])

        return Response(self.get_serializer(subscription).data)
