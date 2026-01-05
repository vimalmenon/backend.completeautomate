from enum import Enum


class TaskStatusEnum(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PENDING_APPROVAL = "PENDING_APPROVAL"


class TeamEnum(dict[str, str], Enum):
    SCRUM_MASTER = {
        "role": "SCRUM MASTER",
        "responsibility": "Overseeing project management and team coordination",
    }
    RESEARCHER = {
        "role": "RESEARCHER",
        "responsibility": "Conducting in-depth research to gather relevant information",
    }
    BACKEND_DEVELOPER = {
        "role": "BACKEND DEVELOPER",
        "responsibility": "Designing and implementing server-side logic and databases",
    }
    FRONTEND_DEVELOPER = {
        "role": "FRONTEND DEVELOPER",
        "responsibility": "Creating user interfaces and enhancing user experience",
    }
    SCRIPT_WRITER = {
        "role": "SCRIPT WRITER",
        "responsibility": "Creating engaging and informative video scripts",
    }
    MANAGER = {
        "role": "MANAGER",
        "responsibility": "Overseeing team performance and project delivery",
    }

    def get_role(self) -> str:
        return self.value["role"]

    def get_responsibility(self) -> str:
        return self.value["responsibility"]


class AICreativityLevelEnum(str, Enum):
    LOW = 0
    MEDIUM = 4
    HIGH = 7
