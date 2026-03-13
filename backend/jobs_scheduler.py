import logging

logger = logging.getLogger(__name__)


class JobScheduler:

    def start(
        self,
        job_id: str | None = None,
        transform: bool | None = False,
        test: bool | None = False,
    ):
        if job_id:
            logger.info("Starting one-time job execution for job_id=%s", job_id)

            logger.info("Completed one-time job execution for job_id=%s", job_id)
            return
        pass
