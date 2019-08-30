from unittest.mock import patch

from django.shortcuts import reverse

from email_alerts.tests.base_test_setup import EmailTestCase
from subscribers.models import Subscriber
from subscribers.utils import create_secure_link


class CeleryTransactionalEmailTasksTest(EmailTestCase):

    @patch('email_alerts.tasks.process_and_send_email.delay')
    def test_signup_triggers_task(self, send_confirm_email):
        test_email_address = 'foo@example.com'
        response = self.client.post(
            reverse('register_new_email'),
            data={'email': test_email_address}
        )
        self.assertEqual(send_confirm_email.called, True)


    @patch('email_alerts.tasks.process_and_send_email.delay')
    def test_successful_confirm_triggers_sendout(self, send_welcome_email):
        # Create a user and request object
        new_user, request = self.create_user_and_request(
            email='test2@test.com'
        )

        # Create a confirmation link
        confirmation_link = create_secure_link(
            request=request,
            user=new_user,
            viewname='verify_email'
        )

        # Follow the confirmation link
        response = self.client.get(confirmation_link)
        self.assertEqual(send_welcome_email.called, True)


    @patch('email_alerts.tasks.process_and_send_email.delay')
    def test_optout_request_triggers_sendout(self, send_optout_email):
        # Create and activate a new user
        new_user = Subscriber.objects.create(
            email='test4@test.com',
            is_active=True
        )

        # Call the view that requests an optout email
        response = self.client.post(
            reverse('optout_request'),
            data={'email': new_user.email}
        )

        self.assertEqual(send_optout_email.called, True)


    @patch('email_alerts.tasks.process_and_send_email.delay')
    def test_successful_optout_triggers_sendout(self, send_goodbye_email):
        # Create a user and request object
        new_user, request = self.create_user_and_request(
            email='test3@test.com'
        )

        # Activate the new user
        new_user.is_active = True
        new_user.save()

        # Create an optout link for the new user
        unsubscribe_link = create_secure_link(
            request=request,
            user=new_user,
            viewname='unsubscribe_user'
        )

        # Follow the unsubscribe link
        response = self.client.get(unsubscribe_link)
        self.assertEqual(send_goodbye_email.called, True)
