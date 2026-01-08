"""Unit tests for database access helpers"""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from backend.data.image import ImageGeneratorJobData
from backend.data.s3 import S3Data
from backend.database.image.image_generator_db import ImageGeneratorDB
from backend.enum.image import ImageTypeEnum
from backend.enum.s3 import S3ContentTypeEnum


@pytest.mark.unit
class TestImageGeneratorDB:
    """Test cases for ImageGeneratorDB"""

    def test_get_by_task_id(self) -> None:
        """Return ImageGeneratorJobData rows matching task id"""
        task_id = uuid4()
        job_id = uuid4()
        s3_data = S3Data(
            name="image.png",
            content_type=S3ContentTypeEnum.PNG,
            key="campaign",
        )
        job_data = ImageGeneratorJobData(
            id=job_id,
            name="Test Image",
            prompt="test prompt",
            image_type=ImageTypeEnum.YouTube,
            task_id=task_id,
            data=s3_data,
        )

        db = ImageGeneratorDB()
        db.db_manager = MagicMock()
        db.db_manager.query_items.return_value = [job_data.to_json()]

        result = db.get_by_task_id(str(task_id))

        assert len(result) == 1
        assert result[0].id == job_id
        assert result[0].task_id == task_id
        assert result[0].data.name == "image.png"
        assert db.db_manager.query_items.called
