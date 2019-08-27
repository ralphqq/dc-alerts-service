from django.db import IntegrityError
from django.test import TestCase

from subscribers.models import Subscriber


class SubscriberModelTest(TestCase):

    def test_saving_and_retrieving_subscribers(self):
        email_1 = 'sub1@example.com'
        email_2 = 'sub2@example.com'

        # Create two new subscribers
        subscriber_1 = Subscriber.objects.create(email=email_1)
        subscriber_2 = Subscriber.objects.create(email=email_2)

        # Retrieve the two subscribers
        s1 = Subscriber.objects.get(email=email_1)
        s2 = Subscriber.objects.get(email=email_2)

        # Test if there are exactly 2 subscribers saved
        self.assertEqual(Subscriber.objects.count(), 2)

        # Test if the emails stored are correct
        self.assertEqual(s1.email, email_1)
        self.assertEqual(s2.email, email_2)


    def test_correct_permissions_at_start_of_signup(self):
        s1 = Subscriber.objects.create(email='s1@example.com')

        self.assertIs(s1.is_staff, False)
        self.assertIs(s1.is_active, False)


    def test_unique_email_constraint(self):
        # Test whether adding non-unique email address raises an IntegrityError
        with self.assertRaises(IntegrityError):
            email_1 = 'email1@example.com'
            subscriber_1 = Subscriber.objects.create(email=email_1)
            subscriber_2 = Subscriber.objects.create(email=email_1)

