from jinja2 import StrictUndefined, Template, TemplateError

from backend.ai import DeepseekAI, GrokAI, PerplexityAI
from backend.database import PromptDB
from backend.enum import AIModelEnum, PromptTaskEnum
from backend.exception.app_exception import AppException


class AgentService:
    PROMPT_DATA_NOT_FOUND_ERROR = "Prompt data not found for the given task"

    def __init__(
        self, prompt_task: PromptTaskEnum, task_id: str, data: dict | None = None
    ):
        self.db = PromptDB()
        self.prompt_task = prompt_task
        self.task_id = task_id
        self.prompt_data = self.db.get_prompt_by_task(self.prompt_task)
        self.data = data or {}

    def __render_template(self, template: str) -> str:
        try:
            return Template(template, undefined=StrictUndefined).render(**self.data)
        except TemplateError as e:
            raise AppException(f"Error rendering prompt template: {e}") from e

    def get_model(self):
        if not self.prompt_data:
            raise AppException(self.PROMPT_DATA_NOT_FOUND_ERROR)
        if self.prompt_data.ai == AIModelEnum.Deepseek:
            return DeepseekAI().get_model()
        elif self.prompt_data.ai == AIModelEnum.Grok:
            return GrokAI().get_model()
        elif self.prompt_data.ai == AIModelEnum.Perplexity:
            return PerplexityAI().get_model()
        else:
            raise AppException("Unsupported AI model")

    def get_system_message(self) -> str:
        if not self.prompt_data:
            raise AppException(self.PROMPT_DATA_NOT_FOUND_ERROR)
        return self.__render_template(self.prompt_data.system_message)

    def get_prompt(self) -> str:
        if not self.prompt_data:
            raise AppException(self.PROMPT_DATA_NOT_FOUND_ERROR)
        return self.__render_template(self.prompt_data.prompt)
