"""
Представления для приложения mailings.
"""

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from .forms import MailingForm, MessageForm, RecipientForm
from .models import Mailing, MailingAttempt, Message, Recipient

from django.contrib.auth.mixins import LoginRequiredMixin


# =============================================================================
# Миксин для проверки владельца или прав
# =============================================================================
class OwnerOrPermRequiredMixin:
    """Миксин: доступ только владельцу или пользователю с нужным разрешением."""

    permission_required = None  # например: "mailings.view_all_mailings"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object() if hasattr(self, "get_object") else None
        if obj is None:
            return super().dispatch(request, *args, **kwargs)

        if obj.owner == request.user:
            return super().dispatch(request, *args, **kwargs)

        if self.permission_required and request.user.has_perm(self.permission_required):
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied


# =============================================================================
# Главная страница
# =============================================================================
@method_decorator(cache_page(60 * 5), name="dispatch")
class HomeView(TemplateView):
    """Главная страница с общей статистикой."""

    template_name = "mailings/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        mailing_stats = Mailing.objects.aggregate(
            total=Count("id"),
            active=Count("id", filter=Q(status=Mailing.STATUS_STARTED)),
        )

        ctx.update(
            {
                "total_mailings": mailing_stats["total"],
                "active_mailings": mailing_stats["active"],
                "unique_recipient_count": Recipient.objects.values("email")
                .distinct()
                .count(),
            }
        )
        return ctx


# =============================================================================
# Message CRUD
# =============================================================================
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailings/message_list.html"
    context_object_name = "messages"
    paginate_by = 25

    def get_queryset(self):
        if self.request.user.has_perm("mailings.view_all_messages"):
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailings/message_form.html"
    success_url = reverse_lazy("mailings:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, OwnerOrPermRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailings/message_form.html"
    success_url = reverse_lazy("mailings:message_list")
    permission_required = "mailings.view_all_messages"


class MessageDeleteView(LoginRequiredMixin, OwnerOrPermRequiredMixin, DeleteView):
    model = Message
    template_name = "mailings/message_confirm_delete.html"
    success_url = reverse_lazy("mailings:message_list")
    permission_required = "mailings.view_all_messages"


# =============================================================================
# Recipient CRUD
# =============================================================================
class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = "mailings/recipient_list.html"
    context_object_name = "recipients"
    paginate_by = 25

    def get_queryset(self):
        if self.request.user.has_perm("mailings.view_all_recipients"):
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=self.request.user)


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailings/recipient_form.html"
    success_url = reverse_lazy("mailings:recipient_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, OwnerOrPermRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailings/recipient_form.html"
    success_url = reverse_lazy("mailings:recipient_list")
    permission_required = "mailings.view_all_recipients"


class RecipientDeleteView(LoginRequiredMixin, OwnerOrPermRequiredMixin, DeleteView):
    model = Recipient
    template_name = "mailings/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailings:recipient_list")
    permission_required = "mailings.view_all_recipients"


# =============================================================================
# Mailing CRUD
# =============================================================================
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailings/mailing_list.html"
    context_object_name = "mailings"
    paginate_by = 20

    def get_queryset(self):
        qs = Mailing.objects.select_related("message")
        if self.request.user.has_perm("mailings.view_all_mailings"):
            return qs.all()
        return qs.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, OwnerOrPermRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:mailing_list")
    permission_required = "mailings.view_all_mailings"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class MailingDetailView(LoginRequiredMixin, OwnerOrPermRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailings/mailing_detail.html"
    context_object_name = "mailing"
    permission_required = "mailings.view_all_mailings"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["attempts"] = self.object.attempts.select_related("recipient").order_by(
            "-created_at"
        )
        return ctx


class MailingDeleteView(LoginRequiredMixin, OwnerOrPermRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailings/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailings:mailing_list")
    permission_required = "mailings.view_all_mailings"


# =============================================================================
# Ручная отправка рассылки (временное решение — лучше вынести в celery)
# =============================================================================
class SendMailingView(LoginRequiredMixin, OwnerOrPermRequiredMixin, View):
    permission_required = "mailings.view_all_mailings"

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        if mailing.status == Mailing.STATUS_COMPLETED:
            return redirect("mailings:mailing_detail", pk=pk)

        recipients = mailing.recipients.all()
        if not recipients.exists():
            return redirect("mailings:mailing_detail", pk=pk)

        message_obj = mailing.message
        success_count = 0
        fail_count = 0

        for recipient in recipients.iterator():  # экономим память
            try:
                email = EmailMessage(
                    subject=message_obj.subject,
                    body=message_obj.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient.email],
                )
                email.send(fail_silently=False)

                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status=MailingAttempt.STATUS_OK,
                    server_response="OK",
                )
                success_count += 1

            except Exception as exc:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status=MailingAttempt.STATUS_FAIL,
                    server_response=str(exc)[:1000],
                )
                fail_count += 1

            # Защита от блокировки SMTP-сервера
            import time

            time.sleep(
                0.12
            )  # ~8–9 писем в секунду — безопасно для большинства провайдеров

        # Опционально: завершаем рассылку, если нет ошибок
        if fail_count == 0 and success_count > 0:
            mailing.status = Mailing.STATUS_COMPLETED
            mailing.save(update_fields=["status"])

        return redirect("mailings:mailing_detail", pk=pk)


# =============================================================================
# Список попыток
# =============================================================================
class AttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = "mailings/attempt_list.html"
    context_object_name = "attempts"
    paginate_by = 30

    def get_queryset(self):
        qs = MailingAttempt.objects.select_related("mailing", "recipient")
        if self.request.user.has_perm("mailings.view_all_mailings"):
            return qs.all()
        return qs.filter(mailing__owner=self.request.user)
