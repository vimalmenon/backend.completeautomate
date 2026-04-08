"""Pytest configuration and shared fixtures"""

import os
from typing import Generator
from unittest.mock import MagicMock

import boto3
import pytest
from moto import mock_aws

from backend.enum import DbKeysEnum


def pytest_configure(config: pytest.Config) -> None:
    """Set up mock environment variables before any tests run"""
    # AWS Configuration (mocked)
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_REGION"] = "us-east-1"
    os.environ["AWS_CLIENT_ID"] = "test-client-id"
    os.environ["AWS_SECRET"] = "test-secret"
    os.environ["AWS_SECRET_MANAGER"] = "test-manager"
    os.environ["AWS_TABLE"] = "test-table"
    os.environ["AWS_S3_BUCKET"] = "test-bucket"
    os.environ["OFFLINE"] = "False"
    os.environ["QWEN_API_KEY"] = "test-qwen-key"

    # Application Configuration
    os.environ["COMPANY_NAME"] = "Complete Automate"
    os.environ["VERSION"] = "0.0.1"

    # LLM Provider Keys (mock values)
    os.environ["OPENAI_API_KEY"] = "test-openai-key"
    os.environ["GROK_API_KEY"] = "test-grok-key"
    os.environ["DEEPSEEK_API_KEY"] = "test-deepseek-key"
    os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key"
    os.environ["OPEN_ROUTE_API_KEY"] = "test-openrouter-key"
    os.environ["PPLX_API_KEY"] = "test-perplexity-key"

    # LangSmith Configuration
    os.environ["LANGSMITH_API_KEY"] = "test-langsmith-key"
    os.environ["LANGSMITH_TRACING"] = "false"
    os.environ["LANGSMITH_PROJECT"] = "Test Project"

    # External Services
    os.environ["TEXT_TO_SPEECH_API_KEY"] = "test-tts-key"
    os.environ["RESEMBLE_TTS_ID"] = "test-tts-id"
    os.environ["YOUTUBE_API_KEY"] = "test-youtube-key"
    os.environ["YOUTUBE_CHANNEL_ID"] = "test-channel-id"

    os.environ["CORS_ALLOWED_ORGINS"] = "http://localhost:3000"


@pytest.fixture(scope="session")
def aws_credentials() -> None:
    """Mock AWS credentials for tests"""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_REGION"] = "us-east-1"


@pytest.fixture(scope="function")
def aws_mock(aws_credentials: None) -> Generator:
    """Mock AWS services using moto"""
    with mock_aws():
        yield


@pytest.fixture(scope="function")
def s3_client(aws_mock: None):
    """Create a mock S3 client with test bucket"""
    client = boto3.client("s3", region_name="us-east-1")
    client.create_bucket(Bucket="test-bucket")
    return client


@pytest.fixture(scope="session")
def dynamodb_table(aws_credentials: None):
    """Create a shared mock DynamoDB table for tests"""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName="test-table",
            KeySchema=[
                {"AttributeName": DbKeysEnum.Primary.value, "KeyType": "HASH"},
                {"AttributeName": DbKeysEnum.Secondary.value, "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": DbKeysEnum.Primary.value, "AttributeType": "S"},
                {"AttributeName": DbKeysEnum.Secondary.value, "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield table


@pytest.fixture
def sample_task_data() -> dict:
    """Sample task data for testing"""
    return {
        "task_id": "test-task-123",
        "job_type": "IMAGE_GENERATOR",
        "status": "NEW",
        "created_at": "2026-02-25T00:00:00Z",
        "metadata": {"prompt": "test prompt"},
    }


@pytest.fixture
def mock_llm() -> MagicMock:
    """Mock LLM provider"""
    mock = MagicMock()
    mock.invoke.return_value = "Mock LLM response"
    return mock


@pytest.fixture(autouse=True)
def reset_environment() -> Generator:
    """Reset environment variables after each test"""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)
