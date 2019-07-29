from django.template.loader import render_to_string

from email_alerts.tasks import send_one_email


def send_email(email_object, email_template, context=None):
    send_one_email.delay(
        email_id=email_object.pk,
        subject=email_object.subject_line,
        body=render_to_string(email_template, context),
recipient=email_object.recipient.email
    )
