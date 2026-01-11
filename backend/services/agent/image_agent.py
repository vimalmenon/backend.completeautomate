from backend.services.agent.base_agent import BaseAgent
from backend.config.enum import TeamEnum


class ImageAgent(BaseAgent):
    name = "Julia"
    role = TeamEnum.GRAPHIC_DESIGNER
    responsibility = "Designing visual content for various media"
    teams = []

    def start_task(self, task: str):
        pass

    def resume_task(self, task_id: str):
        pass
