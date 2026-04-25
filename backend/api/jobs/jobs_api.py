from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException

from backend.data.api import JobResponse, JobUpdateRequest
from backend.manager import JobManager, JobSchedulerManager

router = APIRouter()


def _build_update_values(request: JobUpdateRequest) -> dict[str, Any]:
    """Build update values dict from request, filtering out None values."""
    values: dict[str, Any] = {}
    if request.status is not None:
        values["status"] = request.status.value
    if request.description is not None:
        values["description"] = request.description
    if request.task_data is not None:
        values["task_data"] = request.task_data
    if request.failed_count is not None:
        values["failed_count"] = request.failed_count
    if request.pending_on is not None:
        values["pending_on"] = [str(item) for item in request.pending_on]
    if request.completed_at is not None:
        values["completed_at"] = request.completed_at.isoformat()
    if request.error_msg is not None:
        values["error_msg"] = request.error_msg
    return values


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


@router.patch("/jobs/{job_id}", tags=["jobs"], response_model=JobResponse)
async def update_job(job_id: UUID, request: JobUpdateRequest) -> JobResponse:
    manager = JobManager()
    existing_job = manager.get_job_by_id(job_id)
    if not existing_job:
        raise HTTPException(status_code=404, detail="Job not found")

    values = _build_update_values(request)
    if values:
        manager.update_job_values(job_id, values)

    updated_job = manager.get_job_by_id(job_id)
    if not updated_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.model_validate(updated_job.to_json())


@router.put("/jobs/{job_id}", tags=["jobs"])
async def execute_job(job_id: UUID) -> dict[str, Any]:
    result = JobSchedulerManager().execute()
    return {"status": result}
