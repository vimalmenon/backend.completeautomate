from uuid import UUID

from fastapi import APIRouter, HTTPException

from backend.data.api import JobResponse
from backend.manager import JobManager, JobSchedulerManager

router = APIRouter()


@router.get("/jobs", tags=["jobs"], response_model=list[JobResponse])
async def list_jobs() -> list[JobResponse]:
    jobs = JobManager().get_all_jobs()
    return [JobResponse.model_validate(job.to_json()) for job in jobs]


@router.get("/jobs/{job_id}", tags=["jobs"], response_model=JobResponse)
async def get_job(job_id: UUID) -> JobResponse:
    job = JobManager().get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.model_validate(job.to_json())


@router.put("/jobs/{job_id}", tags=["jobs"])
async def execute_job(job_id: UUID):
    result = JobSchedulerManager().execute(job_id)
    return {"status": result}
