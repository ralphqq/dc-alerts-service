# -*- coding: utf-8 -*-
import logging

from django.db import IntegrityError

from notices.models import OutageNotice


class ScrapersPipeline(object):
    def process_item(self, item, spider):
        if spider.db_mode == 'skip':
            logging.log(logging.INFO, 'Skipped: Item not saved to db')
        elif spider.db_mode == 'save':
            try:
                notice = OutageNotice(
                    urgency=item['urgency'],
                    source_url=item['source_url'],
                    headline=item['headline'],
                    details=item['details'],
        provider=item['provider'],
        service=item['service'],
        posted_on=item['posted_on']
                )

                if notice.provider == 'DCWD':
                    notice.notice_id = item['notice_id']
                else:
                    notice.set_notice_id()

                notice.save()
                logging.log(logging.INFO, f'Saved new {notice.provider} notice')
            except IntegrityError as e:
                logging.log(logging.INFO, e)

        return item
