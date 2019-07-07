from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone


def send_email(email_object, email_template, context=None):
    msg = EmailMessage(
        subject=email_object.subject_line,
        body=render_to_string(email_template, context),
        to=[email_object.recipient.email]
    )
    msg.send()
    email_object.date_sent = timezone.now()
    email_object.message_body = msg.body
