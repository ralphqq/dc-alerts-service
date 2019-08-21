from unittest import skip

from django.test import TestCase


class ScrapersBasicTest(TestCase):

    def test_if_scrapers_can_run_tests(self):
        pass

    @skip
    def test_if_scrapers_can_detect_failed_tests(self):
        self.fail('Failed by choice: Test not skipped')
