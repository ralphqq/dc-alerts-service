from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone


class EmailModel(models.Model):
    date_sent = models.DateTimeField(default=timezone.now)
    subject_line = models.CharField(max_length=255)
    message_body = models.TextField()
    html_content = models.TextField(null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.subject_line

    def render_message_body(self, template, context=None):
        self.message_body = render_to_string(template, context)
        self.save()

    def render_html_content(self, template, context=None):
        self.html_content = render_to_string(template, context)
        self.save()


class EmailAlert(EmailModel):
    outage = models.OneToOneField(
        'notices.OutageNotice',
        on_delete=models.CASCADE,
        related_name='email_alert',
        null=True
    )
    recipients = models.ManyToManyField('subscribers.Subscriber')


class TransactionalEmail(EmailModel):
    recipient = models.ForeignKey(
        'subscribers.Subscriber',
        on_delete=models.CASCADE,
        null=True
    )
