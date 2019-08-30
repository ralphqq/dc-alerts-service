import logging

from celery import task

from scrapers.crawl import CrawlTaskHandler
from scrapers.scrapers.spiders.dcwd import DcwdSpider


@task(name='dcwd-spider')
def run_dcwd_spider(**kwargs):
    try:
        crawler = CrawlTaskHandler(DcwdSpider, **kwargs)
        crawler.run_spider()
    except Exception as e:
        logging.warning(e)
        return False
    return True
