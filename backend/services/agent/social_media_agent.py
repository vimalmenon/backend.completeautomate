from backend.services.agent.base_agent import BaseAgent
from backend.config.enum import TeamEnum


class SocialMediaAgent(BaseAgent):
    name = "Samantha"
    role: TeamEnum = TeamEnum.SOCIAL_MEDIA_MANAGER

    def start_task(self, task: str):
        pass

    def resume_task(self, task_id: str):
        pass
