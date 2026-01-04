import os
from backend.app_service import AppService
from backend.services.utility.company_detail_utility import CompanyDetailUtility


def main():
    AppService().start()
    print(CompanyDetailUtility("AI Automation Service Provider").company_values)


if __name__ == "__main__":
    main()
