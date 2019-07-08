from django.db import models
from django.utils import timezone

from subscribers.models import Subscriber


class EmailAlert(models.Model):
    recipients = models.ManyToManyField('subscribers.Subscriber')
    date_sent = models.DateTimeField(default=timezone.now)
    subject_line = models.CharField(max_length=255)
    message_body = models.TextField()


    def __str__(self):
        return self.subject_line


    def add_recipients(self):
        for active_subscriber in Subscriber.objects.filter(is_active=True):
            self.recipients.add(active_subscriber)


class TransactionalEmail(models.Model):
    recipient = models.ForeignKey(
        'subscribers.Subscriber',
        on_delete=models.CASCADE,
        null=True
    )
    date_sent = models.DateTimeField(default=timezone.now)
    subject_line = models.CharField(max_length=255)
    message_body = models.TextField()

    def __str__(self):
        return self.subject_line
