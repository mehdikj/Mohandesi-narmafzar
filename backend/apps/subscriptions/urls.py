
from django.urls import path

from .views import (
    SubscriptionPlanListView,
    MySubscriptionListView,
    CancelSubscriptionView,
)

urlpatterns = [
    path(
        "subscription-plans/",
        SubscriptionPlanListView.as_view(),
        name="subscription-plan-list",
    ),
    path(
        "my-subscriptions/",
        MySubscriptionListView.as_view(),
        name="my-subscription-list",
    ),
    path(
        "my-subscriptions/<int:subscription_id>/cancel/",
        CancelSubscriptionView.as_view(),
        name="subscription-cancel",
    ),
]
