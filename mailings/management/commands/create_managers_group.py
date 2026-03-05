"""
Management command to create Manager group with necessary permissions.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Creates Managers group with permissions to view all mailings, messages, recipients'

    def handle(self, *args, **options):
        # Создаём группу менеджеров
        managers_group, created = Group.objects.get_or_create(name='Managers')

        if created:
            self.stdout.write(self.style.SUCCESS('Created Managers group'))
        else:
            self.stdout.write('Managers group already exists')

        # Добавляем права на просмотр всех объектов
        from mailings.models import Mailing, Message, Recipient, MailingAttempt

        models = [Mailing, Message, Recipient, MailingAttempt]
        perms_codenames = ['view_all_mailings', 'view_all_messages', 'view_all_recipients']

        content_types = {}
        for model in models:
            ct = ContentType.objects.get_for_model(model)
            content_types[model._meta.model_name] = ct

        # Права для Mailing
        perm_view_all_mailings, _ = Permission.objects.get_or_create(
            codename='view_all_mailings',
            name='Может просматривать все рассылки',
            content_type=content_types['mailing']
        )
        perm_disable_mailing, _ = Permission.objects.get_or_create(
            codename='disable_mailing',
            name='Может отключать рассылки',
            content_type=content_types['mailing']
        )

        # Права для Message
        perm_view_all_messages, _ = Permission.objects.get_or_create(
            codename='view_all_messages',
            name='Может просматривать все сообщения',
            content_type=content_types['message']
        )

        # Права для Recipient
        perm_view_all_recipients, _ = Permission.objects.get_or_create(
            codename='view_all_recipients',
            name='Может просматривать всех получателей',
            content_type=content_types['recipient']
        )

        # Добавляем все права группе менеджеров
        perms = [
            perm_view_all_mailings,
            perm_disable_mailing,
            perm_view_all_messages,
            perm_view_all_recipients,
        ]

        for perm in perms:
            managers_group.permissions.add(perm)

        self.stdout.write(self.style.SUCCESS('Added permissions to Managers group'))
        self.stdout.write(self.style.SUCCESS('Done! Managers can now view all objects.'))
