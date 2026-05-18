"""Notification service for job completion alerts.

Supports multiple channels (email, with extensible pattern for Signal/WhatsApp).
Wired into JobManager to send notifications when jobs complete or fail.
"""

import logging
from datetime import datetime
from typing import Any

from backend.services.email_service import EmailService

logger = logging.getLogger(__name__)


class NotificationService:
    """Send notifications across configured channels when jobs complete.

    Usage:
        NotificationService.notify_job_complete(job_id, job_type, status, task_data)

    To add a new channel:
        1. Add a method like _send_signal(...)
        2. Call it in notify() based on env config
    """

    @staticmethod
    def _format_job_summary(  # noqa: C901
        job_id: str,
        job_type: str,
        status: str,
        task_data: dict[str, Any] | None,
        error_msg: str | None = None,
    ) -> str:
        """Format a human-readable job summary for notifications."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            f"═══ Job {status} ═══",
            f"Time:  {now}",
            f"Job:   {job_id}",
            f"Type:  {job_type}",
            f"State: {status}",
        ]

        if error_msg:
            lines.append(f"Error: {error_msg}")

        # Add task-specific details
        if task_data:
            # Extract key info based on job type
            topic = task_data.get("topic") or task_data.get("title", "")
            if topic:
                lines.append(f"Topic: {topic}")

            speech = task_data.get("speech_script", "")
            if speech:
                lines.append(f"Speech: {len(speech)} chars")

            prompts = task_data.get("image_prompts", [])
            if prompts:
                lines.append(f"Images: {len(prompts)} prompts")

            audio = task_data.get("audio_file")
            if audio:
                if isinstance(audio, dict):
                    lines.append(f"Audio:  {audio.get('name', 'yes')}")
                else:
                    lines.append("Audio:  yes")

            video = task_data.get("video_file")
            if video:
                if isinstance(video, dict):
                    lines.append(f"Video:  {video.get('name', 'yes')}")
                else:
                    lines.append("Video:  yes")

            s3_key = task_data.get("rendered_video_s3_key")
            if s3_key:
                lines.append(f"S3 Key: {s3_key}")

        return "\n".join(lines)

    @classmethod
    def notify_job_complete(
        cls,
        job_id: str,
        job_type: str,
        task_data: dict[str, Any] | None = None,
        error_msg: str | None = None,
    ) -> None:
        """Send notifications for a completed/failed job.

        Sends via all configured channels. Currently supports email.
        """
        is_failed = error_msg is not None
        status = "FAILED" if is_failed else "COMPLETE"

        summary = cls._format_job_summary(
            job_id=job_id,
            job_type=job_type,
            status=status,
            task_data=task_data,
            error_msg=error_msg,
        )

        logger.info(
            "Job %s [%s] %s — sending notifications",
            job_id,
            job_type,
            status,
        )

        cls._send_email(job_id, job_type, status, summary)

    @classmethod
    def _send_email(
        cls,
        job_id: str,
        job_type: str,
        status: str,
        body: str,
    ) -> None:
        """Send notification via email if configured."""
        from backend.config.env import env

        try:
            to_email = getattr(env, "NOTIFICATION_EMAIL_TO", None) or getattr(
                env, "SMTP_USERNAME", None
            )
            if not to_email:
                logger.debug(
                    "No NOTIFICATION_EMAIL_TO set — skipping email notification"
                )
                return

            subject = f"[CompleteAutomate] Job {status}: {job_type} ({job_id[:8]}...)"
            email_service = EmailService()
            email_service.send_email(
                to_email=to_email,
                subject=subject,
                body=body,
            )
            logger.info("Email notification sent to %s for job %s", to_email, job_id)
        except Exception as e:
            logger.warning(
                "Failed to send email notification for job %s: %s",
                job_id,
                e,
            )
