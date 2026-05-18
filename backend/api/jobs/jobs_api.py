from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import Field

from backend.data.api import JobResponse, JobUpdateRequest
from backend.data.api.base_model import BaseModelWithConfig
from backend.enum import JobTypeEnum
from backend.manager import JobManager, JobSchedulerManager

router = APIRouter()


class BlogJobCreateRequest(BaseModelWithConfig):
    topic: str = Field(..., description="Blog topic")
    audience: str = Field("General audience", description="Target audience")
    tone: str = Field("professional", description="Writing tone")
    word_count: str = Field("1000", description="Target word count")
    keywords: str = Field("", description="Comma-separated SEO keywords")
    outline: str = Field("", description="Optional blog outline")
    extra_context: str = Field("", description="Additional context for the writer")
    tags: str = Field("", description="Comma-separated tags")


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


@router.post("/jobs/blog", tags=["jobs"], response_model=JobResponse)
async def create_blog_job(request: BlogJobCreateRequest) -> JobResponse:
    """Create a blog generation job."""
    manager = JobManager()
    job = manager.create_job(
        type=JobTypeEnum.BlogGeneration,
        task_data=request.model_dump(by_alias=False),
        description=f"Generate blog post: {request.topic[:80]}",
    )
    manager.save_job(job)
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


# ── Trending Blog Topics ─────────────────────────────────────────────


class TrendingTopicsRequest(BaseModelWithConfig):
    niche: str = Field("AI & Technology", description="Niche or industry to focus on")
    audience: str = Field(
        "Tech enthusiasts", description="Target audience for suggestions"
    )
    tone: str = Field("professional", description="Writing tone")
    max_suggestions: int = Field(
        5, description="Maximum number of topic suggestions", ge=1, le=20
    )


class TrendingTopicsResponse(BaseModelWithConfig):
    niche: str
    suggestions: list[dict]


@router.post(
    "/jobs/trending-topics", tags=["jobs"], response_model=TrendingTopicsResponse
)
async def suggest_blog_topics(request: TrendingTopicsRequest) -> TrendingTopicsResponse:
    """Fetch Google Trends + Google News → AI suggests blog topics → return curated list."""
    from backend.generator.trending.trending_blog_topic_generator import (
        TrendingBlogTopicGenerator,
    )

    generator = TrendingBlogTopicGenerator(
        niche=request.niche,
        audience=request.audience,
        tone=request.tone,
        max_suggestions=request.max_suggestions,
    )
    suggestions = generator.generate()
    return TrendingTopicsResponse(
        niche=request.niche,
        suggestions=suggestions,
    )
