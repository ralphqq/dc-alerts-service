from unittest import skip
from unittest.mock import patch

from django.core.exceptions import PermissionDenied
from django.shortcuts import reverse
from django.test import TestCase

from subscribers.forms import OptOutRequestForm
from subscribers.models import Subscriber
from subscribers.utils import create_secure_link
from subscribers.views import BAD_SIGNUP_ERROR_MSG


class RegisterEmailViewTest(TestCase):

    def test_submit_redirects_to_landing_or_home_page(self):
        # valid post request should
        # redirect to landing page after submission
        test_email_address = 'myemail@example.com'
        response = self.client.post(
            reverse('register_new_email'),
            data={'email': test_email_address}
        )

        self.assertRedirects(
            response,
            reverse('confirm_email_page')
        )

        # Also, make sure that prev_view item is deleted in landing page
        with self.assertRaises(KeyError):
            self.client.session['prev_view']

        # if method is get, then redirect to home
        response = self.client.get(reverse('register_new_email'))
        self.assertRedirects(response, reverse('homepage'))

        
    def test_saves_inactive_new_user_to_db(self):
        test_email_address = 'anotheruser@email.com'
        response = self.client.post(
            reverse('register_new_email'),
            data={'email': test_email_address}
        )
        new_user = Subscriber.objects.get(email=test_email_address)
        active_users = Subscriber.get_all_active_subscribers()

        self.assertEqual(new_user.email, test_email_address)
        self.assertIs(new_user.is_active, False)
        self.assertEqual(active_users.count(), 0)

    @patch('subscribers.models.Subscriber.send_transactional_email')
    def test_confirm_email_sent_only_to_new_or_inactive_user(self, mock_send):
        new_user_email_address = 'newuser@examplemail.com'
        inactive_user = Subscriber.objects.create(email='inact@supermail.com')
        active_user = Subscriber.objects.create(
            email='act@xyz.com',
            is_active=True
        )

        # Register the new user
        self.client.post(
            reverse('register_new_email'),
            data={'email': new_user_email_address}
        )
        self.assertEqual(mock_send.called, True)

        # Try to re-register an inactive user
        mock_send.called = False    # To check if request will make it True
        self.client.post(
            reverse('register_new_email'),
            data={'email': inactive_user.email}
        )
        self.assertEqual(mock_send.called, True)

        # Try to register an active user
        mock_send.called = False
        self.client.post(
            reverse('register_new_email'),
            data={'email': active_user.email}
        )
        self.assertEqual(mock_send.called, False)

    @patch('django.contrib.messages.error')
    def test_bad_signup_sends_error_message(self, msg_error):
        active_user = Subscriber.objects.create(
            email='a1@dcd.com',
            is_active=True
        )

        # Register an already active user
        self.client.post(
            reverse('register_new_email'),
            data={'email': active_user.email}
        )

        (request, msg), _ = msg_error.call_args
        self.assertEqual(msg_error.called, True)
        self.assertEqual(BAD_SIGNUP_ERROR_MSG, msg)


class ConfirmEmailPageViewTest(TestCase):

    def test_restricts_if_not_from_referrer(self):
        response = self.client.get(reverse('confirm_email_page'))
        session = self.client.session

        with self.assertRaises(KeyError):
            session['prev_view']

        self.assertEqual(response.status_code, 403)


class ActivateUserTest(TestCase):

    def test_activation_uid_and_token(self):
        test_email_address = 'newusernow@email.com'
        response = self.client.post(
            reverse('register_new_email'),
            data={'email': test_email_address}
        )
        new_user = Subscriber.objects.get(email=test_email_address)
        request = response.wsgi_request

        confirmation_link = create_secure_link(
            request=request,
            user=new_user,
            viewname='verify_email',
            external=True
        )

        verification_response = self.client.get(confirmation_link)
        this_user = Subscriber.objects.get(email=test_email_address)
        active_users = Subscriber.get_all_active_subscribers()

        self.assertIs(this_user.is_active, True)
        self.assertRedirects(
            verification_response,
            reverse('verification_results', kwargs={'results': 'success'})
        )
        self.assertEqual(active_users.count(), 1)


    def test_invalid_confirmation_links(self):
        address_1 = 'foo1@example.com'
        address_2 = 'foo2@example.com'

        response_1 = self.client.post(
            reverse('register_new_email'),
            data={'email': address_1}
        )

        new_user_1 = Subscriber.objects.get(email=address_1)
        new_user_2 = Subscriber.objects.create(email=address_2)

        request_1 = response_1.wsgi_request

        confirmation_link_1 = create_secure_link(
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


class VerificationResultsPageViewTest(TestCase):

    def test_restricts_results_page_if_not_from_referrer(self):
        for res in ['success', 'failed']:
            response = self.client.get(
                reverse(
                    'verification_results',
                    kwargs={'results': res})
            )
            session = self.client.session

            with self.assertRaises(KeyError):
                session['prev_view']

            self.assertEqual(response.status_code, 403)


class UnsubscribeUserViewTest(TestCase):

    def test_user_opt_out_flow(self):
        # Create confirmed user
        test_email_address = 'foo@xmail.com'
        user = Subscriber.objects.create(email=test_email_address)
        user.is_active = True
        user.save()

        # Get a request object
        response = self.client.get(reverse('homepage')) # Could be any view
        request = response.wsgi_request

        # Create an opt out URL
        unsubscribe_link = create_secure_link(
            request=request,
            user=user,
            viewname='unsubscribe_user',
            external=True
        )

        # Unsubscribe the user
        response_unsub = self.client.get(unsubscribe_link)

        # Check the user object
        this_user = Subscriber.objects.get(email=test_email_address)
        active_users = Subscriber.get_all_active_subscribers()

        self.assertIs(this_user.is_active, False)
        self.assertEqual(active_users.count(), 0)

        # Redirect to successful opt out page
        self.assertRedirects(
            response_unsub,
            reverse('unsubscribe_results', kwargs={'results': 'success'})
        )

        # Check if prev_vew is deleted
        session = self.client.session
        with self.assertRaises(KeyError):
            session['prev_view']


class UnsubscribeUserPageViewTest(TestCase):

    def test_optout_request_page_shows_correct_form(self):
        response = self.client.get(reverse('optout_request'))
        self.assertIsInstance(response.context['form'], OptOutRequestForm)

    @patch('subscribers.models.Subscriber.send_transactional_email')
    def test_request_allowed_only_for_active_user(self, mock_send_optout):
        active_user = Subscriber.objects.create(email='email1@gmail.com', is_active=True)
        inactive_user = Subscriber.objects.create(email='email2@gmail.com')

        # The below request will end up calling the patched function
        response = self.client.post(
            reverse('optout_request'),
            data={'email': active_user.email}
        )

        # ... which makes the `called` variable True
        self.assertEqual(mock_send_optout.called, True)

        # Reassign back to original value
        mock_send_optout.called = False

        # The below request will not call the patched function
        response = self.client.post(
            reverse('optout_request'),
            data={'email': inactive_user.email}
        )

        # ... leaving the `called` variable unchanged
        self.assertEqual(mock_send_optout.called, False)


    def test_blocks_if_not_from_referrer(self):
        for res in ['success', 'failed']:
            response = self.client.get(
                reverse(
                    'unsubscribe_results',
                    kwargs={'results': res})
            )
            session = self.client.session

            with self.assertRaises(KeyError):
                session['prev_view']

            self.assertEqual(response.status_code, 403)
