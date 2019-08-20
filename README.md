# dc-alerts-service
This project is a (soon-to-be-launched) web-based service that sends out email alerts about scheduled and emergency utility outages in Davao City. It's a Django port of a previous app I put together using Flask and consists of the following components:

* User management (signup, authentication, and opt-out) with Django
* Web crawling with multiple Scrapy spiders
* Asynchronous task handling through Celery and Redis
* Periodic tasks managed with Celery Beat
* Unit and integration tests done with unittest and Selenium

## Environment Variables
Make sure to specify values for the following variables in the `.env` file which is saved in the project root directory:

```
EMAIL_HOST=smtp.googlemail.com  # or some other email host used for sending emails
EMAIL_HOST_USER=example.address.42@gmail.com    # or some other email address as sender
EMAIL_HOST_PASSWORD=YOUR_EMAIL_PASSWORD_HERE
EMAIL_PORT=587
SAMPLE_RECIPIENT_EMAIL=some.other.email.address@example.com# used to populate signup fields when testing
TEST_EMAIL_HOST=smtp.mailtrap.io    # email host used for testing purposes
TEST_EMAIL_HOST_USER=GET_YOUR_OWN_USERNAME
TEST_EMAIL_HOST_PASSWORD=GET_YOUR_OWN_PASSWORD
TEST_EMAIL_PORT=2525
```

**Note:** This project uses [Mailtrap.io](https://mailtrap.io/) as fake SMTP server for testing the app's email sending capabilities.

## Running Locally
When running in local machine, make sure to follow the below steps:

1. Activate a virtual environment where the dependencies are installed
2. Define the values for the environment variables in the `.env` file (see above)
3. Run the Redis server in a terminal (I do this via a docker container)
4. Start a Celery worker in another terminal using the following command: `celery -A dcalerts worker -l INFO`
5. Start Celery Beat in yet another terminal: `celery -A dcalerts beat -l INFO`
6. Spin up the Django development server

## Testing
Before carrying out the unit and integration tests, make sure to start the Redis server and stop any running Celery workers.
Also, the tests under the `email_alerts` directory sometimes raise `django.db.utils.OperationalError`. This is most likely because SQLite [ignores the timeout parameter](https://stackoverflow.com/questions/46831783/django-sqlite3-timeout-has-no-effect) when using the shared cache. In case you encounter this, just re-run the tests or restart the Redis server before re-running the tests.

## License
[MIT license](https://opensource.org/licenses/MIT)