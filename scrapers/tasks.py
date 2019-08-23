from celery import task

from scrapers.crawl import CrawlTaskHandler
from scrapers.scrapers.spiders.dcwd import DcwdSpider


@task(name='dcwd-spider')
def run_dcwd_spider():
    crawler = CrawlTaskHandler(DcwdSpider)
    crawler.run_spider()
