from django.core import mail
from django.template.loader import render_to_string

from email_alerts.models import TransactionalEmail
from email_alerts.tasks import send_one_email
from email_alerts.tests.base_test_setup import EmailTestCase
from subscribers.models import Subscriber


class SendEmailTest(EmailTestCase):

    def test_send_email_function(self):
        new_user = Subscriber.objects.create(email='noreply@example.com')
        test_email = TransactionalEmail(
            recipient=new_user,
            subject_line='Testing email send-outs'
        )
        mail_created_at = test_email.date_sent
        test_email.save()
        task = send_one_email.delay(
            email_id=test_email.pk,
            subject=test_email.subject_line,
            body=render_to_string('email_alerts/test.html'),
            recipient=new_user.email
        )
        result = task.get()

        self.assertEqual(len(mail.outbox), 1)

        msg = mail.outbox[0]
        self.assertEqual(msg.subject, test_email.subject_line)
