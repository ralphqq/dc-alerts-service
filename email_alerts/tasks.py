import logging

from celery import shared_task, task
from django.utils import timezone

from email_alerts.models import TransactionalEmail
from email_alerts.utils import send_email, send_email_alerts
from notices.models import OutageNotice


@shared_task(bind=True, max_retries=6)
def process_and_send_email(self, email_id):
    try:
        email_obj = TransactionalEmail.objects.get(pk=email_id)
        send_email(email_obj)
        email_obj.date_sent = timezone.now()
        email_obj.save()
    except TransactionalEmail.DoesNotExist:
        self.retry(countdown= 2 ** self.request.retries)


@task(name='prepare-send-alerts')
def prepare_and_send_alerts(scraper_success):
    """Retrieves new notices and sends each as email alert to active users.

    Returns:
        int: the number of notices successfully processed
        None: if no data is available from scraper
    """
    if scraper_success:
        completed_notices = 0
        all_unsent_notices = OutageNotice.get_pending_notices()

        for notice in all_unsent_notices:
            alerts = notice.create_email_alerts()

            if alerts:
                sent_count = send_email_alerts(alerts)
                logging.info(
                    f'Sent {sent_count} of {len(alerts)} '
                    f'for {notice}'
                )
                completed_notices += 1
            else:
                logging.info('No alerts created or sent')

        return completed_notices

    logging.info('No data obtained from scraper')
    return None
