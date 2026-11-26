from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
@admin.register(User)
class LibraryUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Library role", {"fields": ("role","display_name")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Library role", {"fields": ("role","display_name")}),)
    list_display = ("username","email","role","is_active","is_staff")
    list_filter = ("role","is_active","is_staff")
