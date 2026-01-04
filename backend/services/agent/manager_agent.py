# from backend.services.utility.company_detail_utility import CompanyDetailUtility
from backend.config.enum import TeamEnum


class ManagerAgent:
    name: str = "Elara"
    role: TeamEnum = TeamEnum.MANAGER
    responsibility: str = "Overseeing team performance and project delivery"
    teams: list = ["scrum_master", "researcher"]

    def __init__(self):
        # CompanyValueUtility(
        #     role=self.role, responsibility=self.responsibility
        # ).company_values
        pass
