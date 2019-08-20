from unittest.mock import patch

from django.shortcuts import reverse
from django.test import RequestFactory, TestCase

from subscribers.models import Subscriber
from subscribers.utils import create_secure_link


class CeleryTransactionalEmailTasksTest(TestCase):

    def create_user_and_request(self, email='foo@example.com'):
        # Create user
        user = Subscriber.objects.create(email=email)

        # Get a request object
        response = self.client.get(reverse('homepage'))  # Could be any view
        request = response.wsgi_request

        return user, request


    @patch('email_alerts.tasks.send_one_email.delay')
    def test_signup_triggers_task(self, send_confirm_email):
        test_email_address = 'foo@example.com'
        response = self.client.post(
            reverse('register_new_email'),
            data={'email_address': test_email_address}
        )
        self.assertEqual(send_confirm_email.called, True)


    @patch('email_alerts.tasks.send_one_email.delay')
    def test_successful_confirm_triggers_sendout(self, send_welcome_email):
        new_user, request = self.create_user_and_request(
            email='test2@test.com'
        )

        confirmation_link = create_secure_link(
            request=request,
            user=new_user,
            viewname='verify_email'
        )

        response = self.client.get(confirmation_link)
        self.assertEqual(send_welcome_email.called, True)


    @patch('email_alerts.tasks.send_one_email.delay')
    def test_optout_request_triggers_sendout(self, send_optout_email):
        new_user = Subscriber.objects.create(
            email='test4@test.com',
            is_active=True
        )

        response = self.client.post(
            reverse('optout_request'),
            data={'email_address': new_user.email}
        )

        self.assertEqual(send_optout_email.called, True)


    @patch('email_alerts.tasks.send_one_email.delay')
    def test_successful_optout_triggers_sendout(self, send_goodbye_email):
        new_user, request = self.create_user_and_request(
            email='test3@test.com'
        )
        new_user.is_active = True
        new_user.save()

        unsubscribe_link = create_secure_link(
            request=request,
            user=new_user,
            viewname='unsubscribe_user'
        )

        response = self.client.get(unsubscribe_link)
        self.assertEqual(send_goodbye_email.called, True)
