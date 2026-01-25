from backend.services.agent.manager_agent import ManagerAgent
from backend.services.agent.frontend_agent import FrontendAgent
from backend.services.agent.planner_agent import PlannerAgent
from backend.services.agent.graphic_designer_agent import GraphicDesignerAgent
from backend.config.enum import TeamEnum


class NewIdeaTask:
    def __init__(self, assigned_team: TeamEnum):
        self.assigned_team = assigned_team

    def input(self, task: str):
        if self.assigned_team == TeamEnum.MANAGER:
            return ManagerAgent().start_task(task=task)
        if self.assigned_team == TeamEnum.FRONTEND_DEVELOPER:
            return FrontendAgent().start_task(task=task)
        if self.assigned_team == TeamEnum.PLANNER:
            return PlannerAgent().start_task(task=task)
        if self.assigned_team == TeamEnum.GRAPHIC_DESIGNER:
            return GraphicDesignerAgent().start_task(task=task)
