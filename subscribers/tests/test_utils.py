from unittest.mock import patch

from django.shortcuts import reverse
from django.test import TestCase

from subscribers.models import Subscriber
from subscribers.utils import create_secure_link


class SecureLinkTests(TestCase):

    @patch('subscribers.models.Subscriber.send_transactional_email')
    def test_secure_link_without_request_object(self, mock_send_email):
        # Create an active user
        user = Subscriber.objects.create(
            email='abc123@abc123x.com',
            is_active=True
        )
        self.assertIs(user.is_active, True)

        # Generate a one-time link for opting out
        link = create_secure_link(user=user, viewname='unsubscribe_user')
        response = self.client.get(link)
        self.assertIs(mock_send_email.called, True)

        new_user = Subscriber.objects.get(email=user.email)
        self.assertIs(new_user.is_active, False)
