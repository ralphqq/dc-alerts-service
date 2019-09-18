import json
import re
from unittest import skip

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from email_alerts.models import EmailAlert
from notices.models import OutageDetails, OutageNotice
from notices.utils import get_datetime_from_text
from notices.tests.utils import create_fake_details
from scrapers.tests.utils import make_fake_id
from subscribers.models import Subscriber


class ModelTestCase(TestCase):

    def make_dummy_details(self, date_offset=None, **kwargs):
        """Wrapper for utils.create_fake_details()."""
        return create_fake_details(date_offset, **kwargs)


class NewOutageNoticeTest(ModelTestCase):

    def test_saving_with_normal_create(self):
        n = OutageNotice.objects.create(
            urgency='Emergency',
            source_url='https://www.test.com',
            headline='Test outage notice',
            provider='Utility Co., Ltd.',
            service='Water',
            posted_on=timezone.now()
        )

        # Before further initialization
        self.assertEqual(OutageNotice.objects.count(), 1)
        self.assertIs(n.notice_id, '')
        self.assertEqual(n.details.count(), 0)
        self.assertEqual(n.scheduled_for.year, 1900)
        self.assertEqual(n.scraped_on.month, timezone.now().month)

        # Make two outage batches
        raw_details = [
            self.make_dummy_details(date_offset=3),
            self.make_dummy_details(date_offset=5)
        ]

        # Initialize further
        n.set_outage_details(raw_details)
        n.set_notice_id()
        n.save()

        self.assertIsNot(n.notice_id, '')
        self.assertEqual(n.details.count(), len(raw_details))
        self.assertNotEqual(n.scheduled_for.year, 1900)
        self.assertEqual(n.scraped_on.month, timezone.now().month)


    def test_saving_with_custom_create(self):
        n = OutageNotice.objects.create_and_set(
            raw_details = [
                self.make_dummy_details(date_offset=3),
                self.make_dummy_details(date_offset=5)
            ],
            urgency='Emergency',
            source_url='https://www.test.com',
            headline='Test outage notice',
            provider='Utility Co., Ltd.',
            service='Water',
            posted_on=timezone.now()
        )
        self.assertEqual(OutageNotice.objects.count(), 1)
        self.assertIsNot(n.notice_id, '')
        self.assertEqual(n.details.count(), 2)
        self.assertNotEqual(n.scheduled_for.year, 1900)
        self.assertEqual(n.scraped_on.month, timezone.now().month)


    def test_required_args_for_custom_create(self):
        with self.assertRaises(TypeError):
            n = OutageNotice.objects.create_and_set(
                source_url='https://www.outagestuffinc.com/'
            )

        with self.assertRaises(TypeError):
            m = OutageNotice.objects.create_and_set(
                raw_details=[self.make_dummy_details(date_offset=2)]
            )

        # Does not raise TypeError
        p = OutageNotice.objects.create_and_set(
            raw_details=[self.make_dummy_details(date_offset=3)],
            source_url='https://www.example-of-outage-notices.com/index.html'
        )
        self.assertEqual(OutageNotice.objects.count(), 1)


    def test_make_notice_id(self):
        test_outage_notice = OutageNotice.objects.create(
            urgency='Emergency',
    source_url='https://www.test.com',
    headline='Test outage notice',
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


    def test_unique_notice_id_with_custom_create(self):
        n1 = OutageNotice.objects.create_and_set(
            raw_details=[self.make_dummy_details(date_offset=5)],
            source_url='https://outagetoday.com/1'
        )

        # Another notice with unique source_url
        n2 = OutageNotice.objects.create_and_set(
            raw_details=[self.make_dummy_details(date_offset=5)],
            source_url='https://outagetoday.com/2'
        )

        with self.assertRaises(IntegrityError):
            # A notice with the same source_url as n2
            n2 = OutageNotice.objects.create_and_set(
                raw_details=[self.make_dummy_details(date_offset=5)],
                source_url='https://outagetoday.com/2'
            )


class OutageNoticeAndEmailAlertModelTest(ModelTestCase):

    def test_relationship_with_email_alert(self):
        # Dummy outage notice
        test_outage_notice = OutageNotice.objects.create_and_set(
            raw_details=[
                self.make_dummy_details(date_offset=3),
                self.make_dummy_details(date_offset=5)
            ],
            urgency='Emergency',
    source_url='https://www.test.com',
    headline='Test outage notice',
    provider='Utility Co., Ltd.',
    service='Water',
    posted_on=timezone.now()
        )

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

            # Headline text is in plain text content
            self.assertIsNotNone(re.search(
                test_outage_notice.headline,
                alert.message_body
            ))

            # Headline text is in HTML content
            self.assertIsNotNone(re.search(
                test_outage_notice.headline,
                alert.html_content
            ))

            for item in test_outage_notice.details.all():
                self.assertIsNot(item.outage_batch, None)
                self.assertIsNot(item.schedule, None)
                self.assertIsNot(item.area, None)
                self.assertIsNot(item.reason, None)
                self.assertNotEqual(item.timestamp.year, 1900)


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

        notice = OutageNotice.objects.create_and_set(
            raw_details=dummy_details,
            notice_id=make_fake_id(),
            headline='Water outage on Aug 23',
            source_url='https://www.example.com/waters'
        )

        self.assertEqual(notice.details.count(), len(dummy_details  ))
        self.assertIsInstance(notice.details.last(), OutageDetails)


class OutageSchedulesTest(ModelTestCase):

    def test_notice_gets_soonest_outage_schedule(self):
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

        notice = OutageNotice.objects.create_and_set(
            raw_details=dummy_details,
            urgency='Scheduled',
            source_url='https://www.test.com/page-for-this.html',
        headline='Test outage notice',
            provider='Utility Co., Ltd.',
            service='Water',
            posted_on=timezone.now()
        )

        self.assertEqual(notice.scheduled_for, sched_1_dt)


    def test_can_filter_out_expired_notices(self):
        # Make an upcoming outage notice
        n1 = OutageNotice.objects.create_and_set(
            raw_details=[self.make_dummy_details(date_offset=3)],
            urgency='Emergency',
            source_url='https://www.test.com',
            headline='Test outage notice',
            provider='Utility Co., Ltd.',
            service='Water',
            posted_on=timezone.now()
        )

        # Make an expired outage notice
        n2 = OutageNotice.objects.create_and_set(
            raw_details=[self.make_dummy_details(date_offset=-3)],
            urgency='Emergency',
            source_url='https://www.test.com/123',
            headline='Test outage notice',
            provider='Utility Co., Ltd.',
            service='Water',
            posted_on=timezone.now()
        )

        pending_notices = OutageNotice.get_pending_notices()
        self.assertEqual(OutageNotice.objects.count(), 2)
        self.assertEqual(pending_notices.count(), 1)
