import logging

from celery import chain, shared_task, task

from email_alerts.tasks import prepare_and_send_alerts
from scrapers.tasks import run_dcwd_spider


@task(name='dcwd-workflow')
def run_dcwd_workflow(**kwargs):
    """Starts the workflow for DCWD, from scraiping to sending alerts.

    The parameters passed with kwargs are passed as arguments to the 
    crawler task. An example is:

        run_dcwd_workflow(input='inputargument', db_mode='skip')

    which tells the spider not to save the scraped items to the db.
    See scrapers.tasks.run_dcwd_spider() for details.

    Returns:
        bool: False if if an unexpected error occurred in a sub-task or 
            no new notices were successfully processed; True otherwise.
    """
    try:
        dcwd_workflow = chain(
            run_dcwd_spider.s(**kwargs),
            prepare_and_send_alerts.s()
        )
        logging.info('Starting DCWD workflow')
        dcwd_workflow()
    except Exception as e:
        logging.error(f'DCWD Workflow: {e}')
        return False
    logging.info('Completed DCWD workflow')
    return True
