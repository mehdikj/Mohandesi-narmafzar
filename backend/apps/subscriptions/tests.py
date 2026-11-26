
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import SubscriptionPlan, UserSubscription


User = get_user_model()


class SubscriptionAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="subscription_user",
            password="TestPassword123"
        )

        self.other_user = User.objects.create_user(
            username="other_subscription_user",
            password="TestPassword123"
        )

        self.active_plan = SubscriptionPlan.objects.create(
            name="Monthly Plan",
            description="Monthly subscription",
            duration_days=30,
            price=100000,
            is_active=True,
        )

        self.inactive_plan = SubscriptionPlan.objects.create(
            name="Inactive Plan",
            duration_days=30,
            price=50000,
            is_active=False,
        )

    def create_subscription(self, user, status=UserSubscription.Status.ACTIVE):
        now = timezone.now()

        return UserSubscription.objects.create(
            user=user,
            plan=self.active_plan,
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=29),
            status=status,
        )

    def test_public_plan_list_shows_only_active_plans(self):
        response = self.client.get(
            "/api/v1/subscription-plans/",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Monthly Plan")

    def test_anonymous_user_cannot_access_subscriptions(self):
        response = self.client.get(
            "/api/v1/my-subscriptions/",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 401)

    def test_user_can_only_see_own_subscriptions(self):
        self.create_subscription(self.user)
        self.create_subscription(self.other_user)

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            "/api/v1/my-subscriptions/",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["plan"]["name"], "Monthly Plan")
        self.assertTrue(response.data[0]["is_valid"])

    def test_expired_subscription_is_not_valid(self):
        now = timezone.now()

        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.active_plan,
            start_date=now - timedelta(days=10),
            end_date=now - timedelta(days=1),
        )

        self.assertFalse(subscription.is_valid)

    def test_user_can_cancel_own_active_subscription(self):
        subscription = self.create_subscription(self.user)

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f"/api/v1/my-subscriptions/{subscription.id}/cancel/",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 200)

        subscription.refresh_from_db()
        self.assertEqual(
            subscription.status,
            UserSubscription.Status.CANCELLED,
        )

    def test_user_cannot_cancel_other_users_subscription(self):
        subscription = self.create_subscription(self.other_user)

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f"/api/v1/my-subscriptions/{subscription.id}/cancel/",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 404)

        subscription.refresh_from_db()
        self.assertEqual(
            subscription.status,
            UserSubscription.Status.ACTIVE,
        )

    def test_cancelled_subscription_cannot_be_cancelled_again(self):
        subscription = self.create_subscription(
            self.user,
            UserSubscription.Status.CANCELLED,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f"/api/v1/my-subscriptions/{subscription.id}/cancel/",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 400)
