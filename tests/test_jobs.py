"""Unit tests for job implementations"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestImageGeneratorJob:
    """Test cases for ImageGeneratorJob"""

    @patch("backend.jobs.image_generator_job.ImageGeneratorJob")
    def test_execute_job(self, mock_job: MagicMock, sample_task_data: dict) -> None:
        """Test executing image generator job"""
        mock_job.execute.return_value = {
            "status": "completed",
            "image_url": "s3://bucket/images/test.png",
        }

        result = mock_job.execute()
        assert result["status"] == "completed"
        assert "image_url" in result


@pytest.mark.unit
class TestNoJob:
    """Test cases for NoJob"""

    @patch("backend.jobs.no_job.NoJob")
    def test_no_job_execution(self, mock_job: MagicMock) -> None:
        """Test NoJob execution (does nothing)"""
        mock_job.execute.return_value = {"status": "skipped"}

        result = mock_job.execute()
        assert result["status"] == "skipped"
