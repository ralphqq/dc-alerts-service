# -*- coding: utf-8 -*-
from datetime import datetime

import scrapy

from ..items import ScrapersItem, ScrapersLoader

# xpaths for home page:
main_xpath = '//h3[a/text()="{}"]/parent::*'
item_xpath = './/li'
item_title_xpath = './/h4/text()'
item_link_xpath = './/a/@href'
item_id_xpath = './/a/@id'

# xpaths for details page:
date_xpath = '//div[@class="divTitle"]//b/text()'
sets_xpath = '//h1[@class="black"]/parent::*'
set_name_xpath = './h1/text()'
when_xpath = './following-sibling::div[@class="panel panel-success"][1]//div[@class="divInput"]//text()'
where_xpath = './following-sibling::div[@class="panel panel-info"][1]//text()'
why_xpath = './following-sibling::div[@class="panel panel-primary"][1]//div[@class="divInput"]//text()'


class DcwdSpider(scrapy.Spider):
    name = 'dcwd'
    allowed_domains = ['davao-water.gov.ph']
    start_urls = ['http://davao-water.gov.ph/']

    def parse(self, response):
        for urgency in ['Scheduled', 'Emergency']:
            # Select priority/urgency group
            notice_type = response.xpath(main_xpath.format(urgency))

            # Select all notices in a priority category
            notices = notice_type.xpath(item_xpath)

            # Process each notice
            for notice in notices:
                text = notice.xpath(item_title_xpath).extract_first()
                link = notice.xpath(item_link_xpath).extract_first()
                id = notice.xpath(item_id_xpath).extract_first()
                
                if id is not None:
                    yield response.follow(link,
                                          callback=self.parse_page,
                                          meta={'urgency': urgency,
                                                'title': text,
                                                'notice_id': id})

    def parse_page(self, response):
        date_scraped = datetime.utcnow()
        date_posted = response.xpath(date_xpath).extract_first()

        # Select all sets in outage
        sets = response.xpath(sets_xpath)

        w_details = []
        for s in sets:
            w_set = {}
            w_set['set_n'] = s.xpath(set_name_xpath).extract_first()
            w_set['when'] = s.xpath(when_xpath).extract()
            w_set['where'] = s.xpath(where_xpath).extract()
            w_set['why'] = s.xpath(why_xpath).extract()
            w_details.append(w_set)

        l = ScrapersLoader(ScrapersItem())
        l.add_value('urgency', response.meta['urgency'])
        l.add_value('headline', response.meta['title'])
        l.add_value('source_url', response.url)
        l.add_value('notice_id', response.meta['notice_id'])
        l.add_value('posted_on', date_posted)
        l.add_value('details', w_details)
        l.add_value('scraped_on', date_scraped)
        l.add_value('provider', ['DCWD'])
        l.add_value('service', ['Water'])

        yield l.load_item()
