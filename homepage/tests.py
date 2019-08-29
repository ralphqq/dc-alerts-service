from django.shortcuts import reverse
from django.test import TestCase

from subscribers.forms import SignupForm


class HomePageTest(TestCase):

    def test_homepage_returns_correct_html(self):
        response = self.client.get(reverse('homepage'))
        self.assertTemplateUsed(response, 'homepage/index.html')


    def test_homepage_uses_signup_form(self):
        response = self.client.get(reverse('homepage'))
        self.assertIsInstance(response.context['form'], SignupForm)
