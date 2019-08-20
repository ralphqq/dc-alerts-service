from celery.contrib.testing.worker import start_worker
from django.test import SimpleTestCase, TestCase, TransactionTestCase

from dcalerts.celery import app


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
