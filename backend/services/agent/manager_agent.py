from backend.services.utility.company_detail_utility import CompanyDetailUtility


class ManagerAgent:
    name: str = "Elara"
    role: str = "Manager"
    responsibility: str = "Overseeing team performance and project delivery"
    teams: list = ["scrum_master", "researcher"]

    def __init__(self):
        CompanyDetailUtility(
            role=self.role, responsibility=self.responsibility
        ).company_values
