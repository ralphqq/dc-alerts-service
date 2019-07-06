from django.shortcuts import redirect, render, reverse
from django.views import View

from subscribers.models import Subscriber


class RegisterEmailView(View):

    def post(self, request):
        email = request.POST['email_address']
        new_user = Subscriber.objects.create(email=email.strip())
        return redirect(reverse('confirm_email_page'))


    def get(self, request):
        return redirect(reverse('homepage'))


class ConfirmEmailPageView(View):

    def get(self, request):
        return render(request, 'subscribers/confirm_email.html')
