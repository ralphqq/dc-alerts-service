from django.contrib.staticfiles.templatetags.staticfiles import static
from django.test import TestCase

from subscribers.utils import get_external_link_for_static_file


class AddAsContactTest(TestCase):

    def test_vcard_download(self):
        vcard_url = static('others/dvoalerts.vcf')
        abs_vcard_url = get_external_link_for_static_file(
            'others/dvoalerts.vcf'
        )
        self.assertIsNotNone(vcard_url)
        self.assertIn(vcard_url, abs_vcard_url)
