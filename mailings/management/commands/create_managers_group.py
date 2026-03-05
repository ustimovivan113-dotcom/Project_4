"""
Management command to create Manager group with necessary permissions.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from mailings.models import Mailing, Message, Recipient, MailingAttempt


class Command(BaseCommand):
    help = "Creates Managers group with permissions to view all mailings, messages, recipients"

    def handle(self, *args, **options):
        # Создаём группу менеджеров
        managers_group, created = Group.objects.get_or_create(name="Managers")

        if created:
            self.stdout.write(self.style.SUCCESS("Created Managers group"))
        else:
            self.stdout.write("Managers group already exists")

        # Список нужных прав (codename → описание)
        permissions_data = [
            ("view_all_mailings", "Может просматривать все рассылки", Mailing),
            ("disable_mailing", "Может отключать рассылки", Mailing),
            ("view_all_messages", "Может просматривать все сообщения", Message),
            ("view_all_recipients", "Может просматривать всех получателей", Recipient),
        ]

        added_permissions = []

        for codename, name, model_class in permissions_data:
            content_type = ContentType.objects.get_for_model(model_class)

            perm, created_perm = Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=content_type,
            )
            if created_perm:
                self.stdout.write(self.style.SUCCESS(f"Created permission: {codename}"))
            added_permissions.append(perm)

        # Добавляем все собранные права группе
        managers_group.permissions.add(*added_permissions)

        count = len(added_permissions)
        self.stdout.write(
            self.style.SUCCESS(f"Added {count} permission(s) to Managers group")
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Done! Managers can now view all objects and disable mailings."
            )
        )
