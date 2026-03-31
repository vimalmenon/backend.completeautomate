from backend.enum import JobsStatusEnum
from backend.manager.job_manager import JobManager


def transform_data() -> bool:
    # TODO remove once done
    jobs = JobManager().get_in_review_job()
    for job in jobs:
        JobManager().update_job_status(
            job.id,
            JobsStatusEnum.COMPLETE
        )
    return False
