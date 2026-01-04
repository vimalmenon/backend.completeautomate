from backend.services.utility.company_detail_utility import CompanyDetailUtility


class ScriptWriterAgent:
    name: str = "Luna"
    role: str = "Youtube Script Writer"
    responsibility: str = "Creating engaging and informative video scripts"

    def __init__(self):
        CompanyDetailUtility(
            role=self.role, responsibility=self.responsibility
        ).company_values
