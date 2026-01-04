from backend.config.env import env


class CompanyDetailUtility:
    company_values: str

    def __init__(self, role: str):
        self.company_values = self.__get_company_values(role)

    def __get_company_values(self, role: str) -> str:
        return """
            You work for a company, {company_name}, as a {role}, and the company provides automation services. Align your response based on the company's values.
            #Values.
            2) We prioritize customer satisfaction and long-term relationships
        """.format(
            company_name=env.COMPANY_NAME, role=role
        )
