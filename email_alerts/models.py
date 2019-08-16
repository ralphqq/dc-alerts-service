from django.db import models
from django.utils import timezone


class EmailAlert(models.Model):
    outage = models.OneToOneField(
        'notices.OutageNotice',
        on_delete=models.CASCADE,
        related_name='email_alert',
        null=True
    )
    recipients = models.ManyToManyField('subscribers.Subscriber')
    date_sent = models.DateTimeField(default=timezone.now)
    subject_line = models.CharField(max_length=255)
    message_body = models.TextField()


    def __str__(self):
        return self.subject_line


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
