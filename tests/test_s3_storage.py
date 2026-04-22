"""Unit tests for S3Storage"""

import pytest

from backend.data.s3 import S3Data
from backend.enum.s3 import S3ContentTypeEnum
from backend.exception import AppException
from backend.integration.storage.s3_storage import S3Storage


@pytest.mark.unit
class TestS3Storage:
    """Test cases for S3Storage class"""

    def test_upload_bytes_data(self, s3_client) -> None:
        """Test uploading byte data to S3"""
        storage = S3Storage()
        storage.bucket_name = "test-bucket"
        storage.s3_client = s3_client

        s3_data = S3Data(
            name="file.png",
            content_type=S3ContentTypeEnum.PNG,
        )

        result = storage.upload_data(s3_data, b"test content")
        assert result is True

    def test_upload_string_data(self, s3_client) -> None:
        """Test uploading string data to S3"""
        storage = S3Storage()
        storage.bucket_name = "test-bucket"
        storage.s3_client = s3_client

        s3_data = S3Data(
            name="data.json",
            content_type=S3ContentTypeEnum.JSON,
        )

        result = storage.upload_data(s3_data, "test string content")
        assert result is True

    def test_get_bytes(self, s3_client) -> None:
        """Test retrieving byte data from S3"""
        s3_data = S3Data(
            name="file.png",
            content_type=S3ContentTypeEnum.PNG,
        )

        s3_client.put_object(
            Bucket="test-bucket", Key=s3_data.s3_key, Body=b"test content"
        )

        storage = S3Storage()
        storage.bucket_name = "test-bucket"
        storage.s3_client = s3_client

        result = storage.get_bytes(s3_data)
        assert result == b"test content"

    def test_get_bytes_error(self, s3_client) -> None:
        """Test error handling when retrieving bytes from S3"""
        storage = S3Storage()
        storage.bucket_name = "test-bucket"
        storage.s3_client = s3_client

        s3_data = S3Data(
            name="nonexistent.png",
            content_type=S3ContentTypeEnum.PNG,
        )

        with pytest.raises(AppException):
            storage.get_bytes(s3_data)

    def test_delete_data(self, s3_client) -> None:
        """Test deleting data from S3"""
        s3_data = S3Data(
            name="file.png",
            content_type=S3ContentTypeEnum.PNG,
        )

        s3_client.put_object(
            Bucket="test-bucket", Key=s3_data.s3_key, Body=b"test content"
        )

        storage = S3Storage()
        storage.bucket_name = "test-bucket"
        storage.s3_client = s3_client

        # Should not raise exception
        storage.delete_data(s3_data)

    def test_list_items(self, s3_client) -> None:
        """Test listing items in S3 bucket"""
        s3_client.put_object(
            Bucket="test-bucket", Key="images/test1.png", Body=b"content1"
        )
        s3_client.put_object(
            Bucket="test-bucket", Key="images/test2.png", Body=b"content2"
        )

        storage = S3Storage()
        storage.bucket_name = "test-bucket"
        storage.s3_client = s3_client

        items = storage.list_items(prefix="images/")
        assert len(items) >= 0
        assert all(isinstance(item, S3Data) for item in items)
