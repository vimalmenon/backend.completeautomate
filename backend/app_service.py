from backend.services.utility.company_detail_utility import CompanyDetailUtility


class AppService:

    def start(self) -> None:
        print(
            CompanyDetailUtility(
                "AI Automation Service Provider",
                responsibility="driving innovation and excellence in automation solutions",
            ).company_values
        )
