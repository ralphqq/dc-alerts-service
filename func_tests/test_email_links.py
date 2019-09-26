import re
from urllib.parse import urljoin

from func_tests.base import FunctionalTest
from subscribers.models import Subscriber
from subscribers.utils import create_secure_link


class EmailLinksTests(FunctionalTest):

    def setUp(self):
        self.active_user = Subscriber.objects.create(
            email='alive.user@dvoalerts.com',
            is_active=True
        )
        self.inactive_user = Subscriber.objects.create(
            email='dead.user@dvoalerts.com'
        )


    def create_email_link(self, user, mode=''):
        """Helper method that generates full absolute URL.

        Args:
            user (Subscriber object): user to process
            mode (str): type of transaction ('confirm', 'unsubscribe')
        """
        path_url = ''

        if mode == 'confirm':
            path_url = create_secure_link(
                user=user,
                viewname='verify_email',
                external=False
            )
        elif mode == 'unsubscribe':
            path_url = create_secure_link(
                user=user,
                viewname='unsubscribe_user',
                external=False
            )

        return urljoin(self.live_server_url, path_url)


    def check_text_in_headline(self, text=''):
        """Helper method to test if text is in headline."""
        self.wait_for(
            lambda: self.assertIn(
                text,
                self.browser.find_element_by_tag_name('h1').text
            )
        )


    def test_valid_and_used_confirm_links(self):
        confirm_link = self.create_email_link(
            user=self.inactive_user,
            mode='confirm'
        )

        # User clicks the confirmation link 
        # contained in the email
        self.browser.get(confirm_link)

        # The user sees her signup is complete
        self.check_text_in_headline(
            text='Success! Your email address has been verified'
        )
        user = Subscriber.objects.get(email=self.inactive_user.email)
        self.assertEqual(user.is_active, True)

        # User tries clicking the link again
        self.browser.get(confirm_link)

        # A page loads saying it can't be done.
        self.check_text_in_headline(
            text='Unable to verify your email'
        )


    def test_invalid_confirmation_link(self):
        confirm_link = self.create_email_link(
            user=self.active_user,
            mode='confirm'
        )

        # Replace last 5 alphanumeric chars in URL with 'xxxxx'
        wrong_link = re.sub(r'[a-z0-9]{5}$', 'xxxxx', confirm_link)

        # User clicks the wrong link
        self.browser.get(wrong_link)

        # A page loads saying the verification failed.
        self.check_text_in_headline(
            text='Unable to verify your email'
        )


    def test_valid_and_used_unsubscribe_link(self):
        unsubscribe_link = self.create_email_link(
            user=self.active_user,
            mode='unsubscribe'
        )

        # User clicks unsubscribe link in email.
        self.browser.get(unsubscribe_link)

        # A page loads confirming the opt out.
        self.check_text_in_headline(
            text='successfully unsubscribed from DVO Alerts'
        )
        user = Subscriber.objects.get(email=self.active_user.email)
        self.assertEqual(user.is_active, False)

        # User tries to click the unsubscribe link again
        # and a page loads saying it can't be done.
        self.browser.get(unsubscribe_link)
        self.check_text_in_headline(
            text='Unable to process your opt-out request'
        )


    def test_invalid_unsubscribe_link(self):
        unsubscribe_link = self.create_email_link(
            user=self.active_user,
            mode='unsubscribe'
        )

        # Replace last 5 alphanumeric chars in URL with 'xxxxx'
        wrong_link = re.sub(r'[a-z0-9]{5}$', 'xxxxx', unsubscribe_link)

        # User clicks the wrong link
        self.browser.get(wrong_link)

        # A page loads saying the opt-out failed.
        self.check_text_in_headline(
            text='Unable to process your opt-out request'
        )
