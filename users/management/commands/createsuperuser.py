from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создает суперпользователя по email и паролю"

    def handle(self, *args, **options):
        User = get_user_model()

        email = input("Email: ").strip()
        if not email:
            self.stdout.write(self.style.ERROR("Email обязателен"))
            return

        while True:
            password = input("Пароль: ")
            password2 = input("Пароль (повтор): ")
            if password != password2:
                self.stdout.write(self.style.ERROR("Пароли не совпадают"))
                continue
            if not password:
                self.stdout.write(self.style.ERROR("Пароль не может быть пустым"))
                continue
            break

        try:
            User.objects.create_superuser(email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Суперпользователь {email} создан"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
