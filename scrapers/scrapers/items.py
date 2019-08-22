# -*- coding: utf-8 -*-
import datetime

import pytz
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst


def clean_up_details(self, w_details):
    """Helper function to clean up details field."""
    for i, val in enumerate(w_details):
        for k in ('when', 'where', 'why'):
            clean_text = [x.strip() for x in val[k]]
            clean_text = '\n'.join(clean_text)
            w_details[i][k] = clean_text.strip()
    yield w_details


def make_tz_aware(time_string):
    """Turns time string to tz-aware datetime obj with UTC offset."""
    naive_dt = datetime.datetime.strptime(time_string.strip(), '%m/%d/%Y')
    aware_dt = pytz.timezone('Asia/Manila').localize(naive_dt)
    return aware_dt.astimezone(pytz.UTC)


class ScrapersItem(scrapy.Item):
    notice_id = scrapy.Field()
    urgency = scrapy.Field()
    source_url = scrapy.Field()
    headline = scrapy.Field()
    details = scrapy.Field()
    provider = scrapy.Field()
    service = scrapy.Field()
    posted_on = scrapy.Field()
    scraped_on = scrapy.Field()


class ScrapersLoader(ItemLoader):
    default_input_processor = MapCompose(lambda x: x.strip())
    default_output_processor = TakeFirst()

    posted_on_in = MapCompose(lambda x: make_tz_aware(x))

    scraped_on_in = MapCompose(lambda x: x)

    details_in = clean_up_details
