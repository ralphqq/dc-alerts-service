from datetime import datetime

from django.test import TestCase

from notices.utils import get_datetime_from_text


class DateTimeParsingTest(TestCase):

    def test_parses_common_datetime_formats(self):
        various_texts = [
            'The scheduled outage will be on Aug 23, 2019',
            'Outage on August 24 2019',
            'The outage will be on 8/23/2019',
            'The 8-24-2019 outage schedule',
            'We set the new outage to take place on 2019-8-25',
            'Maybe at 6 am',
            'Some time around 12 AM',
            'August 24, 2019 at around 4PM',
            'Around 5:30 a.m. on August 24, 2019'
        ]

        for text in various_texts:
            self.assertIsInstance(get_datetime_from_text(text), datetime)


    def test_returns_none_for_invalid_datetime_format(self):
        various_texts = [
            'No schedule yet',
            'Feb 29, 2017',
            '3:61 PM'
        ]

        for text in various_texts:
            self.assertEqual(get_datetime_from_text(text), None)
