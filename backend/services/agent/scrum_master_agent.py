from backend.services.utility.system_prompt.system_prompt_utility import (
    SystemPromptUtility,
)
from backend.config.enum import TeamEnum


class ScrumMasterAgent:
    name: str = "Kai"
    role: TeamEnum = TeamEnum.SCRUM_MASTER
    responsibility: str = "Facilitating agile processes and removing team impediments"

    def __init__(self):
        self.system_prompt = SystemPromptUtility(
            role=self.role, responsibility=self.responsibility
        ).get_system_prompt()
