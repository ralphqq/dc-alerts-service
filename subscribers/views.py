from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse
from django.views import View

from email_alerts.models import TransactionalEmail
from email_alerts.utils import send_email
from subscribers.models import Subscriber
from subscribers.tokens import account_activation_token
from subscribers.utils import create_confirmation_link, get_uid


class RegisterEmailView(View):

    def post(self, request):
        email = request.POST['email_address']
        new_user = Subscriber.objects.create(email=email.strip())

        confirmation_link = create_confirmation_link(
            request=request,
            user=new_user,
            viewname='verify_email',
            external=True
        )

        confirmation_email = TransactionalEmail.objects.create(
            recipient=new_user,
            subject_line='Please confirm your email address'
        )

        send_email(
            email_object=confirmation_email,
            email_template='email_alerts/confirmation_email.html',
            context={'confirmation_link': confirmation_link}
        )
        confirmation_email.save()

        return redirect(reverse('confirm_email_page'))


    def get(self, request):
        return redirect(reverse('homepage'))


class ConfirmEmailPageView(View):

    def get(self, request):
        return render(request, 'subscribers/confirm_email.html')


class VerifyEmailView(View):

    def get(self, request, uid, token):
        try:
            uid_from_url = get_uid(uid)
            user = Subscriber.objects.get(pk=uid_from_url)
        except (TypeError, ValueError, OverflowError, Subscriber.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return HttpResponse('Success')

        else:
            return HttpResponse('Failed')
