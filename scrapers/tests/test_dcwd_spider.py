from unittest import skip

from scrapy.http import Request

from scrapers.scrapers.spiders.dcwd import DcwdSpider
from scrapers.tests.base_scraper_test_setup import ScraperTestCase, html_files
from scrapers.tests.utils import make_response_object, make_fake_id


class DcwdParserTests(ScraperTestCase):

    def setUp(self):
        self.spider = DcwdSpider(limit=1)


    def test_parse(self):
        """Tests the spider's main parse method."""
        valid_results = self.get_parse_results(
            response=make_response_object(html_files['dcwd_index'])
        )

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
        valid_results = self.get_parse_results(
            parse_method_name='parse_page',
            response=make_response_object(
                filepath=html_files['dcwd_details'],
                meta={'urgency': 'a', 'title': 'Some Title',
                      'notice_id': make_fake_id()}
            )
        )

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


    def test_water_outage_details(self):
        """Tests if scraped outage details are complete."""
        # Get results from parse_page
        valid_results = self.get_parse_results(
            parse_method_name='parse_page',
            response=make_response_object(
                filepath=html_files['dcwd_details'],
                meta={'urgency': 'a', 'title': 'Some Title',
                      'notice_id': make_fake_id()}
            )
        )        

        for item in valid_results:
            # Unpack list of outage details (dicts)
            details_per_set = item['details']
            for outage_set in details_per_set:
                self.assertIsNotNone(outage_set.get('set_n'))
                self.assertIsNotNone(outage_set.get('when'))
                self.assertIsNotNone(outage_set.get('where'))
                self.assertIsNotNone(outage_set.get('why'))
