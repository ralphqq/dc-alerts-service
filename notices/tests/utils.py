from datetime import timedelta

from django.utils import timezone


def create_fake_details(date_offset=None, **kwargs):
    """Generates fake outage details dictionary for a notice.

    Args:
        date_offset (int): number of days added to current day

    Additional dictionary fields and values are passed as kwargs.
    Values to overwrite defaults for fields 'set_n', 'when', 
    'where', and 'why' are also passed as kwargs.
    """
    outage_date = timezone.now()
    if date_offset is not None:
        outage_date += timedelta(days=date_offset)

    details_for_set = {
        'set_n': 'SET 1',
        'when': outage_date.strftime('%B %d, %Y %H:%M'),
        'where': 'Somewhere',
        'why': 'Routine maintenance'
    }

    if kwargs:
        # Additional fields in dict
        # Or values to overwrite defaults
        for k, v in kwargs.items():
            details_for_set[k] = v

    return details_for_set
