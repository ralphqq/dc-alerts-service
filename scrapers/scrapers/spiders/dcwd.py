# -*- coding: utf-8 -*-
import scrapy


class DcwdSpider(scrapy.Spider):
    name = 'dcwd'
    allowed_domains = ['davao-water.gov.ph']
    start_urls = ['http://davao-water.gov.ph/']

    def parse(self, response):
        title = response.xpath('//title//text()').extract_first()
        yield title
