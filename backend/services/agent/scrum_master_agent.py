from backend.services.utility.company_detail_utility import CompanyDetailUtility
from backend.config.enum import TeamEnum


class ScrumMasterAgent:
    name: str = "Kai"
    role: TeamEnum = TeamEnum.SCRUM_MASTER
    responsibility: str = "Facilitating agile processes and removing team impediments"

    def __init__(self):
        CompanyDetailUtility(
            role=self.role, responsibility=self.responsibility
        ).company_values
