from django.core import mail
from django.template.loader import render_to_string
from django.test import TransactionTestCase

from email_alerts.models import TransactionalEmail
from email_alerts.misc import emojis
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


class FancyEmailRenderingTest(EmailTestCase):

    def test_fancy_characters_in_email(self):
        s = Subscriber.objects.create(email='xxx@xmail.com')

        subject_line = ' '.join(emojis.values())
        additional_stuff = [f'{k}: {v}' for k, v in emojis.items()]
        email_obj = TransactionalEmail.objects.create(
            recipient=s,
            subject_line=subject_line
        )
        email_obj.render_email_body(
            template='email_alerts/test.html',
            context={'additional_stuff': additional_stuff}
        )
        task = process_and_send_email.delay(email_id=email_obj.pk)
        result = task.get()
        msg = mail.outbox[0]

        # Check emojis in subject line
        # as well as in plain-text and HTML content
        for k, v in emojis.items():
            self.assertIn(v, msg.subject)
            self.assertIn(v, msg.body)
            self.assertIn(v, msg.alternatives[0][0])
