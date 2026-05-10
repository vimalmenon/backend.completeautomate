import logging
import os
import smtplib
from email.message import EmailMessage

from pydantic import SecretStr

from backend.config.env import env
from backend.exception import AppException

logger = logging.getLogger(__name__)


class EmailService:
    DEFAULT_SERVER = "smtppro.zoho.com"
    SSL_PORT = 465
    TLS_PORT = 587

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        server: str | None = None,
        port: int | None = None,
    ) -> None:
        self.server = server or os.environ.get("SMTP_SERVER", self.DEFAULT_SERVER)
        self.port = port or int(os.environ.get("SMTP_PORT", str(self.SSL_PORT)))
        self.username: str = username or env.SMTP_USERNAME

        env_password: str | SecretStr = env.SMTP_PASSWORD
        resolved_env_password = (
            env_password.get_secret_value()
            if isinstance(env_password, SecretStr)
            else env_password
        )
        self.password: str = password or resolved_env_password

    def _validate_credentials(self) -> None:
        if not self.username or not self.password:
            raise AppException(
                "SMTP credentials are required. Set SMTP_USERNAME and SMTP_PASSWORD."
            )

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: str | None = None,
        is_html: bool = False,
    ) -> None:
        self._validate_credentials()

        sender = from_email or self.username
        if not sender:
            raise AppException("A sender email address is required.")

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = to_email

        if is_html:
            message.set_content("This email requires an HTML-compatible client.")
            message.add_alternative(body, subtype="html")
        else:
            message.set_content(body)

        try:
            if self.port == self.SSL_PORT:
                with smtplib.SMTP_SSL(self.server, self.port) as smtp_client:
                    smtp_client.login(self.username, self.password)
                    smtp_client.send_message(message)
            elif self.port == self.TLS_PORT:
                with smtplib.SMTP(self.server, self.port) as smtp_client:
                    smtp_client.ehlo()
                    smtp_client.starttls()
                    smtp_client.ehlo()
                    smtp_client.login(self.username, self.password)
                    smtp_client.send_message(message)
            else:
                raise AppException(
                    f"Unsupported SMTP port {self.port}. Use 465 (SSL) or 587 (TLS)."
                )
        except (smtplib.SMTPException, OSError) as exc:
            logger.error("Failed to send email to %s: %s", to_email, exc)
            raise AppException(f"Failed to send email: {exc}") from exc
