from django.conf import settings
from django.test import TestCase


class MiscStuffTest(TestCase):

    def test_external_url_building_settings(self):
        self.assertEqual(
            settings.EXTERNAL_URL_SCHEME,
            'http'
        )
        self.assertEqual(
            settings.EXTERNAL_URL_HOST,
            'testserver'
        )