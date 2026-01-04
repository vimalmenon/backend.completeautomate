from backend.config.env import env
from backend.config.enum import TeamEnum


class SystemPromptUtility:
    system_prompt: str
    role: TeamEnum

    def __init__(self, role: TeamEnum, teams: list[TeamEnum]) -> None:
        self.role = role
        self.system_prompt = self.__get_company_values(role, teams)

    def __get_company_values(self, role: TeamEnum, teams: list[TeamEnum]) -> str:
        base_text = """
            As the {role} of {company_name}, my core responsibility is to operationalize our primary value of customer satisfaction and long-term relationships in every decision and process and also includes
        """
        core_values = self.__get_company_core_values()

        team_details = ""
        if teams:
            team_details = self.__get_team_details(teams)
        responsibility_as_role = self.__get_responsibility_as_role(role)

        return (base_text + core_values + team_details + responsibility_as_role).format(
            company_name=env.COMPANY_NAME,
            role=role.get_role(),
        )

    def __get_responsibility_as_role(self, role: TeamEnum) -> str:
        if role == TeamEnum.MANAGER:
            return """
            # Responsibility as Manager
            1) You are responsible for overseeing team performance and project delivery.
            2) You must ensure that all teams are aligned with the company's core values and objectives.
            3) You will facilitate communication between different teams to ensure smooth project execution.
            4) You must delegate tasks effectively to teams and monitor progress to meet deadlines.
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
        if role == TeamEnum.CODER:
            return """
            # Responsibility as Coder
            1) You are responsible for developing and implementing code based on project requirements.
            2) You must ensure that the code adheres to best practices and coding standards.
            3) You will collaborate with other team members to ensure that the code integrates seamlessly with other components of the project.
            4) You must participate in code reviews and provide constructive feedback to peers.
            5) You will write unit tests to ensure the quality and reliability of the code.
            6) You must document the code to facilitate future maintenance and updates.
            7) You will push the code to the designated repository following the project's version control guidelines.
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

    def __get_company_core_values(self) -> str:
        return """
            # Company core values.
            1) Customer Satisfaction: We prioritize our clients' needs and strive to exceed their expectations through innovative automation solutions.
            2) Long-term Relationships: We believe in building lasting partnerships with our clients based on trust, transparency, and mutual growth.
            3) Innovation: We are committed to staying at the forefront of automation technology and continuously improving our services.
            4) Excellence: We aim for excellence in every project we undertake, ensuring high-quality deliverables and exceptional service.
        """

    def get_system_prompt(self) -> str:
        return self.system_prompt
