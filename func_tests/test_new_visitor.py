import os
import time

from selenium.webdriver.common.keys import Keys

from func_tests.base import FunctionalTest
from subscribers.models import Subscriber
from subscribers.views import BAD_SIGNUP_ERROR_MSG


MAX_WAIT = 30   # seconds
SAMPLE_RECIPIENT_EMAIL = os.environ.get('SAMPLE_RECIPIENT_EMAIL', 'validemail@example.com')


class NewVisitorTest(FunctionalTest):

    def test_user_can_register_via_email(self):
        # User visits homepage
        self.browser.get(self.live_server_url)

        # User sees the page title and header mention 'Never miss'
        text_to_find = 'Never miss'
        self.assertIn(text_to_find, self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn(text_to_find, header_text)

        # She is asked to enter her email address
        email_input_box = self.browser.find_element_by_id('id_email')
        self.assertEqual(
            email_input_box.get_attribute('placeholder'),
            'Enter your email address'
        )

        # She provides a valid email address
        valid_email = SAMPLE_RECIPIENT_EMAIL
        email_input_box.send_keys(valid_email)

        # She hits enter and a page loads asking to click
        # the link in the email we sent
        email_input_box.send_keys(Keys.ENTER)
        header_text = self.wait_for(
            lambda: self.browser.find_element_by_xpath(
                '//h1[contains(text(), "Confirm")]'
            )
        )
        self.assertIn(
            'Confirm your email',
            header_text.text
        )

        # She also sees the email address she typed.
        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn(valid_email, body_text)


    def test_cannot_signup_again_if_active(self):
        active_user = Subscriber.objects.create(
            email='activeuser@gmail.com',
            is_active=True
        )

        # User goes to the homepage.
        self.browser.get(self.live_server_url)

        # She is already an active subscriber, 
        # but still decides to sign up anyway.
        email_input_box = self.browser.find_element_by_id('id_email')
        email_input_box.send_keys(active_user.email)

        # She hits enter and an error message appears 
        # saying she cannot proceed with the signup.
        email_input_box.send_keys(Keys.ENTER)
        alert_div = self.wait_for(
            lambda: self.browser.find_element_by_xpath('//div[@role="alert"]')
        )
        self.assertIn(
            BAD_SIGNUP_ERROR_MSG,
            alert_div.text
        )


    def test_inactive_user_can_still_sign_up(self):
        inactive_user = Subscriber.objects.create(
            email='inactiveuser@gmail.com'
        )
        
        # A user who has unsubscribed wants to sign up again.
        # He visits the homepage.
        self.browser.get(self.live_server_url)

        # He provides his old email address.
        email_input_box = self.browser.find_element_by_id('id_email')
        email_input_box.send_keys(inactive_user.email)

        # He hits enter and a page loads asking to click
        # the link in the email we sent.
        email_input_box.send_keys(Keys.ENTER)
        header_text = self.wait_for(
            lambda: self.browser.find_element_by_xpath(
                '//h1[contains(text(), "Confirm")]'
            )
        )
        self.assertIn(
            'Confirm your email',
            header_text.text
        )

        # He also sees the email address he typed.
        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn(inactive_user.email, body_text)
