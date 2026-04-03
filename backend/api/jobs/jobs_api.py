from fastapi import APIRouter

from backend.data.api.job import JobData as ApiJobData
from backend.manager.job_manager import JobManager

router = APIRouter()


@router.get("/jobs", tags=["jobs"], response_model=list[ApiJobData])
def list_jobs() -> list[ApiJobData]:
    jobs = JobManager().get_all_jobs()
    return [ApiJobData.model_validate(job.to_json()) for job in jobs]
