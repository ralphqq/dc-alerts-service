from django.utils import timezone

from notices.models import OutageNotice
from scrapers.scrapers.items import ScrapersItem, ScrapersLoader
from scrapers.scrapers.pipelines import ScrapersPipeline
from scrapers.scrapers.spiders.dcwd import DcwdSpider
from scrapers.tests.base_scraper_test_setup import ScraperTestCase, html_files
from scrapers.tests.utils import make_response_object, make_fake_id

dcwd_details_file = 'scrapers/tests/html/dcwd_details.html'

class ScrapersPipelineTests(ScraperTestCase):

    def setUp(self):
        self.spider = DcwdSpider(limit=1)


    def test_scrapers_pipeline_saves_items_to_db(self):
        """Tests if default item pipeline saves to db."""
        # Get results from parse_page
        valid_results = self.get_parse_results(
            parse_method_name='parse_page',
            response=make_response_object(
                filepath=html_files['dcwd_details'],
                meta={'urgency': 'a', 'title': 'Some Title',
                      'notice_id': make_fake_id()}
            )
        )        
        item_count = len(valid_results)
        item_pipeline = ScrapersPipeline()
        for item in valid_results:
            item_pipeline.process_item(item, self.spider)

        self.assertEqual(item_count, OutageNotice.objects.count())
