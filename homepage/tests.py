from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone

from notices.models import OutageNotice
from notices.tests.utils import create_fake_details
from subscribers.forms import SignupForm


class HomePageTest(TestCase):

    def test_homepage_uses_correct_template(self):
        response = self.client.get(reverse('homepage'))
        self.assertTemplateUsed(response, 'homepage/index.html')


    def test_homepage_uses_signup_form(self):
        response = self.client.get(reverse('homepage'))
        self.assertIsInstance(response.context['form'], SignupForm)


class HomepageNoticeTableTest(TestCase):

    def setUp(self):
        # Create upcoming (pending) outage notices
        n1 = OutageNotice.objects.create_and_set(
            raw_details=[create_fake_details(date_offset=7)],
            urgency='Emergency',
            source_url='https://www.test.com/1',
            headline='Upcoming outage notice 1',
            provider='Utility Co., Ltd.',
            service='Water',
            posted_on=timezone.now()
        )

        n2 = OutageNotice.objects.create_and_set(
            raw_details=[create_fake_details(date_offset=10)],
            urgency='Emergency',
            source_url='https://www.test.com/2',
            headline='Upcoming outage notice 2',
            provider='Utility Co., Ltd.',
            service='Water',
            posted_on=timezone.now()
        )

        # An expired/outdated outage notice:
        n3 = OutageNotice.objects.create_and_set(
            raw_details=[create_fake_details(date_offset=-5)],
            urgency='Scheduled',
            source_url='https://www.test.com/3',
            headline='Upcoming outage notice 3',
            provider='Utility Co., Ltd.',
            service='Water',
            posted_on=timezone.now()
        )

        self.notices = [n1, n2, n3]
        self.response = self.client.get(reverse('homepage'))


    def test_passes_only_upcoming_notices(self):
        self.assertIn('recent_alerts', self.response.context)

        upcoming_notices = self.response.context.get('recent_alerts')
        self.assertEqual(upcoming_notices.count(), 2)
        self.assertIn(self.notices[0], upcoming_notices)
        self.assertIn(self.notices[1], upcoming_notices)
        self.assertNotIn(self.notices[2], upcoming_notices)


    def test_displays_only_upcoming_notices(self):
        html_content = self.response.content.decode()
        self.assertIn(self.notices[0].headline, html_content)
        self.assertIn(self.notices[1].headline, html_content)
        self.assertNotIn(self.notices[2].headline, html_content)
