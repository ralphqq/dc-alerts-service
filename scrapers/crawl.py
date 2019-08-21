import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class CrawlTaskHandler:

    def __init__(self, spider):
        os.environ.setdefault(
            'SCRAPY_SETTINGS_MODULE',
            'scrapers.settings'
        )
        self.process = CrawlerProcess(get_project_settings())
        self.spider = spider

    def run_spider(self):
        self.process.crawl(self.spider)
        self.process.start()
