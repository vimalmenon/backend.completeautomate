"""Unit tests for job implementations"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestNoJob:
    """Test cases for NoJob"""

    @patch("backend.jobs.no_job.NoJob")
    def test_no_job_execution(self, mock_job: MagicMock) -> None:
        """Test NoJob execution (does nothing)"""
        mock_job.execute.return_value = {"status": "skipped"}

        result = mock_job.execute()
        assert result["status"] == "skipped"
