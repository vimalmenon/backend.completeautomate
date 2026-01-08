from enum import Enum


class TaskStatusEnum(str, Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    CLEAN_UP = "CLEAN_UP"
    FAILED = "FAILED"


# Explanation of the status:
# NEW: Task is newly created
# PENDING: Task is pending and waiting to for other process to complete
# REVIEW: Task is under review by owner or agent
# IN_PROGRESS: Task is currently being processed
# APPROVED: Task is approved and ready to be completed
# COMPLETED: Task completed successfully
# CLEAN_UP : Task is marked for cleanup and will be deleted in the next cleanup cycle
# FAILED : On failure

# NEW -> IN_PROGRESS -> APPROVED -> COMPLETED


class JobStatusEnum(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    PROMOTE = "PROMOTE"
    FAILED = "FAILED"
    CLEAN_UP = "CLEAN_UP"


# Explanation of the status:

# PENDING: Task is pending and waiting to be processed
# REVIEW: Task is under review
# NEW: Task is newly created (Details Missing)
# IN_PROGRESS: Task is currently being processed
# APPROVED: Task is approved and ready to be completed
# COMPLETED: Task completed successfully
# PROMOTE: Task is promoted to next level a Task
# CLEAN_UP : Task is marked for cleanup and will be deleted in the next cleanup cycle
# FAILED : On failure


# NEW -> IN_PROGRESS -> APPROVED -> COMPLETED
