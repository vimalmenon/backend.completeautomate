"""Integration tests for S3 and DynamoDB"""

import pytest


@pytest.mark.integration
@pytest.mark.aws
class TestAWSIntegration:
    """Integration tests for AWS services"""

    def test_s3_upload_download_cycle(self, aws_mock: None) -> None:
        """Test complete S3 upload and download cycle"""
        import boto3

        from backend.data.s3 import S3Data
        from backend.enum.s3 import S3ContentTypeEnum
        from backend.integration.storage.s3_storage import S3Storage

        # Create S3 bucket
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")

        storage = S3Storage()
        storage.bucket_name = "test-bucket"
        storage.s3_client = s3_client

        # Upload data
        s3_data = S3Data(
            name="integration.json",
            content_type=S3ContentTypeEnum.JSON,
        )
        upload_result = storage.upload_data(s3_data, b"integration test content")
        assert upload_result is True

        # Download data
        bytes_result = storage.get_bytes(s3_data)
        assert bytes_result == b"integration test content"

    def test_dynamodb_put_get_cycle(self, dynamodb_table) -> None:
        """Test complete DynamoDB put and get cycle"""
        from backend.database.dynamo_database import DbManager

        db = DbManager()
        db.table = dynamodb_table

        # Put item
        test_item = {"id": "test-123", "data": "test data"}
        db.add_item(test_item)

        # Get item
        result = db.get_item({"id": "test-123"})
        assert result["id"] == "test-123"
        assert result["data"] == "test data"
