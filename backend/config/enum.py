from enum import Enum
from typing import Dict, Any

# Team roles and responsibilities mapping
TEAM_INFO: Dict[str, Dict[str, str]] = {
    "SCRUM_MASTER": {
        "role": "SCRUM MASTER",
        "responsibility": "Overseeing project management and team coordination",
    },
    "RESEARCHER": {
        "role": "RESEARCHER",
        "responsibility": "Conducting in-depth research to gather relevant information",
    },
    "BACKEND_DEVELOPER": {
        "role": "BACKEND DEVELOPER",
        "responsibility": "Designing and implementing server-side logic and databases",
    },
    "FRONTEND_DEVELOPER": {
        "role": "FRONTEND DEVELOPER",
        "responsibility": "Creating user interfaces and enhancing user experience",
    },
    "SCRIPT_WRITER": {
        "role": "SCRIPT WRITER",
        "responsibility": "Creating engaging and informative video scripts",
    },
    "MANAGER": {
        "role": "MANAGER",
        "responsibility": "Overseeing team performance and project delivery",
    },
    "GRAPHIC_DESIGNER": {
        "role": "GRAPHIC DESIGNER",
        "responsibility": "Designing visual content for various media",
    },
    "PLANNER": {
        "role": "PLANNER",
        "responsibility": "Planning and coordinating project tasks and resources",
    },
    "SOCIAL_MEDIA_MANAGER": {
        "role": "SOCIAL MEDIA MANAGER",
        "responsibility": "Managing social media platforms and campaigns",
    },
}


class TaskStatusEnum(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PENDING_APPROVAL = "PENDING_APPROVAL"


class TeamEnum(str, Enum):
    SCRUM_MASTER = "SCRUM_MASTER"
    RESEARCHER = "RESEARCHER"
    BACKEND_DEVELOPER = "BACKEND_DEVELOPER"
    FRONTEND_DEVELOPER = "FRONTEND_DEVELOPER"
    SCRIPT_WRITER = "SCRIPT_WRITER"
    MANAGER = "MANAGER"
    GRAPHIC_DESIGNER = "GRAPHIC_DESIGNER"
    PLANNER = "PLANNER"
    SOCIAL_MEDIA_MANAGER = "SOCIAL_MEDIA_MANAGER"

    def get_role(self) -> str:
        return TEAM_INFO[self.value]["role"]

    def get_responsibility(self) -> str:
        return TEAM_INFO[self.value]["responsibility"]


class AICreativityLevelEnum(str, Enum):
    LOW = 0
    MEDIUM = 4
    HIGH = 7
