from django.core.mail import EmailMessage

def send_email(email_obj):
    """Sends transactional email."""
    msg = EmailMessage(
        subject=email_obj.subject_line,
        body=email_obj.message_body,
        to=[email_obj.recipient.email]
    )
    msg.send()
    