import os
import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


MAX_WAIT = 3   # seconds


class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        staging_server = os.environ.get('STAGING_SERVER')
        if staging_server:
            self.live_server_url = f'http://{staging_server}'


    def tearDown(self):
        self.browser.quit()


    def wait_for(self, fn):
        """Sets up a generic explicit wait condition.

        This function continuously tries calling the passed function object 
        for a maximum of MAX_WAIT seconds. 

        Example usage:

            ```
            self.wait_for(lambda: self.assertEqual(
                self.browser.find_element_by_css_selector('...'),
                'Some text here'
            ))
            ```
        """
        start_time = time.time()
        while True:
            try:
                return fn()
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)
