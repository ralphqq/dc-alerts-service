from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse
from django.views import View
from django.utils.decorators import method_decorator

from subscribers.decorators import is_from_referrer
from subscribers.forms import (
    InactiveSubscriberFound,
    OptOutRequestForm,
    SignupForm
)
from subscribers.models import Subscriber


BAD_SIGNUP_ERROR_MSG = 'Cannot register the email you entered'


class RegisterEmailView(View):

    def post(self, request):
        user = None
        try:
            form = SignupForm(request.POST)
            if form.is_valid():
                user = form.save()
        except IntegrityError:
            user = None
        except InactiveSubscriberFound:
            user = Subscriber.objects.get(email=form.instance.email)

        if user is None:
            messages.error(request, BAD_SIGNUP_ERROR_MSG)
            return redirect(reverse('homepage'))

        confirmation_email = user.create_and_send_confirmation_email(request)
        request.session['prev_view'] = 'register_new_email'
        request.session['new_user_email'] = user.email
        return redirect(reverse('confirm_email_page'))


    def get(self, request):
        return redirect(reverse('homepage'))


@method_decorator(is_from_referrer('register_new_email', ), name='dispatch')
class ConfirmEmailPageView(View):

    def get(self, request):
        new_user_email = request.session.get('new_user_email')

        if new_user_email is not None:
            del request.session['new_user_email']

        return render(
            request, 
            'subscribers/confirm_email.html',
            {'new_user_email': new_user_email}
        )


class VerifyEmailView(View):

    def get(self, request, uid, token):
        request.session['prev_view'] = 'verify_email'
        user = Subscriber.verify_secure_link(uid, token)

        if user is not None:
            user.is_active = True
            user.save()

            welcome_email = user.create_and_send_welcome_email(request)
            return redirect(reverse(
                'verification_results',
                kwargs={'results': 'success'}
            ))

        else:
            return redirect(reverse(
                'verification_results',
                kwargs={'results': 'failed'}
            ))


@method_decorator(is_from_referrer('verify_email'), name='dispatch')
class VerificationResultsPageView(View):

    def get(self, request, results):
        if results == 'success' or results == 'failed':
            return render(
                request,
                'subscribers/verification_results_page.html',
                {'results': results}
            )


class UnsubscribeUserView(View):

    def get(self, request, uid, token):
        request.session['prev_view'] = 'unsubscribe_user'
        user = Subscriber.verify_secure_link(uid, token)

        if user is not None:
            user.is_active = False
            user.save()

            goodbye_email = user.create_and_send_goodbye_email(request)
            return redirect(reverse(
                'unsubscribe_results',
                kwargs={'results': 'success'}
            ))

        else:
            return redirect(reverse(
                'unsubscribe_results',
                kwargs={'results': 'failed'}
            ))


@method_decorator(is_from_referrer('unsubscribe_user'), name='dispatch')
class UnsubscribeResultsPageView(View ):

    def get(self, request, results):
        if results == 'success' or results == 'failed':
            return render(
                request,
                'subscribers/unsubscribe_results_page.html',
                {'results': results}
            )


class OptOutRequestPageView(View):

    def get(self, request):
        return render(
            request,
            'subscribers/optout_request.html',
            {'form': OptOutRequestForm()}
        )


    def post(self, request):
        user = None
        try:
            form = OptOutRequestForm(request.POST)
            if form.is_valid():
                user = Subscriber.objects.get(email=form.cleaned_data['email'])
        except Subscriber.DoesNotExist:
            user = None

        if user is not None and user.is_active:
            # Create and send optout email only to existing active user
            optout_email = user.create_and_send_optout_email(request)

        # Show same instructions to existing and non-existing users 
        # to avoid guessing registered email addresses
        request.session['prev_view'] = 'optout_request'
        request.session['submitted_email'] = form.data.get('email')
        return redirect(reverse('optout_instructions'))


@method_decorator(is_from_referrer('optout_request'), name='dispatch')
class OptOutInstructionsPageView(View):

    def get(self, request):
        email_address = request.session.get('submitted_email')
        if email_address is not None:
            del request.session['submitted_email']

        return render(
            request,
            'subscribers/optout_instructions.html',
            {'email_address': email_address}
        )
