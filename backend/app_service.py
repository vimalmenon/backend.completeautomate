from backend.services.utility.company_detail_utility import CompanyDetailUtility


class AppService:

    def start(self) -> None:
        print(CompanyDetailUtility("AI Automation Service Provider").company_values)
