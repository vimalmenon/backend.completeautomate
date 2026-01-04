from enum import Enum


class TaskStatusEnum(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PENDING_APPROVAL = "PENDING_APPROVAL"


class TeamEnum(str, Enum):
    SCRUM_MASTER = "SCRUM MASTER"
    RESEARCHER = "RESEARCHER"
    CODER = "coder"
    SCRIPT_WRITER = "SCRIPT WRITER"
    MANAGER = "MANAGER"
