from backend.config.env import env
from backend.config.enum import TeamEnum


class CompanyValueUtility:
    company_values: str
    role: TeamEnum

    def __init__(self, role: TeamEnum, responsibility: str, teams: list) -> None:
        self.role = role
        self.company_values = self.__get_company_values(role, responsibility, teams)

    def __get_company_values(self, role: str, responsibility: str, teams: list) -> str:
        base_text = """
            As the {role} of {company_name}, my core responsibility is to operationalize our primary value of customer satisfaction and long-term relationships in every decision and process and also includes {responsibility}
            #Values.
            1) I will steer the company towards being a trusted automation partner, not just a service provider. Our goal is to become an integral part of our clients' operational efficiency and growth.
        """

        teams_text = ""
        if teams:
            teams_text = """
            You have access to following teams to do your job effectively:
            {teams}
            """

        return (base_text + teams_text).format(
            company_name=env.COMPANY_NAME,
            role=role.value,
            responsibility=responsibility,
            teams=teams,
        )

    def get_values(self) -> str:
        return self.company_values
