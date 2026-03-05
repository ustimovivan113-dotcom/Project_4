"""
Management command to send a specific mailing manually.
Usage: python manage.py send_mailing <mailing_id>
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.utils import timezone

from mailings.models import Mailing, MailingAttempt


class Command(BaseCommand):
    help = 'Send a specific mailing by its ID'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID of the mailing to send')

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']

        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            raise CommandError(f'Mailing with ID {mailing_id} does not exist')

        self.stdout.write(f'Processing mailing #{mailing_id}...')

        # Проверяем статус
        if mailing.status == Mailing.STATUS_COMPLETED:
            self.stdout.write(self.style.WARNING('Mailing is already completed'))
            return

        recipients = mailing.recipients.all()
        if not recipients.exists():
            self.stdout.write(self.style.ERROR('No recipients in this mailing'))
            return

        status = MailingAttempt.STATUS_OK
        response_text = 'Successfully sent'

        # Отправляем письма
        try:
            emails = [r.email for r in recipients]
            count = send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=None,  # используется DEFAULT_FROM_EMAIL из settings
                recipient_list=emails,
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'Sent to {len(emails)} recipients'))
            response_text = f'Sent {count} messages'
        except Exception as e:
            status = MailingAttempt.STATUS_FAIL
            response_text = str(e)
            self.stdout.write(self.style.ERROR(f'Error: {e}'))

        # Записываем попытку
        attempt = MailingAttempt.objects.create(
            mailing=mailing,
            status=status,
            server_response=response_text,
        )

        self.stdout.write(self.style.SUCCESS(f'Created attempt #{attempt.pk} with status: {status}'))
