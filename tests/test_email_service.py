"""Unit tests for EmailService"""

from unittest.mock import MagicMock, patch

import pytest

from backend.exception import AppException
from backend.services.email_service import EmailService, env


@pytest.mark.unit
class TestEmailService:
    @patch("backend.services.email_service.smtplib.SMTP_SSL")
    def test_send_email_uses_ssl_for_port_465(self, mock_smtp_ssl: MagicMock) -> None:
        smtp_client = MagicMock()
        mock_smtp_ssl.return_value.__enter__.return_value = smtp_client

        service = EmailService(
            username="user@example.com",
            password="secret",
            port=465,
            server="smtp.zoho.com",
        )

        service.send_email(
            to_email="receiver@example.com",
            subject="Test Subject",
            body="Test Body",
        )

        mock_smtp_ssl.assert_called_once_with("smtp.zoho.com", 465)
        smtp_client.login.assert_called_once_with("user@example.com", "secret")
        smtp_client.send_message.assert_called_once()

    @patch("backend.services.email_service.smtplib.SMTP")
    def test_send_email_uses_tls_for_port_587(self, mock_smtp: MagicMock) -> None:
        smtp_client = MagicMock()
        mock_smtp.return_value.__enter__.return_value = smtp_client

        service = EmailService(
            username="user@example.com",
            password="secret",
            port=587,
            server="smtp.zoho.com",
        )

        service.send_email(
            to_email="receiver@example.com",
            subject="Test Subject",
            body="Test Body",
        )

        mock_smtp.assert_called_once_with("smtp.zoho.com", 587)
        smtp_client.starttls.assert_called_once()
        smtp_client.login.assert_called_once_with("user@example.com", "secret")
        smtp_client.send_message.assert_called_once()

    def test_send_email_raises_when_credentials_missing(self) -> None:
        with (
            patch.object(env, "SMTP_USERNAME", ""),
            patch.object(env, "SMTP_PASSWORD", ""),
        ):
            service = EmailService(username=None, password=None)

            with pytest.raises(AppException, match="SMTP credentials are required"):
                service.send_email(
                    to_email="receiver@example.com",
                    subject="Test Subject",
                    body="Test Body",
                )

    def test_send_email_raises_for_unsupported_port(self) -> None:
        service = EmailService(
            username="user@example.com",
            password="secret",
            port=2525,
            server="smtp.zoho.com",
        )

        with pytest.raises(AppException, match="Unsupported SMTP port"):
            service.send_email(
                to_email="receiver@example.com",
                subject="Test Subject",
                body="Test Body",
            )
