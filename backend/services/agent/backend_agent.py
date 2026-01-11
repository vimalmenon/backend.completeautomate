from backend.services.helper.system_prompt.system_prompt_helper import (
    SystemPromptHelper,
)
from backend.services.agent.base_agent import BaseAgent
from backend.config.enum import TeamEnum


class BackendAgent(BaseAgent):
    name = "Backend Agent"
    role = TeamEnum.BACKEND_DEVELOPER
    responsibility = "Building and maintaining the server-side logic and databases"
    teams = []

    def __init__(self):
        self.system_prompt = SystemPromptHelper(
            role=self.role, teams=self.teams
        ).get_system_prompt()

    def start_task(self, task: str):
        pass

    def resume_task(self, task_id: str):
        pass
