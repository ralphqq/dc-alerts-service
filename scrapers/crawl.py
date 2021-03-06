import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class CrawlTaskHandler:

    def __init__(self, spider, log_enabled=True, **kwargs):
        os.environ.setdefault(
            'SCRAPY_SETTINGS_MODULE',
            'scrapers.scrapers.settings'
        )

        # Custom settings
        s = get_project_settings()
        s['SPIDER_MODULES'] = ['scrapers.scrapers.spiders']
        s['NEWSPIDER_MODULE'] = 'scrapers.scrapers.spiders'
        s['ITEM_PIPELINES'] = {
            'scrapers.scrapers.pipelines.ScrapersPipeline': 300,
        }
        s['LOG_ENABLED'] = log_enabled

        self.process = CrawlerProcess(s)
        self.spider = spider
        self.kwargs = kwargs

    def run_spider(self):
        self.process.crawl(self.spider, **self.kwargs)
        self.process.start()
