import re
from unittest import skip

from django.core import mail
from django.shortcuts import reverse

from email_alerts.models import TransactionalEmail
from email_alerts.tests.base_test_setup import EmailTestCase
from email_alerts.utils import send_email
from subscribers.models import Subscriber
from subscribers.utils import create_secure_link


class TransactionalEmailTest(EmailTestCase):

    def setUp(self):
        self.url_re = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


    def create_user_and_request(self, email='foo@example.com'):
        # Create user
        user = Subscriber.objects.create(email=email)

        # Get a request object
        response = self.client.get(reverse('homepage'))  # Could be any view
        request = response.wsgi_request

        return user, request


    def test_if_signup_generates_confirmation_email(self):
        test_email_address = 'foo1@example.com'
        response = self.client.post(
            reverse('register_new_email'),
            data={'email_address': test_email_address}
        )
        msg = mail.outbox[0]
        new_user = Subscriber.objects.get(email=test_email_address)

        self.assertEqual(len(mail.outbox), 1)
        self.assertSequenceEqual(msg.recipients(), [new_user.email])
        self.assertEqual(msg.subject, 'Please confirm your email address')
        self.assertIsNotNone(self.url_re.search(msg.body))


    def test_successful_confirmation_sends_welcome_email(self):
        # Create user and response
        user, request = self.create_user_and_request('foo2@example.com')

        # Create a confirmation link
        confirmation_link = create_secure_link(
            request=request,
            user=user,
            viewname='verify_email'
        )

        # Activate confirmation link
        response_conf = self.client.get(confirmation_link)

        # Get the most recent email message
        msg = mail.outbox[0]

        # Check if msg has correct details
        self.assertSequenceEqual(msg.recipients(), [user.email])
        self.assertEqual(msg.subject, 'Welcome to DC Alerts!')
        self.assertIn(user.email, msg.body)


    def test_unsubscribe_sends_goodbye_email(self):
        # Create user and response
        user, request = self.create_user_and_request('foo42@example.com')

        # Confirm user
        user.is_active = True
        user.save()

        # Create an unsubscribe link
        unsubscribe_link = create_secure_link(
            request=request,
            user=user,
            viewname='unsubscribe_user'
        )

        # Follow unsubscribe link
        response_unsub = self.client.get(unsubscribe_link)

        # Get the most recent email message
        msg = mail.outbox[0]

        # Check if msg has correct details
        self.assertSequenceEqual(msg.recipients(), [user.email])
        self.assertEqual(msg.subject, 'You have successfully unsubscribed')
        self.assertIn(user.email, msg.body)


    def test_optout_request_sends_email(self):
        # Create and confirm a user
        email_address = 'fighter@abnormal.com'
        user, _ = self.create_user_and_request(email_address)
        user.is_active = True
        user.save()

        # Request an optout email
        response = self.client.post(
            reverse('optout_request'),
            data={'email_address': email_address}
        )

        # Get the most recent email message
        msg = mail.outbox[0]

        # Check if msg has correct details
        self.assertSequenceEqual(msg.recipients(), [user.email])
        self.assertEqual(msg.subject, 'Unsubscribe from our mailing list')
        self.assertIn(user.email, msg.body)
        self.assertIsNotNone(self.url_re.search(msg.body))
