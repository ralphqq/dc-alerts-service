from celery import task

from scrapers.crawl import CrawlTaskHandler
from scrapers.scrapers.spiders.dcwd import DcwdSpider


@task(name='dcwd-spider')
def run_dcwd_spider(**kwargs):
    crawler = CrawlTaskHandler(DcwdSpider, **kwargs)
    crawler.run_spider()
