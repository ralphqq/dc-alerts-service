from unittest import skip
from unittest.mock import patch

from django.test import TestCase

from notices.models import OutageNotice
from notices.tasks import run_dcwd_workflow


class ChainAndWorkFlowTests(TestCase, ):

    @patch('notices.tasks.chain')
    @patch('notices.tasks.prepare_and_send_alerts')
    @patch('notices.tasks.run_dcwd_spider')
    def test_dcwd_workflow(
            self,
            mock_dcwd_crawl,
            mock_dcwd_alerts,
            mock_dcwd_workflow
        ):
        result= run_dcwd_workflow()
        mock_dcwd_workflow.assert_called_once_with(
            mock_dcwd_crawl.s(),
            mock_dcwd_alerts.s()
        )
        self.assertEqual(result, True)

    @patch('notices.tasks.chain')
    def test_error_in_a_task_returns_false(self, mock_dcwd_workflow):
        mock_dcwd_workflow.side_effect = ValueError('An intentional error occurred')
        result = run_dcwd_workflow()
        self.assertEqual(result, False)
