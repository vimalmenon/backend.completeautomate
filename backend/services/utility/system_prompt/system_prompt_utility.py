from backend.config.env import env
from backend.config.enum import TeamEnum

from jinja2 import Environment, FileSystemLoader

# Set up environment to load templates from a directory
jinja_env = Environment(
    loader=FileSystemLoader("backend/services/utility/system_prompt/templates")
)


class SystemPromptUtility:
    system_prompt: str
    role: TeamEnum

    def __init__(self, role: TeamEnum, teams: list[TeamEnum]) -> None:
        self.role = role
        self.system_prompt = self.__get_company_values(role, teams)

    def __get_company_values(self, role: TeamEnum, teams: list[TeamEnum]) -> str:
        base_text_template = jinja_env.get_template("base_text.html")
        core_values_template = jinja_env.get_template("core_values.html")
        team_details_template = jinja_env.get_template("team_details.html")

        base_text = base_text_template.render(
            role=role.get_role(), company_name=env.COMPANY_NAME
        )
        core_values = core_values_template.render()

        team_details = ""
        if teams:
            team_details = "\n".join(
                [
                    f"- {team.value['role']}: {team.value['responsibility']}"
                    for team in teams
                ]
            )
            team_details = team_details_template.render(team_details=team_details)
        responsibility_as_role = self.__get_responsibility_as_role(role)

        return "\n\n".join(
            [base_text, core_values, team_details, responsibility_as_role]
        )

    def __get_responsibility_as_role(self, role: TeamEnum) -> str:
        responsibility_template = jinja_env.get_template("responsibility.html")
        return responsibility_template.render(
            is_manager=(role == TeamEnum.MANAGER),
            is_frontend_developer=(role == TeamEnum.FRONTEND_DEVELOPER),
        )
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

    def get_system_prompt(self) -> str:
        return self.system_prompt
