from hashlib import sha256
import json

from django.apps import apps
from django.db import models
from django.utils import timezone

from notices.utils import (
    datetime_as_str,
    get_datetime_from_text
)


class OutageNotice(models.Model):
    notice_id = models.CharField(max_length=20, unique=True)
    urgency = models.CharField(max_length=20)
    source_url = models.URLField(max_length=256)
    headline = models.CharField(max_length=180)
    details = models.TextField()
    provider = models.CharField(max_length=50)
    service = models.CharField(max_length=25)
    posted_on = models.DateTimeField(default=timezone.now)
    scraped_on = models.DateTimeField(default=timezone.now)
    scheduled_for = models.DateTimeField(null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        raw_details = kwargs.get('details')
        if raw_details is not None:
            self.set_outage_schedules(raw_details)

    def __str__(self):
        return f'<OutageNotice: {self.headline}>'

    def set_notice_id(self):
        """Helper function to generate unique notice_id.

        This function makes hash value from self.source_url
        and assigns first 20 characters of the resulting hex digest to 
        the variable self.notice_id.
        """
        h = sha256(self.source_url.encode())
        self.notice_id = h.hexdigest()[:20]

    def set_outage_schedules(self, raw_details):
        """Extracts schedules and assigns into appropriate fields.

        This method gets dates and times from the 'when' 
        field of each outage set in the raw_details 
        variable.

        The extracted datetime strings are then converted into 
        tz-aware datetime objects with UTC offset which are 
        then assigned to the 'sched' field of the 
        corresponding outage set.

        The updated details variable is then dumped into the 
        notice instance's details field.

        The earliest datetime object is also assigned to the 
        notice instance's scheduled_for field.
        """
        updated_details = []
        soonest_sched = None

        for item in raw_details:
            sched = get_datetime_from_text(item.get('when'))
            item['sched'] = sched
            updated_details.append(item)

            if soonest_sched is None or (sched is not None and 
                sched < soonest_sched):
                # Assign to temporary variable
                soonest_sched = sched

        self.details = json.dumps(updated_details, default=datetime_as_str)
        self.scheduled_for = soonest_sched

    def load_details(self):
        """Returns value in details field as Python list object."""
        return json.loads(self.details)


    def create_email_alerts(self):
        """Creates email alerts for each active user.

        The resulting collection of email alerts will then be 
        assigned to this instance's email_alerts attribute.
        """
        Subscriber = apps.get_model('subscribers', 'Subscriber')
        active_users = Subscriber.get_all_active_subscribers()

        for user in active_users:
            alert = self.email_alerts.create(
                recipient=user,
                subject_line=self.headline
            )
            alert.render_message_body(
                template='email_alerts/alert.html',
                context={'recipient': user, 'notice': self}
            )
            alert.save()
