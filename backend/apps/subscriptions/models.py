
from django.conf import settings
from django.db import models
from django.utils import timezone


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    duration_days = models.PositiveIntegerField()
    price = models.PositiveBigIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("price", "name")

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CANCELLED = "CANCELLED", "Cancelled"
        EXPIRED = "EXPIRED", "Expired"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="user_subscriptions",
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user} - {self.plan}"

    @property
    def is_valid(self):
        return (
            self.status == self.Status.ACTIVE
            and self.start_date <= timezone.now() < self.end_date
            and self.user.is_active
        )
