# Generated migration for mailings app

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("subject", models.CharField(max_length=255, verbose_name="Тема")),
                ("body", models.TextField(verbose_name="Текст сообщения")),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Владелец",
                    ),
                ),
            ],
            options={
                "verbose_name": "Сообщение",
                "verbose_name_plural": "Сообщения",
                "permissions": [
                    ("view_all_messages", "Может просматривать все сообщения")
                ],
            },
        ),
        migrations.CreateModel(
            name="Recipient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="Email"
                    ),
                ),
                ("full_name", models.CharField(max_length=200, verbose_name="ФИО")),
                ("comment", models.TextField(blank=True, verbose_name="Комментарий")),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipients",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Владелец",
                    ),
                ),
            ],
            options={
                "verbose_name": "Получатель",
                "verbose_name_plural": "Получатели",
                "permissions": [
                    ("view_all_recipients", "Может просматривать всех получателей")
                ],
            },
        ),
        migrations.CreateModel(
            name="Mailing",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "start_time",
                    models.DateTimeField(verbose_name="Дата и время начала"),
                ),
                (
                    "end_time",
                    models.DateTimeField(verbose_name="Дата и время окончания"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("created", "Создана"),
                            ("started", "Запущена"),
                            ("completed", "Завершена"),
                        ],
                        default="created",
                        max_length=20,
                        verbose_name="Статус",
                        db_column="status",
                    ),
                ),
                (
                    "message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mailings",
                        to="mailings.message",
                        verbose_name="Сообщение",
                    ),
                ),
                (
                    "recipients",
                    models.ManyToManyField(
                        related_name="mailings",
                        to="mailings.recipient",
                        verbose_name="Получатели",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mailings",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Владелец",
                    ),
                ),
            ],
            options={
                "verbose_name": "Рассылка",
                "verbose_name_plural": "Рассылки",
                "permissions": [
                    ("view_all_mailings", "Может просматривать все рассылки"),
                    ("disable_mailing", "Может отключать рассылки"),
                ],
            },
        ),
        migrations.CreateModel(
            name="MailingAttempt",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "attempt_time",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата и время попытки"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("ok", "Успешно"), ("fail", "Ошибка")],
                        max_length=10,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "server_response",
                    models.TextField(blank=True, verbose_name="Ответ сервера"),
                ),
                (
                    "mailing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attempts",
                        to="mailings.mailing",
                        verbose_name="Рассылка",
                    ),
                ),
            ],
            options={
                "verbose_name": "Попытка рассылки",
                "verbose_name_plural": "Попытки рассылок",
                "ordering": ["-attempt_time"],
            },
        ),
    ]
