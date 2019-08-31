from django.core.mail import get_connection, EmailMessage


def send_email(email_obj):
    """Sends transactional email."""
    msg = EmailMessage(
        subject=email_obj.subject_line,
        body=email_obj.message_body,
        to=[email_obj.recipient.email]
    )
    msg.send()


def send_email_alerts(notice):
    """Handles bulk send-out of email alerts.

    Returns:
        int: the number of emails sent
    """
    sent_count = 0
    with get_connection() as connection:
        messages = [
            EmailMessage(
                subject=alert.subject_line,
                body=alert.message_body,
                to=[alert.recipient.email]
            )
            for alert in notice.email_alerts.all()
        ]
        sent_count = connection.send_messages(messages)
    return sent_count
