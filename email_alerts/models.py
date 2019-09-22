from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone

from email_alerts.misc import emojis


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

        This method assigns the rendered results to the instance's 
        `html_content` and `message_body` attributes and calls `save()`.
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

    def set_alert_subject_line(self, notice):
        """Creates subject line based on notice attributes.

        This method then assigns the resulting subject line text to 
        the instance's `subject_line` attribute and calls `save()`.
        """
        h = notice.headline
        s = notice.service.title()
        m = emojis.get(s.lower(), emojis['default'])
        first_part = f'{m} {s} Service Advisory: '

        # Limit subject line to 50 characters
        subject = ''
        if len(first_part) + len(h) < 50:
            subject = f'{first_part}{h}'
        else:
            # free space for headline snippet takes
            # into account the 3 characters for ellipsis,
            # thus: 50 - 3 = 47
            num_chars = 47 - len(first_part)
            subject = f'{first_part}{h[:num_chars]}...'

        # Assign to subject_line attribute and save
        self.subject_line = subject
        self.save()


class TransactionalEmail(EmailModel):
    recipient = models.ForeignKey(
        'subscribers.Subscriber',
        on_delete=models.CASCADE,
        null=True
    )
    message_type = models.CharField(max_length=20, null=True)
