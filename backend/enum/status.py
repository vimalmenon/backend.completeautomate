from enum import Enum


class TaskStatusEnum(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING = "PENDING"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    CLEAN_UP = "CLEAN_UP"
    FAILED = "FAILED"


# Explanation of the status of Task:
# NEW: Task will be IN_PROGRESS in next cycle
# PENDING: Task is pending and waiting to for other process to complete
# REVIEW: Task is under review by owner or agent
# IN_PROGRESS: Task is currently being processed
# APPROVED: Task is approved and ready to be completed
# COMPLETED: Task completed successfully
# CLEAN_UP : Task is marked for cleanup and will be deleted in the next cleanup cycle
# FAILED : On failure

# NEW -> IN_PROGRESS -> APPROVED -> COMPLETED
# NEW -> IN_PROGRESS -> PENDING -> (Wait for other process to be over) -> COMPLETED
# NEW -> IN_PROGRESS -> REVIEW -> (Wait for Owner to review) -> COMPLETED
# NEW -> IN_PROGRESS -> FAILED -> (Process goes on)


class JobStatusEnum(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    PROMOTE = "PROMOTE"
    FAILED = "FAILED"
    CLEAN_UP = "CLEAN_UP"


# Explanation of the status of Job:

# PENDING: Job is pending and waiting to be processed
# REVIEW: Job is under review
# NEW: Job is newly created (Details Missing)
# IN_PROGRESS: Job is currently being processed
# APPROVED: Job is approved and ready to be completed
# COMPLETED: Job completed successfully
# PROMOTE: Job is promoted to next level as Task
# CLEAN_UP : Job is marked for cleanup and will be deleted in the next cleanup cycle
# FAILED : Failure


# NEW -> IN_PROGRESS -> APPROVED -> COMPLETED
