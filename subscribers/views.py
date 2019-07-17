from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse
from django.views import View
from django.utils.decorators import method_decorator

from subscribers.decorators import is_from_referrer
from subscribers.models import Subscriber


class RegisterEmailView(View):

    def post(self, request):
        email = request.POST['email_address']
        new_user = Subscriber.objects.create(email=email.strip())
        confirmation_email = new_user.create_and_send_confirmation_email(
            request
        )
        confirmation_email.save()

        request.session['prev_view'] = 'register_new_email'
        request.session['new_user_email'] = email.strip()
        return redirect(reverse('confirm_email_page'))


    def get(self, request):
        return redirect(reverse('homepage'))


@method_decorator(is_from_referrer('register_new_email', ), name='dispatch')
class ConfirmEmailPageView(View):

    def get(self, request):
        new_user_email = request.session.get('new_user_email')

        if new_user_email is not None:
            del request.session['new_user_email']

        return render(request, 
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

            welcome_email = user.create_and_send_welcome_email()
            welcome_email.save()

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
        return HttpResponse('Hey!')
