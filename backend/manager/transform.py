from backend.manager.job_manager import JobManager


def transform_data() -> bool:
    jobs = JobManager().get_in_review_job()
    return False
