import logging
from pathlib import Path
from typing import Any, Union

from botocore.exceptions import ClientError

from backend.config.env import env
from backend.config.session import get_aws_session
from backend.data.s3 import S3Data
from backend.exception.app_exception import AppException
from backend.helper.folder_helper.folder_helper import FolderHelper

logger = logging.getLogger(__name__)


class S3Storage:
    def __init__(self):
        session = get_aws_session()
        self.s3_client = session.client("s3", region_name=env.AWS_REGION)
        self.bucket_name = env.AWS_S3_BUCKET
        self.folder_helper = FolderHelper()

    def upload_data(
        self,
        s3_data: S3Data,
        data: Union[bytes, str, Path],
    ) -> bool:
        """
        Upload data to S3 bucket.

        Args:
            s3_data: S3Data object representing the data to upload
            data: Data to upload (bytes, string, or file path)

        Returns:
            True if upload successful, False otherwise
        """
        try:
            extra_args = {}
            if s3_data.content_type:
                extra_args["ContentType"] = s3_data.content_type.value

            if isinstance(data, Path) or (
                isinstance(data, str) and Path(data).exists()
            ):
                # Upload from file
                self.s3_client.upload_file(
                    str(data),
                    self.bucket_name,
                    s3_data.s3_key,
                    ExtraArgs=extra_args if extra_args else None,
                )
            elif isinstance(data, bytes):
                # Upload bytes
                self.s3_client.put_object(
                    Bucket=self.bucket_name, Key=s3_data.s3_key, Body=data, **extra_args
                )
            elif isinstance(data, str):
                # Upload string as bytes
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_data.s3_key,
                    Body=data.encode("utf-8"),
                    **extra_args,
                )
            else:
                raise ValueError(f"Unsupported data type: {type(data)}")

            return True
        except ClientError as e:
            logger.error(f"Error uploading to S3: {e}")
            return False

    def download_data(self, data: S3Data) -> str:
        """
        Get data from S3 bucket and download to output folder.

        Args:
            key: S3 object key (path/filename in S3)
            output_path: Local path to save the downloaded file
        Returns:
            Path to the downloaded file as string
        """
        try:
            output_path = data.downloaded_path
            self.folder_helper.create_missing_folders(output_path)
            logger.info(
                f"Downloading S3 object '{data.s3_key}' to output folder: {output_path}"
            )
            self.s3_client.download_file(
                self.bucket_name, data.s3_key, str(output_path)
            )
            logger.info(f"Successfully downloaded to {output_path}")
            return str(output_path)
        except ClientError as e:
            logger.error(f"Error getting data from S3 for key '{data.s3_key}': {e}")
            raise AppException(f"Error getting data from S3: {e}")

    def delete_data(self, data: S3Data) -> None:
        """
        Delete data from S3 bucket.

        Args:
            data: S3Data object representing the data to delete

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=data.s3_key)
        except ClientError as e:
            raise AppException(f"Error deleting data from S3: {e}")

    def list_items(self, prefix: str = "", max_keys: int = 1000) -> list[S3Data]:
        """
        List items in the S3 bucket.

        Args:
            prefix: Optional prefix to filter objects (e.g., 'images/', 'json/')
            max_keys: Maximum number of keys to return (default: 1000)

        Returns:
            List of S3Data objects for each item in the bucket
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix, MaxKeys=max_keys
            )

            if "Contents" not in response:
                logger.info(f"No objects found with prefix '{prefix}'")
                return []

            return [S3Data.to_cls_from_path(obj["Key"]) for obj in response["Contents"]]

        except ClientError as e:
            logger.error(f"Error listing S3 objects: {e}")
            raise AppException(f"Error listing S3 objects: {e}")

    def get_bytes(self, data: S3Data) -> Any:
        """
        Get byte data from S3 bucket without downloading to local file.

        Args:
            data: S3Data object representing the data to retrieve

        Returns:
            Byte content of the S3 object

        Raises:
            AppException: If error occurs while retrieving data from S3
        """
        try:
            logger.info(f"Retrieving bytes for S3 object '{data.s3_key}'")
            response = self.s3_client.get_object(
                Bucket=self.bucket_name, Key=data.s3_key
            )
            byte_data = response["Body"].read()
            logger.info(f"Successfully retrieved {len(byte_data)} bytes from S3")
            return byte_data
        except ClientError as e:
            logger.error(f"Error getting bytes from S3 for key '{data.s3_key}': {e}")
            raise AppException(f"Error getting bytes from S3: {e}")
        except Exception as e:
            logger.error(
                f"Unexpected error getting bytes from S3 for key '{data.s3_key}': {e}"
            )
            raise AppException(f"Unexpected error getting bytes from S3: {e}")
