from django.core import mail
from django.template.loader import render_to_string

from email_alerts.models import TransactionalEmail
from email_alerts.tasks import process_and_send_email
from email_alerts.tests.base_test_setup import EmailTestCase
from subscribers.models import Subscriber


class SendEmailTest(EmailTestCase):

    def test_send_email_function(self):
        new_user = Subscriber.objects.create(email='noreply@example.com')
        test_email = TransactionalEmail.objects.create(
            recipient=new_user,
            subject_line='Testing email send-outs'
        )
        test_email.render_email_body(template='email_alerts/test.html')
        mail_created_at = test_email.date_sent
        task = process_and_send_email.delay(
            email_id=test_email.pk
        )
        result = task.get()

        self.assertEqual(len(mail.outbox), 1)

        msg = mail.outbox[0]
        self.assertEqual(msg.subject, test_email.subject_line)
