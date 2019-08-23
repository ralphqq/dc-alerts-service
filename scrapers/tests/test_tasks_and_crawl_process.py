from unittest.mock import patch

from django.test import TransactionTestCase

from scrapers.crawl import CrawlTaskHandler
from scrapers.scrapers.spiders.dcwd import DcwdSpider


class ScrapersCrawlProcessTest(TransactionTestCase):

    @patch('scrapers.scrapers.spiders.dcwd.DcwdSpider.start_requests')
    def test_crawl_process_launches_dcwd_spider(self, mock_requests):
        crawl = CrawlTaskHandler(DcwdSpider)
        crawl.run_spider()
        self.assertEqual(mock_requests.called, True)

