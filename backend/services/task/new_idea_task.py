from backend.services.agent.manager_agent import ManagerAgent
from backend.services.agent.frontend_agent import FrontendAgent


class NewIdeaTask:

    def input(self, task: str):
        # manager = ManagerAgent().start_task(task=task)
        FrontendAgent().start_task(task=task)
