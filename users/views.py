"""
Представления для приложения users.
"""

from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from users.forms import UserRegisterForm, UserProfileForm
from users.models import User


class UserRegisterView(CreateView):
    """Регистрация нового пользователя."""

    model = User
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")


class UserLoginView(LoginView):
    """Авторизация пользователя."""

    template_name = "users/login.html"


class UserLogoutView(LogoutView):
    """Выход из системы."""

    pass


class UserProfileView(LoginRequiredMixin, UpdateView):
    """Просмотр и редактирование профиля текущего пользователя."""

    model = User
    form_class = UserProfileForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        # возвращаем текущего пользователя - нет смысла передавать pk
        return self.request.user
