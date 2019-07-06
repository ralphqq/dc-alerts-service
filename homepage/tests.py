from django.shortcuts import reverse
from django.test import TestCase


class HomePageTest(TestCase):

    def test_homepage_returns_correct_html(self):
        response = self.client.get(reverse('homepage'))
        self.assertTemplateUsed(response, 'homepage/index.html')
