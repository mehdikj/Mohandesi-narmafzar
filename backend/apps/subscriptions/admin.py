
from django.contrib import admin

from .models import SubscriptionPlan, UserSubscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "duration_days",
        "price",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("price",)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "start_date",
        "end_date",
        "status",
    )
    list_filter = ("status", "plan")
    search_fields = ("user__username", "plan__name")
    readonly_fields = ("created_at",)
