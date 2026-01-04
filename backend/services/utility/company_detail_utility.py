from backend.config.env import env


class CompanyDetailUtility:
    company_values: str

    def __init__(self, role: str, responsibility: str) -> None:
        self.company_values = self.__get_company_values(role, responsibility)

    def __get_company_values(self, role: str, responsibility: str) -> str:
        return """
            As the {role} of {company_name}, my core responsibility is to operationalize our primary value of customer satisfaction and long-term relationships in every decision and process and also includes {responsibility}
            #Values.
            1) I will steer the company towards being a trusted automation partner, not just a service provider. Our goal is to become an integral part of our clients' operational efficiency and growth.
        """.format(
            company_name=env.COMPANY_NAME, role=role, responsibility=responsibility
        )
