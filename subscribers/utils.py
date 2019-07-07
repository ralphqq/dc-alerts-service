from django.shortcuts import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from subscribers.tokens import account_activation_token


def create_confirmation_link(request, user, viewname, external=True):
    url_path = reverse(
        viewname,
        kwargs = {
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user)
        }
    )
    if external:
        # pre-append protocol and domain
        url_path = f'{request.scheme}://{request.get_host()}{url_path}'

    return url_path

def get_uid(uidb64):
    return force_text(urlsafe_base64_decode(uidb64))
