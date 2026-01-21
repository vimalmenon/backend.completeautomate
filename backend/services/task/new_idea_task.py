from backend.services.agent.manager_agent import ManagerAgent
from backend.services.agent.frontend_agent import FrontendAgent
from backend.services.agent.planner_agent import PlannerAgent
from backend.services.agent.graphic_designer_agent import GraphicDesignerAgent


class NewIdeaTask:

    def input(self, task: str):
        # manager = ManagerAgent().start_task(task=task)
        # FrontendAgent().start_task(task=task)
        PlannerAgent().start_task(task=task)
        # GraphicDesignerAgent().start_task(task=task)
