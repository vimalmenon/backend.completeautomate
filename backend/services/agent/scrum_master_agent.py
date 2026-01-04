from backend.services.utility.company_detail_utility import CompanyDetailUtility


class ScrumMasterAgent:
    name: str = "Kai"
    role: str = "Scrum Master"
    responsibility: str = "Facilitating agile processes and removing team impediments"

    def __init__(self):
        CompanyDetailUtility(
            role=self.role, responsibility=self.responsibility
        ).company_values
