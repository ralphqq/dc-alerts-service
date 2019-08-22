from unittest import skip

from django.test import TestCase
from scrapy.http import Request
from scrapy.selector import Selector

from scrapers.scrapers.spiders.dcwd import DcwdSpider
from scrapers.tests.utils import make_response_object

# Paths to HTML test files
dcwd_index_file = 'scrapers/tests/html/dcwd_index.html'
dcwd_details_file = 'scrapers/tests/html/dcwd_details.html'


class DcwdParserTests(TestCase):

    def setUp(self):
        self.spider = DcwdSpider(limit=1)


    def test_parse(self):
        """Tests the spider's main parse method."""
        response = make_response_object(dcwd_index_file)
        raw_results = self.spider.parse(response)

        # Convert generator into list of Request objects
        valid_results = list(raw_results)

        # Test if list is non-empty
        self.assertGreater(len(valid_results), 0)

        # Test each Request object in the result
        for request in valid_results:
            self.assertIsInstance(request, Request)
            self.assertIsNotNone(request.meta)
            self.assertIsNotNone(request.meta.get('urgency'))
            self.assertIsNotNone(request.meta.get('title'))
            self.assertIsNotNone(request.meta.get('notice_id'))


    def test_parse_page(self):
        """Tests the spider's parse_page method."""
        response = make_response_object(
            filepath=dcwd_details_file,
            meta={'urgency': 'a', 'title': 'Some Title', 'notice_id': '123'}
        )
        raw_results = self.spider.parse_page(response)
        valid_results = list(raw_results)

        self.assertGreater(len(valid_results), 0)
        for item in valid_results:
            self.assertIsNotNone(item.get('urgency'))
            self.assertIsNotNone(item.get('headline'))
            self.assertIsNotNone(item.get('source_url'))
            self.assertIsNotNone(item.get('notice_id'))
            self.assertIsNotNone(item.get('posted_on'))
            self.assertIsInstance(item.get('details'), list)
            self.assertIsNotNone(item.get('scraped_on'))
            self.assertEqual(item.get('provider'), 'DCWD')
            self.assertEqual(item.get('service'), 'Water')
