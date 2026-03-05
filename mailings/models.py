"""
Модели для приложения mailings.
Содержит: Message, Recipient, Mailing, MailingAttempt
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class Recipient(models.Model):
    """Получатель рассылки."""
    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=200, verbose_name='ФИО')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipients',
        verbose_name='Владелец'
    )

    class Meta:
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'
        permissions = [
            ('view_all_recipients', 'Может просматривать всех получателей'),
        ]

    def __str__(self):
        return f'{self.full_name} <{self.email}>'


class Message(models.Model):
    """Сообщение для рассылки."""
    subject = models.CharField(max_length=255, verbose_name='Тема')
    body = models.TextField(verbose_name='Текст сообщения')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Владелец'
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        permissions = [
            ('view_all_messages', 'Может просматривать все сообщения'),
        ]

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    """
    Рассылка. Статус вычисляется динамически через property
    на основе текущего времени и start_time/end_time.
    """
    STATUS_CREATED = 'created'
    STATUS_STARTED = 'started'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_CREATED, 'Создана'),
        (STATUS_STARTED, 'Запущена'),
        (STATUS_COMPLETED, 'Завершена'),
    ]

    start_time = models.DateTimeField(verbose_name='Дата и время начала')
    end_time = models.DateTimeField(verbose_name='Дата и время окончания')
    # храним вручную переданный статус (можно принудительно завершить)
    _status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name='Статус',
        db_column='status'
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name='Сообщение'
    )
    recipients = models.ManyToManyField(
        Recipient,
        related_name='mailings',
        verbose_name='Получатели'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name='Владелец'
    )

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        permissions = [
            ('view_all_mailings', 'Может просматривать все рассылки'),
            ('disable_mailing', 'Может отключать рассылки'),
        ]

    @property
    def status(self):
        """Определяем статус рассылки в зависимости от текущего момента."""
        now = timezone.now()
        if self._status == self.STATUS_COMPLETED:
            return self.STATUS_COMPLETED
        if now < self.start_time:
            return self.STATUS_CREATED
        if self.start_time <= now <= self.end_time:
            return self.STATUS_STARTED
        return self.STATUS_COMPLETED

    @status.setter
    def status(self, value):
        self._status = value

    def get_status_display_value(self):
        """Для отображения в шаблоне читаемого статуса."""
        status_map = {
            self.STATUS_CREATED: 'Создана',
            self.STATUS_STARTED: 'Запущена',
            self.STATUS_COMPLETED: 'Завершена',
        }
        return status_map.get(self.status, self.status)

    def __str__(self):
        return f'Рассылка #{self.pk} ({self.get_status_display_value()})'


class MailingAttempt(models.Model):
    """Попытка отправки рассылки."""
    STATUS_OK = 'ok'
    STATUS_FAIL = 'fail'
    STATUS_CHOICES = [
        (STATUS_OK, 'Успешно'),
        (STATUS_FAIL, 'Ошибка'),
    ]

    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Рассылка'
    )
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время попытки')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name='Статус'
    )
    server_response = models.TextField(blank=True, verbose_name='Ответ сервера')

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылок'
        ordering = ['-attempt_time']

    def __str__(self):
        return f'Попытка {self.pk} для {self.mailing} - {self.get_status_display()}'
