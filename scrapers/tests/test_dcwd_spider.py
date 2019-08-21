from django.test import TestCase
from scrapy.selector import Selector

from scrapers.crawl import CrawlTaskHandler
from scrapers.scrapers.spiders.dcwd import DcwdSpider
# Paths to test HTML files
dcwd_index_file = 'scrapers/tests/html/dcwd_index.html'
dcwd_details_file = 'scrapers/tests/html/dcwd_details.html'

class DcwdParserTests(TestCase):

    def setUp(self):
        self.spider = DcwdSpider(limit=1)
        with open(dcwd_index_file, 'r', encoding='utf-8') as fh:
            self.index_html = Selector(text=fh.read())
        with open(dcwd_details_file, 'r', encoding='utf-8') as fp:
            self.details_html = Selector(text=fp.read())


    def test_parse(self):
        expected = 'Home | Davao City Water District'
        result = self.spider.parse(self.index_html)
        self.assertIn(expected, list(result))
