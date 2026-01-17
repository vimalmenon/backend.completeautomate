from backend.config.env import env
from backend.config.enum import TeamEnum

from jinja2 import Environment, FileSystemLoader

# Set up environment to load templates from a directory
jinja_env = Environment(
    loader=FileSystemLoader("backend/services/helper/system_prompt/templates")
)


class SystemPromptHelper:
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

        return "\n\n".join([base_text, core_values, team_details])

    def __get_responsibility_as_role(self, role: TeamEnum) -> str:
        responsibility_template = jinja_env.get_template("responsibility.html")
        return responsibility_template.render(
            is_manager=(role == TeamEnum.MANAGER),
            is_frontend_developer=(role == TeamEnum.FRONTEND_DEVELOPER),
            is_backend_developer=(role == TeamEnum.BACKEND_DEVELOPER),
            is_graphic_designer=(role == TeamEnum.GRAPHIC_DESIGNER),
            is_researcher=(role == TeamEnum.RESEARCHER),
            is_planner=(role == TeamEnum.PLANNER),
        )

    def get_system_prompt(self) -> str:
        return self.system_prompt

    def get_system_message(self, content: str) -> str:
        responsibility_as_role = self.__get_responsibility_as_role(self.role)
        return "\n\n".join([content, responsibility_as_role])
