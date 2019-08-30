from celery import chain, shared_task, task

from email_alerts.tasks import prepare_and_send_alerts
from scrapers.tasks import run_dcwd_spider


@task(name='dcwd-workflow')
def run_dcwd_workflow():
    dcwd_workflow = chain(
        run_dcwd_spider.s(input='inputargument', db_mode='skip'),
        prepare_and_send_alerts.s()
    )
    dcwd_workflow()
