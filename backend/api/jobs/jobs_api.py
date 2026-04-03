from fastapi import APIRouter
from backend.manager.job_manager import JobManager

router = APIRouter()

@router.get("/jobs", tags=["jobs"])
def list_jobs():
    jobs = JobManager().get_all_jobs()
    return [job.to_json() for job in jobs]
