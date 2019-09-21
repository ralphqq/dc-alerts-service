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

    def render_email_body(self, template, context=None):
        """Generates HTML and plain-text email content.

        This method expects the template to have a .html file extension 
        and that both HTML and plain-text templates have the 
        same filenames.
        """
        self.html_content = render_to_string(template, context)
        self.message_body = render_to_string(
            template.replace('.html', '.txt'),
            context
        )
        self.save()


class EmailAlert(EmailModel):
    outage = models.ForeignKey(
        'notices.OutageNotice',
        on_delete=models.CASCADE,
        related_name='email_alerts',
        null=True
    )
    recipient = models.ForeignKey(
        'subscribers.Subscriber',
        on_delete=models.CASCADE,
        related_name='email_alerts_received',
        null=True
    )


class TransactionalEmail(EmailModel):
    recipient = models.ForeignKey(
        'subscribers.Subscriber',
        on_delete=models.CASCADE,
        null=True
    )
    message_type = models.CharField(max_length=20, null=True)
