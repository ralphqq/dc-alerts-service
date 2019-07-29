from __future__ import absolute_import, unicode_literals

from celery import shared_task
from django.core.mail import EmailMessage
from django.utils import timezone

from email_alerts.models import TransactionalEmail


@shared_task
def send_one_email(email_id, subject, body, recipient):
    email_object = TransactionalEmail.objects.get(pk=email_id)
    msg = EmailMessage(
        subject=subject,
        body=body,
        to=[recipient]
    )
    msg.send()
    email_object.date_sent = timezone.now()
    email_object.message_body = msg.body
    email_object.save()
