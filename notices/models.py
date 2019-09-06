from datetime import datetime
from hashlib import sha256
import json

from django.apps import apps
from django.db import models
from django.utils import timezone
import pytz

from notices.utils import (
    datetime_as_str,
    get_datetime_from_text
)
from subscribers.utils import create_secure_link


class OutageNoticeManager(models.Manager):

    def create_and_set(self, raw_details, source_url, **kwargs):
        """Creates and initializes an OutageNotice instance.

        Args:
            raw_details (list): a collection of notice details 
                dictionaries with the following fields:
                ('set_n', 'when', 'where', 'why')
            source_url (str): The URL of the outage notice

        Values for the other fields are passed as keyword arguments.
        """
        if raw_details is None or source_url is None:
            raise TypeError('`raw_details` and `source_url` are required.')

        notice = self.create(source_url=source_url, **kwargs)
        notice.set_notice_id()
        notice.set_outage_details(raw_details)
        notice.save()
        return notice


class OutageNotice(models.Model):
    notice_id = models.CharField(max_length=20, unique=True)
    urgency = models.CharField(max_length=20)
    source_url = models.URLField(max_length=256)
    headline = models.CharField(max_length=180)
    provider = models.CharField(max_length=50)
    service = models.CharField(max_length=25)
    posted_on = models.DateTimeField(default=timezone.now)
    scraped_on = models.DateTimeField(default=timezone.now)
    scheduled_for = models.DateTimeField(
        default=datetime(1900, 1, 1, tzinfo=pytz.UTC)
    )

    objects = OutageNoticeManager()

    def __str__(self):
        return self.headline

    def set_notice_id(self):
        """Helper function to generate unique notice_id.

        If self.notice_id is empty, This function makes 
        hash value from self.source_url and assigns first 20 
        characters of the resulting hex digest to 
        the variable self.notice_id.
        """
        if self.notice_id == '':
            h = sha256(self.source_url.encode())
            self.notice_id = h.hexdigest()[:20]

    def set_outage_details(self, raw_details):
        """Converts raw details into OutageDetails object.

        This method gets dates and times from the 'when' 
        field of each outage set in the raw_details 
        variable.

        The extracted datetime strings are then converted into 
        tz-aware datetime objects with UTC offset which are 
        then assigned to the `timestamp` field of the 
        corresponding outage set.
        
        Args:
            raw_details (list): a collection of notice details 
                dictionaries with the following fields:
                ('set_n', 'when', 'where', 'why')
        """
        for item in raw_details:
            try:
                sched = get_datetime_from_text(item.get('when'))
                details = OutageDetails.objects.create(
                    notice=self,
                    outage_batch=item.get('set_n'),
                    schedule=item.get('when'),
                    area=item.get('where'),
                    reason=item.get('why'),
                    timestamp=sched
                )
            except Exception as e:
                pass

        # Assign the nearest outage schedule to self.scheduled_for
        self.set_main_schedule()

    def set_main_schedule(self):
        """Gets the soonest outage from this notice's details set."""
        if self.details:
            soonest_sched = self.details.filter(
                timestamp__year__gt=1900    # not default value
            ).aggregate(
                soonest_sched=models.Min('timestamp')
            )
            self.scheduled_for = soonest_sched['soonest_sched']

    def load_details(self):
        """Returns value in details field as Python list object."""
        return json.loads(self.details)

    def create_email_alerts(self):
        """Creates email alerts for each active user.

        The resulting collection of email alerts will then be 
        assigned to this instance's email_alerts attribute and returned
        as a list.
        """
        alerts = []
        for user in OutageNotice.get_all_active_users():
            if self.is_unsent(user):
                alert = self.email_alerts.create(
                    recipient=user,
                    subject_line=self.headline
                )

                alert.render_message_body(
                    template='email_alerts/alert.html',
                    context={
                        'recipient': user,
                        'notice': self,
                        'unsubscribe_link': create_secure_link(
                            user=user,
                            viewname='unsubscribe_user'
                        )
                    }
                )
                alert.save()
                alerts.append(alert)

        return alerts

    def is_unsent(self, user):
        """Checks if user has not yet received the alert."""
        received_alerts = OutageNotice.objects.filter(email_alerts__recipient=user)
        return self not in received_alerts

    @staticmethod
    def get_all_active_users():
        """Wrapper for Subscriber.get_all_active_subscribers()."""
        Subscriber = apps.get_model('subscribers', 'Subscriber')
        return Subscriber.get_all_active_subscribers()

    @staticmethod
    def get_pending_notices():
        """Returns all notices with upcoming outage schedules."""
        return OutageNotice.objects.filter(scheduled_for__gt=timezone.now())


class OutageDetails(models.Model):
    notice = models.ForeignKey(
        'notices.OutageNotice',
        on_delete=models.CASCADE,
        related_name='details',
        null=True
    )
    outage_batch = models.CharField(max_length=100)
    schedule = models.CharField(max_length=560)
    area = models.TextField()
    reason = models.TextField()
    timestamp = models.DateTimeField(
        default=datetime(1900, 1, 1, tzinfo=pytz.UTC)
    )

    def __str__(self):
        return self.schedule
