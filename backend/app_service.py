from backend.services.utility.company_detail_utility import CompanyDetailUtility


class AppService:

    def start(self) -> None:
        # Get pending tasks
        # Prepare next tasks
        # Search for next tasks

        print(
            CompanyDetailUtility(
                "AI Automation Service Provider",
                responsibility="driving innovation and excellence in automation solutions",
            ).company_values
        )
