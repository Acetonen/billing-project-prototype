from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from project.accounts.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    ordering = ("email", "first_name", "last_name")
    list_display = ("email", "is_staff", "created")
    readonly_fields = ("created", "updated")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important dates",
            {
                "fields": (
                    "created",
                    "updated",
                    "last_login",
                )
            },
        ),
    )
