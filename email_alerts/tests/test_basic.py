from django.core import mail
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
