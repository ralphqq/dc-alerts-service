from django.core.mail import get_connection, EmailMultiAlternatives


def send_email(email_obj):
    """Sends transactional email."""
    msg = EmailMultiAlternatives(
        subject=email_obj.subject_line,
        body=email_obj.message_body,
        to=[email_obj.recipient.email],
        alternatives=[(email_obj.html_content, 'text/html')]
    )
    msg.send()


def send_email_alerts(alerts):
    """Handles bulk send-out of email alerts.

    Args:
        alerts (list): list of EmailAlert objects

    Returns:
        int: the number of emails sent
    """
    sent_count = 0
    with get_connection() as connection:
        messages = [
            EmailMultiAlternatives(
                subject=alert.subject_line,
                body=alert.message_body,
                to=[alert.recipient.email],
                alternatives=[(alert.html_content, 'text/html')]
            )
            for alert in alerts

            ]
        sent_count = connection.send_messages(messages)
    return sent_count
