from django.test import TransactionTestCase
from scrapy.selector import Selector

from scrapers.tests.utils import make_response_object

# Paths to HTML test files
html_files = {
    'dcwd_index': 'scrapers/tests/html/dcwd_index.html',
    'dcwd_details': 'scrapers/tests/html/dcwd_details.html',
}


class ScraperTestCase(TransactionTestCase):

    def setUp(self):
        self.spider = None


    def get_parse_results(self, parse_method_name='parse', response=None):
        """Gets the objects yielded by a parse method.

        The parse method to be evaluated must yield a generator 
        instead of returning a value.

        Args:
            parse_method_name (str): name of the parse method to be 
                evaluated
            response (Response object): response object passed as parameter of 
                the given parse method

        Returns:
            list: a list of yielded objects
        """
        parse_method = getattr(self.spider, parse_method_name)
        raw_results = parse_method(response)
        return list(raw_results)
