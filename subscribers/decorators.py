import functools

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, reverse


def is_from_referrer(referrer_name, redirect_name=None):
    """Checks if request comes from a specified view.

    If not, redirects to another specified view. Or, if no 
    redirect view is given, raises a PermissionDenied exception.

    Args:
        referrer_name (str): the name of the referring view
        redirect_name (str): the name of the view to redirect
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            prev_view = request.session.get('prev_view')
            if prev_view is None:
                raise PermissionDenied('')

            if prev_view == referrer_name:
                return func(request, *args, **kwargs)

            if redirect_name is not None:
                return redirect(reverse(redirect_name))
            else:
                raise PermissionDenied

        return wrapper

    return decorator
