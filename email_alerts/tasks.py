import logging

from celery import shared_task, task
from django.core.mail import EmailMessage
from django.utils import timezone

from email_alerts.models import TransactionalEmail


@shared_task(bind=True, max_retries=6)
def send_one_email(self, email_id, subject, body, recipient):
    try:
        email_object = TransactionalEmail.objects.get(pk=email_id)
        msg = EmailMessage(
            subject=subject,
            body=body,
            to=[recipient]
        )
    except TransactionalEmail.DoesNotExist:
        self.retry(countdown= 2 ** self.request.retries)
    msg.send()
    email_object.date_sent = timezone.now()
    email_object.message_body = msg.body
    email_object.save()


@task(name='prepare-send-alerts')
def prepare_and_send_alerts(scraper_success):
    if scraper_success:
        logging.info('Preparing alert')
    else:
        logging.info('Cannot prepare alert')
