from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.shortcuts import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from subscribers.tokens import account_activation_token


def create_secure_link(request=None, user=None, viewname='', external=True):
    """Generates a one-time URL that identifies a user.

    The resulting URL can then be used as confirmation links or 
    unsubscribe links.

    Args:
        request (Request object): needed to obtain the current scheme,
            domain, and port for building the link. If no request obj 
            is passed, the values for these URL components are 
            obtained from the settings file.
        user (Subscriber object): the subscriber whose primary key 
            will be encoded as a base64 UID in the returned URL
        viewname (str): the name of the view which the URL points to 
        external (bool): if True, pre-appends the scheme and netloc to 
            the path. Otherwise, only the path component is returned.
    """
    url_path = reverse(
        viewname,
        kwargs = {
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user)
        }
    )
    if external:
        # pre-append protocol and domain
        url_scheme = ''
        url_host = ''
        if request is not None:
            url_scheme = request.scheme
            url_host = request.get_host()
        else:
            url_scheme = settings.EXTERNAL_URL_SCHEME
            url_host = settings.EXTERNAL_URL_HOST

        url_path = f'{url_scheme}://{url_host}{url_path}'

    return url_path


def get_uid(uidb64):
    """Converts the base64-encoded UID into a string."""
    return force_text(urlsafe_base64_decode(uidb64))


def get_external_link_for_static_file(fpath=''):
    """Generates the absolute URL to a static asset.

    Args:
        fpath (str): the path to the file, relative to static directory
    """
    url_path = static(fpath)
    url_scheme = settings.EXTERNAL_URL_SCHEME
    url_host = settings.EXTERNAL_URL_HOST
    return f'{url_scheme}://{url_host}{url_path}'
