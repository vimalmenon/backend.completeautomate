from backend.services.utility.company_detail_utility import CompanyDetailUtility
from backend.config.enum import TeamEnum


class ScriptWriterAgent:
    name: str = "Luna"
    role: TeamEnum = TeamEnum.SCRIPT_WRITER
    responsibility: str = "Creating engaging and informative video scripts"

    def __init__(self):
        CompanyDetailUtility(
            role=self.role, responsibility=self.responsibility
        ).company_values
