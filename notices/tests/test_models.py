import json
import re
from unittest import skip

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from email_alerts.models import EmailAlert
from notices.models import OutageNotice
from notices.utils import get_datetime_from_text
from notices.tests.utils import create_fake_details
from scrapers.tests.utils import make_fake_id
from subscribers.models import Subscriber


class ModelTestCase(TestCase):

    def make_dummy_details(self, date_offset=None, **kwargs):
        """Wrapper for utils.create_fake_details()."""
        return create_fake_details(date_offset, **kwargs)


class NewOutageNoticeTest(ModelTestCase):

    def test_can_save_new_outage_notice(self):
        test_outage_notice = OutageNotice.objects.create(
            urgency='Emergency',
    source_url='https://www.test.com',
    headline='Test outage notice',
    details=[self.make_dummy_details()],
    provider='Utility Co., Ltd.',
    service='Water',
    posted_on=timezone.now(),
    scraped_on=timezone.now()
        )

        self.assertEqual(OutageNotice.objects.count(), 1)


    def test_make_notice_id(self):
        test_outage_notice = OutageNotice.objects.create(
            urgency='Emergency',
    source_url='https://www.test.com',
    headline='Test outage notice',
    details=[self.make_dummy_details()],
    provider='Utility Co., Ltd.',
    service='Water',
    posted_on=timezone.now(),
    scraped_on=timezone.now()
        )

        # Before setting a notice_id
        self.assertEqual(test_outage_notice.notice_id, '')

        # After setting notice_id
        test_outage_notice.set_notice_id()
        test_outage_notice.save()
        self.assertNotEqual(test_outage_notice.notice_id, '')
        self.assertNotEqual(
            test_outage_notice.notice_id,
            test_outage_notice.headline
        )
        self.assertEqual(len(test_outage_notice.notice_id), 20)


    def test_unique_source_url_and_unique_notice_id(self):
        test_outage_notice = OutageNotice.objects.create(
            urgency='Emergency',
    source_url='https://www.test.com/outage1.html',
    headline='Test outage notice',
    details=[self.make_dummy_details()],
    provider='Utility Co., Ltd.',
    service='Water',
    posted_on=timezone.now(),
    scraped_on=timezone.now()
        )
        test_outage_notice.set_notice_id()
        test_outage_notice.save()

        # Create an exact duplicate of test_outage_notice, do not save yet
        duplicate_notice = OutageNotice(
            urgency='Emergency',
    source_url='https://www.test.com/outage1.html',
    headline='Test outage notice',
    details=[self.make_dummy_details()],
    provider='Utility Co., Ltd.',
    service='Water',
    posted_on=timezone.now(),
    scraped_on=timezone.now()
        )

        # This assigns an already-existing notice_id,
        # since both test_outage_notice and 
        # duplicate_notice have exactly the same source_url.
        # IntegrityError will be raised only upon saving.
        duplicate_notice.set_notice_id()

        # Create a different notice
        different_notice = OutageNotice(
            urgency='Emergency',
    source_url='https://www.test.com/outage2.html',
    headline='Test outage notice',
    details=[self.make_dummy_details()],
    provider='Utility Co., Ltd.',
    service='Water',
    posted_on=timezone.now(),
    scraped_on=timezone.now()
        )
        different_notice.set_notice_id()
        different_notice.save()

        self.assertEqual(
            test_outage_notice.notice_id,
            duplicate_notice.notice_id
        )

        self.assertNotEqual(
            test_outage_notice.notice_id,
            different_notice.notice_id
        )

        with self.assertRaises(IntegrityError):
            duplicate_notice.save()


class OutageNoticeAndEmailAlertModelTest(ModelTestCase):

    def test_relationship_with_email_alert(self):
        # Dummy outage notice
        test_outage_notice = OutageNotice.objects.create(
            urgency='Emergency',
    source_url='https://www.test.com',
    headline='Test outage notice',
    details=[self.make_dummy_details(date_offset=5)],
    provider='Utility Co., Ltd.',
    service='Water',
    posted_on=timezone.now(),
    scraped_on=timezone.now()
        )
        test_outage_notice.set_notice_id()
        test_outage_notice.save()

        # dummy active subscribers
        sub1 = Subscriber.objects.create(
            email='sub1@example.com',
            is_active=True
        )
        sub2 = Subscriber.objects.create(
            email='sub2@example.com',
            is_active=True
        )

        # This Creates two email alerts,
        # one for each subscriber:
        test_outage_notice.create_email_alerts()

        self.assertEqual(test_outage_notice.email_alerts.count(), 2)

        for alert in test_outage_notice.email_alerts.all():
            self.assertIn(alert.recipient, [sub1, sub2])
            self.assertIsNotNone(re.search(
                test_outage_notice.headline,
                alert.subject_line
            ))

            for details in test_outage_notice.load_details():
                for key in ['when', 'where', 'why']:
                    self.assertIn(
                        details[key],
                        alert.message_body
                    )


class NoticeDetailsTests(ModelTestCase):

    def test_loading_and_dumping_details(self):
        dummy_details = [
            self.make_dummy_details(
                when='Aug. 23, 2019 from 5:00 a.m. to 12: p.m.'
            ),
            self.make_dummy_details(
                set_n='SET 2',
                where='Elsewhere',
                when='Aug. 23, 2019 from 1:00 p.m. to 7:00 p.m.',
                why='Valve replacement'
            )
        ]

        notice = OutageNotice.objects.create(
            notice_id=make_fake_id(),
            headline='Water outage on Aug 23',
            source_url='https://www.example.com/waters',
            details=dummy_details
        )

        self.assertIsInstance(notice.details, str)
        self.assertIsInstance(notice.load_details(), list)
        self.assertEqual(len(dummy_details), len(notice.load_details()))


    def test_notice_gets_soonest_outage_schedule(self):
        """Test the get_soonest_schedule() method.

        The get_soonest_schedule() method should return 
        the datetime object of the earliest outage set 
        scheduled or included in the notice.
        """
        # Set some arbitrary schedules
        sched_1_str = 'August 26, 2019 8 AM'
        sched_2_str = 'August 26, 2019 9 AM'
        sched_3_str = 'August 26, 2019 10 AM'

        # Convert these into datetime obj
        sched_1_dt = get_datetime_from_text(sched_1_str)
        sched_2_dt = get_datetime_from_text(sched_2_str)
        sched_3_dt = get_datetime_from_text(sched_3_str)

        # Make some dummy details based on above
        dummy_details = [
            self.make_dummy_details(when=sched_1_str),
            self.make_dummy_details(
                set_n='SET 2',
                where='Elsewhere',
                when=sched_2_str,
                why='Valve replacement'
            ),
            self.make_dummy_details(
                set_n='SET 3',
                where='Everywhere',
                when=sched_3_str,
                why='Pipeline cleanup'
            )
        ]

        notice = OutageNotice.objects.create(
            urgency='Scheduled',
            source_url='https://www.test.com/page-for-this.html',
        headline='Test outage notice',
            provider='Utility Co., Ltd.',
            service='Water',
            posted_on=timezone.now(),
            scraped_on=timezone.now(),
            details=dummy_details
        )

        self.assertEqual(notice.scheduled_for, sched_1_dt)


    def test_can_filter_out_expired_notices(self):
        # Make an upcoming outage notice
        n1 = OutageNotice.objects.create(
            urgency='Emergency',
            source_url='https://www.test.com',
            headline='Test outage notice',
            details=[self.make_dummy_details()],
            provider='Utility Co., Ltd.',
            service='Water',
            posted_on=timezone.now(),
            scraped_on=timezone.now()
        )
        n1.set_notice_id()
        n1.set_outage_schedules([
            create_fake_details(date_offset=7) # 7 days later
        ])
        n1.save()

        # Make an expired outage notice
        n2 = OutageNotice.objects.create(
            urgency='Emergency',
            source_url='https://www.test.com/123',
            headline='Test outage notice',
            details=[self.make_dummy_details()],
            provider='Utility Co., Ltd.',
            service='Water',
            posted_on=timezone.now(),
            scraped_on=timezone.now()
        )
        n2.set_notice_id()
        n2.set_outage_schedules([
            create_fake_details(date_offset=-3) # 3 days earlier
        ])
        n2.save()

        pending_notices = OutageNotice.get_pending_notices()
        self.assertEqual(OutageNotice.objects.count(), 2)
        self.assertEqual(pending_notices.count(), 1)
