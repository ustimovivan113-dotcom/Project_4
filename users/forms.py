"""
Формы для приложения users.
"""

from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from users.models import User


class UserRegisterForm(UserCreationForm):
    """Форма регистрации пользователя по email."""

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # чуть украсим поля
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class UserProfileForm(UserChangeForm):
    """Форма редактирования профиля пользователя."""

    password = None  # скрываем поле пароля из этой формы

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone", "country", "avatar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
