from django.core import mail
from django.shortcuts import reverse
from django.test import TestCase

from email_alerts.models import TransactionalEmail
from email_alerts.utils import send_email
from subscribers.models import Subscriber


class SendMailTest(TestCase):

    def test_send_email_function(self):
        new_user = Subscriber.objects.create(email='noreply@example.com')
        test_email = TransactionalEmail(
            recipient=new_user,
            subject_line='Testing email send-outs'
        )
        mail_created_at = test_email.date_sent
        send_email(
            email_object=test_email,
            email_template='email_alerts/test.html',
            context={'recipient': new_user}
        )
        test_email.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(test_email.date_sent > mail_created_at)


    def test_if_signup_generates_confirmation_email(self):
        test_email_address = 'foo@example.com'
        response = self.client.post(
            reverse('register_new_email'),
            data={'email_address': test_email_address}
        )
        msg = mail.outbox[0]
        new_user = Subscriber.objects.get(email=test_email_address)

        self.assertEqual(len(mail.outbox), 1)
        self.assertSequenceEqual(msg.recipients(), [new_user.email])
        self.assertEqual(msg.subject, 'Please confirm your email address')
