from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Кастомный менеджер для модели User без поля username.
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Создает и сохраняет пользователя с email и паролем.
        """
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Создает обычного пользователя.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создает суперпользователя.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомная модель пользователя с авторизацией по email.
    """

    username = None
    email = models.EmailField(unique=True, verbose_name="email")

    # Дополнительные поля по ТЗ
    phone = models.CharField(max_length=20, blank=True, verbose_name="телефон")
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="аватар"
    )
    country = models.CharField(max_length=100, blank=True, verbose_name="страна")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # Важно: подключаем кастомный менеджер
    objects = UserManager()

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return self.email
