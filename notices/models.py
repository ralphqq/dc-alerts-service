from hashlib import sha256
import json

from django.db import models
from django.utils import timezone


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        raw_details = kwargs.get('details')
        if raw_details is not None:
            self.details = json.dumps(raw_details)

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

    def load_details(self):
        """Returns value in details field as Python list object."""
        return json.loads(self.details)