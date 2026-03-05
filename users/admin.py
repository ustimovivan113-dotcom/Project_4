from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # убираем username из fieldsets т.к. его нет
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личные данные",
            {"fields": ("first_name", "last_name", "phone", "country", "avatar")},
        ),
        (
            "Права",
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
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "first_name", "last_name", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
