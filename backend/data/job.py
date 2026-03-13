from dataclasses import dataclass, field
from datetime import datetime


class JobStatus:
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    PENDING = "PENDING"
    REVIEW = "REVIEW"
    FAILED = "FAILED"


@dataclass
class JobData:
    status: JobStatus
    job_type: str
    task_data: dict
    created_at: datetime
    failed_count: int = 0
    pending_on: list[str] = field(default_factory=list)
    # trail: list[UUID] = field(default_factory=list)
    completed_at: datetime | None = None
