import os
import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


MAX_WAIT = 3   # seconds

@tag('slow')
class FunctionalTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Firefox()
        staging_server = os.environ.get('STAGING_SERVER')
        if staging_server:
            cls.live_server_url = f'http://{staging_server}'


    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.quit()


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
