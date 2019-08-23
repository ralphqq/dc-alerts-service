from unittest.mock import patch

from django.test import TransactionTestCase

from scrapers.crawl import CrawlTaskHandler
from scrapers.scrapers.spiders.dcwd import DcwdSpider
from scrapers.tasks import run_dcwd_spider


class ScrapersCrawlProcessTest(TransactionTestCase):

    @patch('scrapers.scrapers.spiders.dcwd.DcwdSpider.start_requests')
    def test_crawl_process_launches_dcwd_spider(self, mock_requests):
        crawl = CrawlTaskHandler(DcwdSpider, log_enabled=False)
        crawl.run_spider()
        self.assertEqual(mock_requests.called, True)


class CeleryScrapeTasksTest(TransactionTestCase):

    @patch('scrapers.tasks.CrawlTaskHandler.run_spider')
    def test_task_launches_dcwd_spider(self, mock_dcwd_crawl):
        run_dcwd_spider()
        self.assertEqual(mock_dcwd_crawl.called, True)
