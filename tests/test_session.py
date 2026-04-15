from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError

from backend.config import session as session_config


def test_ensure_offline_aws_ignores_existing_table_race() -> None:
    mock_session = MagicMock()
    mock_s3_client = MagicMock()
    mock_dynamodb = MagicMock()

    mock_session.client.return_value = mock_s3_client
    mock_session.resource.return_value = mock_dynamodb
    mock_dynamodb.meta.client.describe_table.side_effect = ClientError(
        error_response={"Error": {"Code": "ResourceNotFoundException"}},
        operation_name="DescribeTable",
    )
    mock_dynamodb.create_table.side_effect = ClientError(
        error_response={"Error": {"Code": "ResourceInUseException"}},
        operation_name="CreateTable",
    )
    with (
        patch("backend.config.session._moto_mock", object()),
        patch("backend.config.session._offline_bootstrapped", False),
        patch("backend.config.session.boto3.Session", return_value=mock_session),
    ):
        session_config.ensure_offline_aws()
        assert session_config._offline_bootstrapped is True
