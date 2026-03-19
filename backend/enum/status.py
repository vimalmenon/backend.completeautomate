from enum import Enum


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
