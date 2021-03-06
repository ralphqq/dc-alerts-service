import os
import time

from selenium.webdriver.common.keys import Keys

from func_tests.base import FunctionalTest


MAX_WAIT = 30   # seconds
SAMPLE_RECIPIENT_EMAIL = os.environ.get('SAMPLE_RECIPIENT_EMAIL', 'validemail@example.com')


class OptOutPageTest(FunctionalTest):

    def test_user_can_request_unsubscribe_link(self):
        # User visits homepage
        self.browser.get(self.live_server_url)

        # User sees the 'Unsubscribe' item in the top navbar
        menu_item = self.browser.find_element_by_xpath(
            '//a[@class="nav-link" and text()="Unsubscribe"]'
        )
        menu_item.click()

        # She sees the title 'Unsubscribe from our mailing list'
        text_to_find = 'Unsubscribe from our mailing list'
        self.assertIn(text_to_find, self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn(text_to_find, header_text)

        # She is asked to enter her email address
        email_input_box = self.browser.find_element_by_id('id_email_optout')
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
                '//h1[contains(text(), "Click")]'
            )
        )
        self.assertIn(
            'Click the link we sent you',
            header_text.text
        )

        # She also sees the email address she typed.
        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn(valid_email, body_text)
