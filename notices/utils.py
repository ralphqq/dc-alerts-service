from datetime import datetime
import re

from dateutil import parser
from django.conf import settings
import pytz


calendar_date_re = re.compile(
    r'((Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?'
    r'|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?'
    r'|Dec(?:ember)?)\s+(\d{1,2},?)\s+(\d{4}))|(\d{1,2}(-|/)\d{1,2}(-|/)\d{4})'
    r'|(\d{4}-\d{1,2}-\d{1,2})'
)

time_re = re.compile(r'\d{1,2}(:\d{2})?(\s+)?([AaPp]\.?(\s+)?[Mm]\.?)')


def get_datetime_from_text(text):
    """Extracts date from text and returns it as tz-aware datetime obj."""
    date_match = calendar_date_re.search(text)
    time_match = time_re.search(text)

    if date_match is not None or time_match is not None:
        # Components of valid datetime string
        date_str = ''
        time_str = ''

        # In either case below,
        # only first occurrence of matched string is obtained
        if date_match is not None:
            date_str = date_match.group(0)
        if time_match is not None:
            time_str = time_match.group(0)

        # Create valid datetime string
        valid_datetime_str = ' '.join([date_str, time_str])

        try:
            # Parse valid datetime string
            naive_dt = parser.parse(valid_datetime_str)
        except ValueError:
            pass
        else:
            # Make object timezone-aware
            aware_dt = pytz.timezone(settings.TIME_ZONE).localize(naive_dt)

            # Return as UTC timezone
            return aware_dt.astimezone(pytz.UTC)

    return None


def datetime_as_str(obj):
    """Gets the str representation of a datetime obj.

    This function is passed as part of the `default` 
    parameter in some calls to json.loads()
    """
    if isinstance(obj, datetime):
        return obj.__str__()
