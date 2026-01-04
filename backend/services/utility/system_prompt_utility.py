from backend.config.env import env
from backend.config.enum import TeamEnum


class SystemPromptUtility:
    system_prompt: str
    role: TeamEnum

    def __init__(self, role: TeamEnum, responsibility: str, teams: list) -> None:
        self.role = role
        self.system_prompt = self.__get_company_values(role, responsibility, teams)

    def __get_company_values(
        self, role: TeamEnum, responsibility: str, teams: list
    ) -> str:
        base_text = """
            As the {role} of {company_name}, my core responsibility is to operationalize our primary value of customer satisfaction and long-term relationships in every decision and process and also includes {responsibility}
            # Company core values.
            1) I will steer the company towards being a trusted automation partner, not just a service provider. Our goal is to become an integral part of our clients' operational efficiency and growth.
        """

        teams_text = ""
        if teams:
            teams_text = self.__get_team_details(teams)

        return (base_text + teams_text).format(
            company_name=env.COMPANY_NAME,
            role=role.value,
            responsibility=responsibility,
            teams=teams,
        )

    def __get_responsibility_as_role(self, role: TeamEnum) -> str:
        return ""

    def __get_team_details(self, teams: list[TeamEnum]) -> str:
        team_details = "\n".join(
            [
                f"- {team.value['role']}: {team.value['responsibility']}"
                for team in teams
            ]
        )
        return """
            You have access to following teams to do your job effectively:
            {team_details}
            """.format(
            team_details=team_details
        )

    def get_values(self) -> str:
        return self.system_prompt

    def get_system_prompt(self) -> str:
        return self.system_prompt
