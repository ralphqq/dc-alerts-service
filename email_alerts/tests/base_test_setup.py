from celery.contrib.testing.worker import start_worker
from django.shortcuts import reverse
from django.test import SimpleTestCase, TestCase, TransactionTestCase

from dcalerts.celery import app
from subscribers.models import Subscriber


class EmailTestCase(TransactionTestCase):
    allow_database_queries = True


    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Start up celery worker
        app.loader.import_module('celery.contrib.testing.tasks')
        cls.celery_worker = start_worker(app)
        cls.celery_worker.__enter__()


    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        # Close worker
        cls.celery_worker.__exit__(None, None, None)


    def create_user_and_request(self, email='foo@example.com'):
        """Helper function to create User and request object."""
        # Create user
        user = Subscriber.objects.create(email=email)

        # Get a request object
        response = self.client.get(reverse('homepage'))  # Could be any view
        request = response.wsgi_request

        return user, request


    