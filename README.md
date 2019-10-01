# dc-alerts-service
This project is a (soon-to-be-launched) web-based service that sends out email alerts about scheduled and emergency utility outages in Davao City. It's a Django port of a previous app I put together using Flask and consists of the following components:

* User management (signup, authentication, and opt-out) with Django
* Web crawling with multiple Scrapy spiders
* Asynchronous task handling through Celery and Redis
* Periodic background tasks managed with Celery Beat
* Unit and integration tests done with unittest and Selenium, along with QUnit for JavaScript/jQuery code

## Environment Variables
Make sure to supply the appropriate values for the following variables in the `.env` file which is saved in the project root directory:

* `DB_USERNAME`: the PostgreSQL username that owns the database used
* `DB_PASSWORD`: the password corresponding to `DB_USERNAME`
* `DB_NAME`: the name of the PostgreSQL database used as backend
* `DB_PORT`: the database port (set this to 5432)
* `EMAIL_HOST`: host used for sending emails (example: `'smtp.googlemail.com'`)
* `EMAIL_HOST_USER`: the sending email address
* `EMAIL_HOST_PASSWORD`: password used for the `EMAIL_HOST_PASSWORD` account
* `EMAIL_PORT`: for Gmail, this is 587
* `SAMPLE_RECIPIENT_EMAIL`: email address used to populate signup fields when testing
* `TEST_EMAIL_HOST`: Mailtrap email host used for testing purposes (`'smtp.mailtrap.io'`)
* `TEST_EMAIL_HOST_USER`: host username provided by Mailtrap
* `TEST_EMAIL_HOST_PASSWORD`: host password provided by Mailtrap
* `TEST_EMAIL_PORT`: port used in email testing provided by Mailtrap (most likely `'2525'`)

**Note:** This project uses [Mailtrap.io](https://mailtrap.io/) as fake SMTP server for testing the app's email sending capabilities.

## Running Locally
When running on local machine, make sure to follow the below steps:

1. Activate a virtual environment where the dependencies are installed
2. Define the values for the environment variables in the `.env` file (see above)
3. Make sure PostgreSQL engine is running
4. Run the Redis server in a terminal (I do this via a docker container)
5. Start a Celery worker in another terminal using the following command: `celery -A dcalerts worker -l INFO`
6. Start Celery Beat in yet another terminal: `celery -A dcalerts beat -l INFO`
7. Spin up the Django development server

## Testing
To test everything under the website's Django and Celery stack:
```
$ python manage.py test
```

To exclude functional tests:
```
$ python manage.py test --exclude-tag=slow
```

To run only the functional tests:
```
$ python manage.py test func_tests
```

To run the JavaScript/jQuery unit tests, open the file `homepage/static/js/tests/test.html` in a browser.

**Notes:**

* Before carrying out the unit and integration tests, make sure to start the Redis server and stop any running Celery workers.
* Also, the tests under the `email_alerts` directory sometimes raise `django.db.utils.OperationalError`. This is most likely because SQLite [ignores the timeout parameter](https://stackoverflow.com/questions/46831783/django-sqlite3-timeout-has-no-effect) when using the shared cache. In case you encounter this, just re-run the tests or restart the Redis server before re-running the tests.
* However, this problem does not occur with PostgreSQL as the database.

## License
[MIT license](https://opensource.org/licenses/MIT)