from func_tests.base import FunctionalTest


class AllStaticPagesTest(FunctionalTest):

    def check_heading_text(self, heading_text):
        """Waits for given text to be found in h1 tag."""
        self.wait_for(lambda: self.assertIn(
            heading_text,
            self.browser.find_element_by_xpath('.//h1').text
        ))


    def test_all_static_pages(self):
        # User visits homepage
        self.browser.get(self.live_server_url)

        # She sees the link to the About page 
        # in the top navbar and clicks it
        about = self.browser.find_element_by_xpath(
            '//li/a[contains(text(), "About")]'
        )
        about.click()

        # She then sees the page heading
        self.check_heading_text('About')

        # She sees the link to the Terms page 
        # in the footer and clicks it
        terms = self.browser.find_element_by_xpath(
            '//li/a[contains(text(), "Terms")]'
        )
        terms.click()

        # She then sees the page heading
        self.check_heading_text('Terms of Use')

        # She sees the link to the Privacy Policy page 
        # also in the footer and clicks it
        privacy = self.browser.find_element_by_xpath(
            '//li/a[contains(text(), "Privacy")]'
        )
        privacy.click()

        # She then sees the page heading
        self.check_heading_text('Privacy Notice')

        # She sees the link to the Contact Us page 
        # also in the footer and clicks it
        contact_us = self.browser.find_element_by_xpath(
            '//li/a[contains(text(), "Contact")]'
        )
        contact_us.click()

        # She then sees the page heading
        self.check_heading_text('Contact')
