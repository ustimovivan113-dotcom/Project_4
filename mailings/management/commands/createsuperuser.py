from django.contrib.auth.management.commands import (
    createsuperuser as django_createsuperuser,
)
from django.core.management import CommandError


class Command(django_createsuperuser.Command):
    """
    Кастомная команда createsuperuser для модели без username.
    Запрашивает только email и пароль.
    """

    def add_arguments(self, parser):
        super().add_arguments(parser)
        # Убираем аргумент username из парсера
        for action in parser._actions[:]:
            if action.dest == "username":
                parser._actions.remove(action)
                break

    def handle(self, *args, **options):
        # Убираем username, если он каким-то образом остался
        options["username"] = None

        # Email
        email = options.get("email")
        if not email:
            email = input("Email address: ").strip()
            if not email:
                raise CommandError("Email обязателен.")

        # Пароль
        while True:
            password = input("Password: ")
            password2 = input("Password (again): ")
            if password != password2:
                self.stderr.write(self.style.ERROR("Пароли не совпадают."))
                continue
            if password.strip() == "":
                self.stderr.write(self.style.ERROR("Пароль не может быть пустым."))
                continue
            break

        try:
            self.UserModel._default_manager.create_superuser(
                email=email,
                password=password,
            )
            self.stdout.write(
                self.style.SUCCESS(f'Суперпользователь "{email}" успешно создан.')
            )
        except Exception as e:
            raise CommandError(f"Ошибка: {e}")
