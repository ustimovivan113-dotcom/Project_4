from django.contrib import admin

from mailings.models import Mailing, MailingAttempt, Message, Recipient


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "owner")
    search_fields = ("subject",)


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "owner")
    search_fields = ("email", "full_name")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("pk", "start_time", "end_time", "owner")
    list_filter = ("owner",)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ("pk", "mailing", "attempt_time", "status")
    list_filter = ("status",)
    readonly_fields = ("attempt_time",)
