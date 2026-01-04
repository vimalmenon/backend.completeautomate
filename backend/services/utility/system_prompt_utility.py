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

        team_details = ""
        if teams:
            team_details = self.__get_team_details(teams)
        responsibility_as_role = self.__get_responsibility_as_role(role)

        return (base_text + team_details + responsibility_as_role).format(
            company_name=env.COMPANY_NAME,
            role=role.value,
            responsibility=responsibility,
        )

    def __get_responsibility_as_role(self, role: TeamEnum) -> str:
        if role == TeamEnum.MANAGER:
            return """
            # Responsibility as Manager
            1) You are responsible for overseeing team performance and project delivery.
            2) You must ensure that all teams are aligned with the company's core values and objectives.
            3) You will facilitate communication between different teams to ensure smooth project execution.
            4) You must delegate tasks effectively and monitor progress to meet deadlines.
            """
        if role == TeamEnum.SCRUM_MASTER:
            return """
            # Responsibility as Scrum Master
            1) You are responsible for facilitating agile processes and removing team impediments.
            2) You must ensure that the team adheres to agile principles and practices.
            3) You will organize and facilitate scrum ceremonies such as sprint planning, daily stand-ups, sprint reviews, and retrospectives.
            4) You must work closely with the product owner to ensure that the team has a clear understanding of the project goals and requirements.
            5) You will create subtasks for the team based on the project requirements and ensure that they are completed on time.
            """
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
