from django.apps import apps
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from email_alerts.utils import send_email, send_email_alerts
from notices.models import OutageNotice
from notices.tests.utils import create_fake_details


class EmailSendingFunctionTests(TestCase):

    def test_send_single_email(self):
        """Tests `email_alerts.utils.send_email()`."""
        Subscriber = apps.get_model('subscribers', 'Subscriber')
        user = Subscriber.objects.create(email='user123x123@exampleemail.com')

        email_obj = user.transactionalemail_set.create(
            subject_line='This is only a test'
        )
        email_obj.render_email_body(
            template='email_alerts/test.html',
            context={'recipient': user}
        )

        send_email(email_obj)
        self.assertEqual(len(mail.outbox), 1)

        msg = mail.outbox[0]
        self.assertEqual(msg.subject, email_obj.subject_line)
        self.assertEqual(msg.body, email_obj.message_body)
        self.assertEqual(msg.alternatives[0][0], email_obj.html_content)
        self.assertIn(user.email, msg.recipients())


    def test_send_bulk_email_alerts(self):
        """Tests `email_alerts.utils.send_email_alerts()`."""
        # Dummy outage notice
        notice = OutageNotice.objects.create_and_set(
            urgency='Emergency',
    source_url='https://www.test.com',
    headline='Test outage notice',
    raw_details=[create_fake_details(date_offset=3)],
    provider='Utility Co., Ltd.',
    service='Water',
    posted_on=timezone.now(),
    scraped_on=timezone.now()
        )
        notice.set_notice_id()
        notice.save()

        # dummy active subscribers
        Subscriber = apps.get_model('subscribers', 'Subscriber')
        sub1 = Subscriber.objects.create(
            email='sub1@example.com',
            is_active=True
        )
        sub2 = Subscriber.objects.create(
            email='sub2@example.com',
            is_active=True
        )

        # This Creates two email alerts,
        # one for each subscriber:
        alerts = notice.create_email_alerts()

        sent_count = send_email_alerts(alerts)
        self.assertEqual(sent_count, notice.email_alerts.count())
