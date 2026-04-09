from uuid import UUID

from fastapi import APIRouter, HTTPException

from backend.data.api.job import JobData as ApiJobData
from backend.manager.job_manager import JobManager

router = APIRouter()


@router.get("/jobs", tags=["jobs"], response_model=list[ApiJobData])
async def list_jobs() -> list[ApiJobData]:
    jobs = JobManager().get_all_jobs()
    return [ApiJobData.model_validate(job.to_json()) for job in jobs]


@router.get("/jobs/{job_id}", tags=["jobs"], response_model=ApiJobData)
async def get_job(job_id: UUID) -> ApiJobData:
    job = JobManager().get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return ApiJobData.model_validate(job.to_json())
