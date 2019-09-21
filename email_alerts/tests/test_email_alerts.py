from datetime import timedelta
from random import choice
from unittest import skip
from unittest.mock import patch

from django.apps import apps
from django.core import mail
from django.test import TransactionTestCase
from django.utils import timezone

from email_alerts.tasks import prepare_and_send_alerts
from notices.models import OutageNotice
from notices.tests.utils import create_fake_details


class EmailAlertTest(TransactionTestCase):

    def create_notices_and_users(self, n_notices=3, n_users=5):
        """Generates querysets of OutageNotice and Subscriber objects.

        Args:
            n_notices (int): the number of OutageNotice objects to be created
            n_users (int): the number of Subscriber objects to be created

        Returns:
            dict: the two querysets as separate items
        """
        Subscriber = apps.get_model('subscribers', 'Subscriber')

        # Create n_users active users
        for i in range(n_users):
            Subscriber.objects.create(
                email=f'user{i + 1}@examplemailer.org',
                is_active=True
            )

        # Create n_notices unsent notices,
        # unsent means an OutageNotice instance 
        # that has email_alerts equal to None
        for k in range(n_notices):
            # some preliminary arithmetic to vary dates among notices
            p = k + 1
            date_offset = timedelta(days=p)
            scheduled_for = timezone.now() + date_offset

            n = OutageNotice.objects.create_and_set(
                urgency=choice(['Scheduled', 'Emergency']),
                source_url=f'https://www.somedomain.com/notice-{p}/',
                headline=f'No utility for {p}',
                provider=choice(['DCWD', 'DLPC']),
                service=choice(['Water', 'Power']),
                raw_details=[{
                    'set_n': 'A',
                    'when': scheduled_for.strftime('%B %d, %Y at %H:%M'),
                    'where': f'Location {p}',
                    'why': 'Reason {p}'
                }]
            )

        return {
            'notices': OutageNotice.objects.all(),
            'users': Subscriber.objects.all()
        }


    @patch('email_alerts.tasks.send_email_alerts')
    def test_valid_conditions_for_bulk_sendout(self, mock_send_alerts):
        # Condition 1: There are unsent notices
        # Condition 2: scraper_success is True (returned by previous task)
        self.create_notices_and_users()
        prepare_and_send_alerts(scraper_success=True)
        self.assertEqual(mock_send_alerts.called, True)


    @patch('email_alerts.tasks.send_email_alerts')
    def test_bulk_sendout_does_not_run_if_no_unsent(self, mock_send_alerts):
        # Create a single OutageNotice instance
        payload = self.create_notices_and_users(n_notices=1, n_users=3)
        notice = payload['notices'].first()
        users = payload['users']

        # Make it a sent OutageNotice instance
        for user in users:
            user.email_alerts_received.create(outage=notice)

        prepare_and_send_alerts(scraper_success=True)
        self.assertEqual(mock_send_alerts.called, False)


    def test_send_alerts_only_to_active_users(self):
        payload = self.create_notices_and_users(n_notices=10, n_users=20)
        notices = payload['notices']
        users = payload['users']

        # Turn two Subscriber instances into inactive users
        user_1 = users.first()
        user_1.is_active = False
        user_1.save()

        user_2 = users.last()
        user_2.is_active = False
        user_2.save()

        active_users = users.filter(is_active=True)
        active_users_count = active_users.count()
        unsent_notices_count = notices.filter(email_alerts=None).count()
        processed_notices_count = prepare_and_send_alerts(scraper_success=True)
        total_alerts_sent = active_users_count * unsent_notices_count
        self.assertEqual(
            total_alerts_sent,  # supposedly sent
            len(mail.outbox)    # actually sent
        )

        # These two lists should contain the exact same unique elements:
        active_users_email_addresses = [u.email for u in active_users]
        alert_recipients = [msg.recipients()[0] for msg in mail.outbox]
        self.assertListEqual(
            sorted(active_users_email_addresses),   # supposed recipients
            sorted(list(set(alert_recipients)))     # actual recipients
        )

    @patch('email_alerts.tasks.OutageNotice.create_email_alerts')
    def test_no_alert_creation_if_no_pending_notice(self, mock_create_alerts):
        payload = self.create_notices_and_users(n_notices=3, n_users=15)
        notices = payload['notices']
        users = payload['users']

        # Make all notices outdated
        for n in notices:
            days_ago = timedelta(days=10)
            n.scheduled_for = timezone.now() - days_ago
            n.scheduled_until = timezone.now() - days_ago
            n.save()

        processed_notices_count = prepare_and_send_alerts(scraper_success=True)
        self.assertIs(mock_create_alerts.called, False)
        self.assertEqual(processed_notices_count, 0)


    def test_only_upcoming_outages_are_sent(self):
        payload = self.create_notices_and_users(
            n_notices=5,
            n_users=10
        )
        notices = payload['notices']
        users = payload['users']

        # Make one of the notices  outdated
        n = notices.last()
        n.scheduled_for = timezone.now() - timedelta(days=10)
        n.scheduled_until = timezone.now() - timedelta(days=10)
        n.save()

        upcoming_alerts = notices.filter(scheduled_until__gt=timezone.now())
        processed_notices_count = prepare_and_send_alerts(scraper_success=True)

        # Expected vs actual number of email alerts sent
        self.assertEqual(
            upcoming_alerts.count() * users.count(),
            len(mail.outbox)
        )

        # Expected vs actual number of notices processed
        self.assertEqual(
            upcoming_alerts.count(),
            processed_notices_count
        )

        # The outdated notice should not be in any active user's 
        # alerts received queryset
        Subscriber = apps.get_model('subscribers', 'Subscriber')
        for subscriber in Subscriber.objects.filter(is_active=True):
            self.assertIs(n.is_unsent(subscriber), True)


    def test_do_not_send_alerts_to_users_who_already_received_them(self):
        payload = self.create_notices_and_users(3, 10)
        notices = payload['notices']
        users = payload['users']

        # Send an alert to two users
        n = notices.first()
        user_1 = users.first()
        user_1.email_alerts_received.create(outage=n)
        user_2 = users.last()
        user_2.email_alerts_received.create(outage=n)

        processed_notices_count = prepare_and_send_alerts(True)
        self.assertEqual(
            notices.count() * users.count() - 2,
            len(mail.outbox)
        )
