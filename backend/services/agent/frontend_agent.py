from backend.services.agent.base_agent import BaseAgent
from backend.config.enum import TeamEnum


class FrontendAgent(BaseAgent):
    name = "Frontend Agent"
    role = TeamEnum.FRONTEND_DEVELOPER
    responsibility = "Building and maintaining the user interface of applications"
    teams = []

    def __init__(self):
        pass

    def start_task(self, task: str):
        pass

    def resume_task(self, task_id: str):
        pass
