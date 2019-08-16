# dc-alerts-service
This project is a (soon-to-be-launched) web service that sends out email alerts about scheduled and emergency utility outages in Davao City. It's a Django port of a previous app I put together using Flask and consists of the following components:
* User management (signup, authentication, and opt-out) with Django
* Web crawling with multiple Scrapy spiders
* Asynchronous task handling through Celery and Redis
* Periodic tasks managed with Celery Beat
* Unit and functional tests done with unittest and Selenium

## Update
This project is currently a work-in-progress.

## License
[MIT license](https://opensource.org/licenses/MIT)