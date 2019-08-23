import re
from unittest import skip

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from email_alerts.models import EmailAlert
from notices.models import OutageNotice
from scrapers.tests.utils import make_fake_id
from subscribers.models import Subscriber


class NewOutageNoticeTest(TestCase):

    def test_can_save_new_outage_notice(self):
        test_outage_notice = OutageNotice.objects.create(
            urgency='Emergency',
    source_url='https://www.test.com',
    headline='Test outage notice',
    details='Test details here',
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
    details='Test details here',
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

    @skip
    def test_unique_source_url_and_unique_notice_id(self):
        test_outage_notice = OutageNotice.objects.create(
            urgency='Emergency',
    source_url='https://www.test.com/outage1.html',
    headline='Test outage notice',
    details='Test details here',
    provider='Utility Co., Ltd.',
    service='Water',
    posted_on=timezone.now(),
    scraped_on=timezone.now()
        )
        test_outage_notice.set_notice_id()

        # Create an exact duplicate of test_outage_notice
        duplicate_notice = OutageNotice.objects.create(
            urgency='Emergency',
    source_url='https://www.test.com/outage1.html',
    headline='Test outage notice',
    details='Test details here',
    provider='Utility Co., Ltd.',
    service='Water',
    posted_on=timezone.now(),
    scraped_on=timezone.now()
        )
        duplicate.set_notice_id()

        # Create a different notice
        different_notice = OutageNotice.objects.create(
            urgency='Emergency',
    source_url='https://www.test.com/outage2.html',
    headline='Test outage notice',
    details='Test details here',
    provider='Utility Co., Ltd.',
    service='Water',
    posted_on=timezone.now(),
    scraped_on=timezone.now()
        )
        different_notice.set_notice_id()

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


class OutageNoticeAndEmailAlertModelTest(TestCase):

    def test_relationship_with_email_alert(self):
        # Dummy outage notice
        test_outage_notice = OutageNotice.objects.create(
            urgency='Emergency',
    source_url='https://www.test.com',
    headline='Test outage notice',
    details='Test details here',
    provider='Utility Co., Ltd.',
    service='Water',
    posted_on=timezone.now(),
    scraped_on=timezone.now()
        )
        test_outage_notice.set_notice_id()
        test_outage_notice.save()

        # dummy subscribers
        sub1 = Subscriber.objects.create(email='sub1@example.com')
        sub2 = Subscriber.objects.create(email='sub2@example.com')

        # Dummy email alert object
        fake_email_alert = EmailAlert.objects.create(
            outage=test_outage_notice,
            subject_line=f'Alert: {test_outage_notice.headline}',
            message_body=f'Please note: {test_outage_notice.details}'
        )
        fake_email_alert.recipients.set(Subscriber.objects.all())
        fake_email_alert.save()

        self.assertIn(sub1, test_outage_notice.email_alert.recipients.all())
        self.assertIn(sub2, test_outage_notice.email_alert.recipients.all())
        self.assertIsNotNone(re.search(
            test_outage_notice.headline,
            test_outage_notice.email_alert.subject_line
        ))
        self.assertIsNotNone(re.search(
            test_outage_notice.details,
            test_outage_notice.email_alert.message_body
        ))


class NoticeDetailsTests(TestCase):

    def test_loading_and_dumping_ofdetails(self):
        dummy_details = [
            {
                'set_n': 'A',
                'where': 'Somewhere',
                'when': 'Aug. 23, 2019 from 5:00 a.m. to 12: p.m.',
                'why': 'Routine maintenance'
            },
            {
                'set_n': 'B',
                'where': 'Elsewhere',
                'when': 'Aug. 23, 2019 from 1:00 p.m. to 7:00 p.m.',
                'why': 'Valve replacement'
            }
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
