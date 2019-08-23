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

        item_pipeline = ScrapersPipeline()
        for item in valid_results:
            item_pipeline.process_item(item, self.spider)

        # Test if at least one item was saved to db
        self.assertGreater(OutageNotice.objects.count(), 0)


    def test_discards_items_with_duplicate_notice_id(self):
        """Test if pipeline  does not save duplicate items."""
        valid_results = self.get_parse_results(
            parse_method_name='parse_page',
            response=make_response_object(
                filepath=html_files['dcwd_details'],
                meta={'urgency': 'a', 'title': 'Some Title',
                      'notice_id': make_fake_id()}
            )
        )        

        # Append existing item into list to simulate duplication
        valid_results.append(valid_results[0])

        # Get length of list with duplicate
        item_count = len(valid_results)

        item_pipeline = ScrapersPipeline()
        for item in valid_results:
            item_pipeline.process_item(item, self.spider)

        # Test if one or more items were not saved to db
        self.assertLess(OutageNotice.objects.count(), item_count)


    def test_db_mode_skip_flag(self):
        """Test if pipeline  obeys db_mode='skip' flag."""
        # Set aside original spider
        orig_spider = self.spider

        # Create new spider with db_mode set to 'skip'
        self.spider = DcwdSpider(db_mode='skip', limit=1)
        self.assertEqual(self.spider.db_mode, 'skip')

        valid_results = self.get_parse_results(
            parse_method_name='parse_page',
            response=make_response_object(
                filepath=html_files['dcwd_details'],
                meta={'urgency': 'a', 'title': 'Some Title',
                      'notice_id': make_fake_id()}
            )
        )        

        item_pipeline = ScrapersPipeline()
        for item in valid_results:
            item_pipeline.process_item(item, self.spider)

        self.assertEqual(OutageNotice.objects.count(), 0)

        # Re-assign original spider back to self.spider (some sort of cleanup)
        self.spider = orig_spider
