import logging

from celery import shared_task, task
from django.core.mail import EmailMessage
from django.utils import timezone

from email_alerts.models import TransactionalEmail


@shared_task(bind=True, max_retries=6)
def process_and_send_email(self, email_id):
    try:
        email_obj = TransactionalEmail.objects.get(pk=email_id)
    except TransactionalEmail.DoesNotExist:
        self.retry(countdown= 2 ** self.request.retries)

    msg = EmailMessage(
        subject=email_obj.subject_line,
        body=email_obj.message_body,
        to=[email_obj.recipient.email]
    )
    msg.send()
    email_obj.date_sent = timezone.now()
    email_obj.save()


@task(name='prepare-send-alerts')
def prepare_and_send_alerts(scraper_success):
    if scraper_success:
        logging.info('Preparing alert')
    else:
        logging.info('Cannot prepare alert')
