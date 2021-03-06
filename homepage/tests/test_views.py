from django.db.models import Max, Min
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


    def test_chronological_order_of_notices(self):
        upcoming_notices = self.response.context.get('recent_alerts')
        soonest_notice = upcoming_notices.first()
        soonest_sched = upcoming_notices.aggregate(
            soonest=Min('scheduled_for')
        ).get('soonest')
        farthest_notice = upcoming_notices.last()
        farthest_sched = upcoming_notices.aggregate(
            farthest=Max('scheduled_for')
        ).get('farthest')
        self.assertEqual(soonest_notice.scheduled_for, soonest_sched)
        self.assertEqual(farthest_notice.scheduled_for, farthest_sched)


    def test_displays_only_upcoming_notices(self):
        html_content = self.response.content.decode()
        self.assertIn(self.notices[0].headline, html_content)
        self.assertIn(self.notices[1].headline, html_content)
        self.assertNotIn(self.notices[2].headline, html_content)


class AboutPageTest(TestCase):

    def test_about_us_page(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage/about.html')


class ContactPageTest(TestCase):

    def test_contact_us_page(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage/contact.html')


class TermsOfUsePageTest(TestCase):

    def test_terms_of_use_page(self):
        response = self.client.get(reverse('terms'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage/terms.html')


class PrivacyPolicyPageTest(TestCase):

    def test_privacy_policy_page(self):
        response = self.client.get(reverse('privacy'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage/privacy.html')


class SignUpPageTest(TestCase):

    def test_signup_page_uses_correct_template(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage/signup.html')


    def test_signup_page_uses_signup_form(self):
        response = self.client.get(reverse('signup'))
        self.assertIsInstance(response.context['form'], SignupForm)
