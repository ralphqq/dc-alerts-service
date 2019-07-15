from django.shortcuts import reverse
from django.test import TestCase

from subscribers.models import Subscriber
from subscribers.utils import create_confirmation_link


class RegisterEmailViewTest(TestCase):

    def test_submit_redirects_to_landing_or_home_page(self):
        # valid post request should
        # redirect to landing page after submission
        test_email_address = 'myemail@example.com'
        response = self.client.post(
            reverse('register_new_email'),
            data={'email_address': test_email_address}
        )
        self.assertRedirects(
            response,
            reverse('confirm_email_page')
        )

        # if method is get, then redirect to home
        response = self.client.get(reverse('register_new_email'))
        self.assertRedirects(response, reverse('homepage'))


    def test_saves_inactive_new_user_to_db(self):
        test_email_address = 'anotheruser@email.com'
        response = self.client.post(
            reverse('register_new_email'),
            data={'email_address': test_email_address}
        )
        new_user = Subscriber.objects.get(email=test_email_address)

        self.assertEqual(new_user.email, test_email_address)


class ActivateUserTest(TestCase):

    def test_activation_uid_and_token(self):
        test_email_address = 'newusernow@email.com'
        response = self.client.post(
            reverse('register_new_email'),
            data={'email_address': test_email_address}
        )
        new_user = Subscriber.objects.get(email=test_email_address)
        request = response.wsgi_request

        confirmation_link = create_confirmation_link(
            request=request,
            user=new_user,
            viewname='verify_email',
            external=True
        )

        verification_response = self.client.get(confirmation_link)
        this_user = Subscriber.objects.get(email=test_email_address)
        self.assertIs(this_user.is_active, True)
        self.assertRedirects(
            verification_response,
            reverse('verification_results', kwargs={'results': 'success'})
        )


    def test_invalid_confirmation_links(self):
        address_1 = 'foo1@example.com'
        address_2 = 'foo2@example.com'

        response_1 = self.client.post(
            reverse('register_new_email'),
            data={'email_address': address_1}
        )

        new_user_1 = Subscriber.objects.get(email=address_1)
        new_user_2 = Subscriber.objects.create(email=address_2)

        request_1 = response_1.wsgi_request

        confirmation_link_1 = create_confirmation_link(
            request=request_1,
            user=new_user_2,
            viewname='verify_email',
            external=False
        )
        fake_token = '77u-31526560950be2792e58'
        fake_link = f'http://testserver/signup/verify/MQ/{fake_token}'

        verification_response = self.client.get(fake_link)
        this_user = Subscriber.objects.get(email=address_1)
        self.assertIs(this_user.is_active, False)
        self.assertRedirects(
            verification_response,
            reverse('verification_results', kwargs={'results': 'failed'})
        )
