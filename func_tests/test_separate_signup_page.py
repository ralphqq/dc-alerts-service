from urllib.parse import urljoin

from django.shortcuts import reverse
from selenium.webdriver.common.keys import Keys

from func_tests.base import FunctionalTest
from subscribers.models import Subscriber
from subscribers.views import BAD_SIGNUP_ERROR_MSG


class SeparateSignUpPageTest(FunctionalTest):

    def test_separate_signup_page(self):
        # User visits homepage
        self.browser.get(self.live_server_url)

        # She sees the link to the About page 
        # in the top navbar and clicks it
        about = self.wait_for(
            lambda: self.browser.find_element_by_xpath(
                '//li/a[contains(text(), "About")]'
            )
        )
        about.click()

        # She sees the Sign up CTA
        # at bottom of page and clicks it
        signup_cta = self.wait_for(
            lambda: self.browser.find_element_by_xpath('//h4/a')
        )
        signup_cta.click()

        # She reads the main heading
        # and knows she's on the right page
        self.wait_for(lambda: self.assertIn(
                'Sign',
                self.browser.find_element_by_xpath('//h1').text
            )
        )

        # She sees the input box 
        # asking her to enter a valid email
        email_input_box = self.browser.find_element_by_id('id_email')
        self.assertEqual(
            email_input_box.get_attribute('placeholder'),
            'Enter your email address'
        )

        # She provides a valid email address
        valid_email = 'x123.y456@xyz.com'
        email_input_box.send_keys(valid_email)

        # She ticks the consent checkbox.
        self.indicate_consent()

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

        # User goes directly to signup page
        signup_page_url = urljoin(self.live_server_url, reverse('signup'))
        self.browser.get(signup_page_url)

        # She is already an active subscriber, 
        # but still decides to sign up anyway.
        email_input_box = self.browser.find_element_by_id('id_email')
        email_input_box.send_keys(active_user.email)
        self.indicate_consent()

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
        signup_page_url = urljoin(self.live_server_url, reverse('signup'))
        self.browser.get(signup_page_url)

        # He provides his old email address.
        email_input_box = self.browser.find_element_by_id('id_email')
        email_input_box.send_keys(inactive_user.email)
        self.indicate_consent()

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


    def test_can_only_register_if_user_gives_consent(self):
        # User goes directly to signup page
        signup_page_url = urljoin(self.live_server_url, reverse('signup'))
        self.browser.get(signup_page_url)

        # She submits an email address
        new_email_address = 'foo@xmail.com'
        email_input = self.browser.find_element_by_id('id_email')
        email_input.send_keys(new_email_address)

        # She sees that the Register button is grayed out,
        # so she doesn't click it.
        register_btn = self.browser.find_element_by_id('submit-btn')
        self.assertEqual(register_btn.is_enabled(), False)

        # She tries pressing enter.
        email_input.send_keys(Keys.ENTER)

        # But receives a helpful alert saying 
        # that she needs to check the consent box first.
        alert_div = self.wait_for(
            lambda: self.browser.find_element_by_id('consent-reminder')
        )
        self.wait_for(
            lambda: self.assertIn(
                'Please acknowledge',
                alert_div.text
            )
        )

        # Internally, the signup never proceeds.
        with self.assertRaises(Subscriber.DoesNotExist):
            Subscriber.objects.get(email=new_email_address)

        # She closes the alert.
        alert_div.find_element_by_tag_name('button').click()

        # She indicates her consent.
        self.indicate_consent()

        # She clicks the register button.
        register_btn.click()

        # A page then loads asking to click
        # the link in the email we sent.
        header_text = self.wait_for(
            lambda: self.browser.find_element_by_xpath(
                '//h1[contains(text(), "Confirm")]'
            )
        )
        self.assertIn(
            'Confirm your email',
            header_text.text
        )
