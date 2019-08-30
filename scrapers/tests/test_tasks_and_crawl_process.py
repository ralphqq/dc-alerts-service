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

    @patch('scrapers.crawl.CrawlerProcess.crawl')
    def test_task_calls_dcwd_spider(self, mock_process):
        run_dcwd_spider()
        self.assertEqual(mock_process.called, True)


    @patch('scrapers.crawl.CrawlerProcess.crawl')
    def test_task_calls_dcwd_spider_with_args(self, mock_process_with_args):
        run_dcwd_spider(input='inputargument', db_mode='skip')
        self.assertEqual(mock_process_with_args.called, True)
        _, kwargs = mock_process_with_args.call_args
        self.assertEqual(kwargs.get('input'), 'inputargument')
        self.assertEqual(kwargs.get('db_mode'), 'skip')


    @patch('scrapers.tasks.CrawlTaskHandler.run_spider')
    def test_task_runs_dcwd_spider_and_returns_true(self, mock_dcwd_crawl):
        result = run_dcwd_spider()
        self.assertEqual(mock_dcwd_crawl.called, True)
        self.assertEqual(result, True)


    @patch('scrapers.tasks.CrawlTaskHandler.run_spider')
    def test_task_returns_false_if_scrape_fails(self, mock_start_crawl):
        mock_start_crawl.side_effect = ValueError
        result = run_dcwd_spider()
        self.assertEqual(result, False)
