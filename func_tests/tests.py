import os
import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys


MAX_WAIT = 30   # seconds
SAMPLE_RECIPIENT_EMAIL = os.environ.get('SAMPLE_RECIPIENT_EMAIL', 'validemail@example.com')


class NewVisitorTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        staging_server = os.environ.get('STAGING_SERVER')
        if staging_server:
            self.live_server_url = f'http://{staging_server}'


    def tearDown(self):
        self.browser.quit()


    def test_user_can_register_via_email(self):
        # User visits homepage
        self.browser.get(self.live_server_url)

        # User sees the page title and header mention 'Never miss'
        text_to_find = 'Never miss'
        self.assertIn(text_to_find, self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn(text_to_find, header_text)

        # She is asked to enter her email address
        email_input_box = self.browser.find_element_by_id('email_input_box')
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
        time.sleep(MAX_WAIT)
        header_text = self.browser.find_element_by_tag_name('h1')
        self.assertIn(
            'Confirm your email',
            header_text.text
        )

