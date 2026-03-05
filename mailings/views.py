"""
Представления для приложения mailings.
"""
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView, DeleteView, DetailView,
    ListView, TemplateView, UpdateView, View
)

from mailings.forms import MailingForm, MessageForm, RecipientForm
from mailings.models import Mailing, MailingAttempt, Message, Recipient


# =============== Главная страница ===============

@method_decorator(cache_page(60 * 5), name='dispatch')  # кешируем на 5 минут
class HomeView(TemplateView):
    """Главная страница с общей статистикой."""
    template_name = 'mailings/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_mailings'] = Mailing.objects.count()
        # активные - те, у которых статус "started"
        all_mailings = Mailing.objects.all()
        ctx['active_mailings'] = sum(1 for m in all_mailings if m.status == Mailing.STATUS_STARTED)
        ctx['unique_recipients'] = Recipient.objects.values('email').distinct().count()
        return ctx


# =============== Message CRUD ===============

class MessageListView(LoginRequiredMixin, ListView):
    """Список сообщений текущего пользователя."""
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        # менеджер видит все, обычный - только свои
        user = self.request.user
        if user.has_perm('mailings.view_all_messages'):
            return Message.objects.all()
        return Message.objects.filter(owner=user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Создание нового сообщения."""
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование сообщения."""
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # проверяем, что пользователь - владелец
        if obj.owner != self.request.user and not self.request.user.has_perm('mailings.view_all_messages'):
            raise PermissionDenied
        return obj


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление сообщения."""
    model = Message
    template_name = 'mailings/message_confirm_delete.html'
    success_url = reverse_lazy('mailings:message_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user:
            raise PermissionDenied
        return obj


# =============== Recipient CRUD ===============

class RecipientListView(LoginRequiredMixin, ListView):
    """Список получателей."""
    model = Recipient
    template_name = 'mailings/recipient_list.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        user = self.request.user
        if user.has_perm('mailings.view_all_recipients'):
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=user)


class RecipientCreateView(LoginRequiredMixin, CreateView):
    """Добавление получателя."""
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:recipient_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование получателя."""
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:recipient_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user and not self.request.user.has_perm('mailings.view_all_recipients'):
            raise PermissionDenied
        return obj


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление получателя."""
    model = Recipient
    template_name = 'mailings/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailings:recipient_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user:
            raise PermissionDenied
        return obj


# =============== Mailing CRUD ===============

class MailingListView(LoginRequiredMixin, ListView):
    """Список рассылок."""
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        user = self.request.user
        if user.has_perm('mailings.view_all_mailings'):
            return Mailing.objects.select_related('message').all()
        return Mailing.objects.select_related('message').filter(owner=user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Создание рассылки."""
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование рассылки."""
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user and not self.request.user.has_perm('mailings.view_all_mailings'):
            raise PermissionDenied
        return obj


class MailingDetailView(LoginRequiredMixin, DetailView):
    """Детальная страница рассылки с попытками."""
    model = Mailing
    template_name = 'mailings/mailing_detail.html'
    context_object_name = 'mailing'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['attempts'] = self.object.attempts.all()
        return ctx

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user and not self.request.user.has_perm('mailings.view_all_mailings'):
            raise PermissionDenied
        return obj


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление рассылки."""
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user:
            raise PermissionDenied
        return obj


# =============== Отправка рассылки вручную ===============

class SendMailingView(LoginRequiredMixin, View):
    """
    Ручная отправка рассылки.
    Проверяем статус, шлём каждому получателю, записываем попытку.
    """

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        if mailing.owner != request.user and not request.user.has_perm('mailings.view_all_mailings'):
            raise PermissionDenied

        if mailing.status == Mailing.STATUS_COMPLETED:
            # уже завершена - отправлять нечего
            return redirect('mailings:mailing_detail', pk=pk)

        recipients = mailing.recipients.all()
        status = MailingAttempt.STATUS_OK
        response_text = 'Успешно отправлено'

        try:
            emails = [r.email for r in recipients]
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=None,  # берём DEFAULT_FROM_EMAIL из settings
                recipient_list=emails,
                fail_silently=False,
            )
        except Exception as e:
            status = MailingAttempt.STATUS_FAIL
            response_text = str(e)

        MailingAttempt.objects.create(
            mailing=mailing,
            status=status,
            server_response=response_text,
        )

        return redirect('mailings:mailing_detail', pk=pk)


# =============== Попытки рассылок ===============

class AttemptListView(LoginRequiredMixin, ListView):
    """Все попытки рассылок текущего пользователя."""
    model = MailingAttempt
    template_name = 'mailings/attempt_list.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        user = self.request.user
        if user.has_perm('mailings.view_all_mailings'):
            return MailingAttempt.objects.select_related('mailing').all()
        return MailingAttempt.objects.select_related('mailing').filter(mailing__owner=user)
