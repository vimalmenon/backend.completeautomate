from enum import Enum


class TaskStatusEnum(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PENDING_APPROVAL = "PENDING_APPROVAL"


class TeamEnum(dict, Enum):
    SCRUM_MASTER = {
        "role": "SCRUM MASTER",
        "responsibility": "Overseeing project management and team coordination",
    }
    RESEARCHER = {
        "role": "RESEARCHER",
        "responsibility": "Conducting in-depth research to gather relevant information",
    }
    CODER = {
        "role": "CODER",
        "responsibility": "Developing and implementing code based on project requirements",
    }
    SCRIPT_WRITER = {
        "role": "SCRIPT WRITER",
        "responsibility": "Creating engaging and informative video scripts",
    }
    MANAGER = {
        "role": "MANAGER",
        "responsibility": "Overseeing team performance and project delivery",
    }


class AICreativityLevelEnum(str, Enum):
    LOW = 0
    MEDIUM = 4
    HIGH = 7
