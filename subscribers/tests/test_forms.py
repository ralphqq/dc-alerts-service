from django.db import IntegrityError
from django.test import TestCase

from subscribers.forms import (
    BLANK_ITEM_ERROR_MSG,
    EMAIL_INPUT_PLACEHOLDER,
    InactiveSubscriberFound,
    SignupForm
)
from subscribers.models import Subscriber


class SignupFormTest(TestCase):

    def test_has_placeholder_and_bootstrap_class(self):
        form = SignupForm()
        self.assertIn(
            f'placeholder="{EMAIL_INPUT_PLACEHOLDER}"',
            form.as_p()
        )
        self.assertIn('class="form-control input-lg"', form.as_p())


    def test_form_validation_for_blank_items(self):
        form = SignupForm(data={'email': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['email'],
            [BLANK_ITEM_ERROR_MSG]
        )


    def test_if_form_rejects_invalid_email_address_format(self):
        form = SignupForm(data={'email': 'adfdhadk'})
        self.assertFalse(form.is_valid())


    def test_form_save_handles_saving_to_db(self):
        user_email = 'user1@example.com'
        form = SignupForm(data={'email': user_email})
        new_user = form.save()
        self.assertEqual(new_user, Subscriber.objects.get(email=user_email))
        self.assertEqual(new_user.email, user_email)


    def test_handles_inactive_user_signup(self):
        user_email = 'user23@gmail.com'
        inactive_user = Subscriber.objects.create(email=user_email)
        self.assertEqual(inactive_user.is_active, False)

        form = SignupForm(data={'email': user_email})
        self.assertTrue(form.is_valid())
        with self.assertRaises(InactiveSubscriberFound):
            form.save()


    def test_rejects_duplicate_signup_for_active_user(self):
        user_email = 'user42@gmail.com'
        active_user = Subscriber.objects.create(email=user_email, is_active=True)
        self.assertEqual(active_user.is_active, True)

        form = SignupForm(data={'email': user_email})
        self.assertTrue(form.is_valid())
        with self.assertRaises(IntegrityError):
            form.save()
