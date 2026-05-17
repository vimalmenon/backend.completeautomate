from jinja2 import StrictUndefined, Template, TemplateError

from backend.ai import (
    DeepseekAI,
    GrokAI,
    GrokImageGeneration,
    OpenRouterImageGeneration,
    PerplexityAI,
    QwenAI,
    QwenImageGeneration,
)
from backend.database import PromptDB
from backend.enum import AIImageModelEnum, AIModelEnum, PromptTaskEnum
from backend.exception import AppException

UNSUPPORTED_AI_MODEL_ERROR = "Unsupported AI model"


class AgentImageService:
    def __init__(self, prompt: str, image_ai: AIImageModelEnum = AIImageModelEnum.Qwen):
        self.prompt = prompt
        self.image_ai = image_ai

    def get_model(
        self,
    ) -> GrokImageGeneration | QwenImageGeneration | OpenRouterImageGeneration:
        if self.image_ai == AIImageModelEnum.Grok:
            return GrokImageGeneration()
        if self.image_ai == AIImageModelEnum.Qwen:
            return QwenImageGeneration()
        if self.image_ai == AIImageModelEnum.OpenRouter:
            return OpenRouterImageGeneration()
        else:
            raise AppException(UNSUPPORTED_AI_MODEL_ERROR)

    def get_prompt(self) -> str:
        return self.prompt


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

    def __inject_examples(self, rendered: str) -> str:
        if not self.prompt_data or not self.prompt_data.examples:
            return rendered

        formatted = []
        for i, ex in enumerate(self.prompt_data.examples):
            lines = []
            if "input" in ex:
                input_val = ex["input"]
                if isinstance(input_val, dict):
                    input_str = ", ".join(f"{k}={v}" for k, v in input_val.items())
                else:
                    input_str = str(input_val)
                lines.append(f"Example {i + 1} Input: {input_str}")
            if "output" in ex:
                lines.append(f"Example {i + 1} Output: {ex['output']}")
            if lines:
                formatted.append("\n".join(lines))

        if not formatted:
            return rendered

        examples_block = "\n\n---\nFew-shot Examples:\n" + "\n\n".join(formatted)
        return rendered + examples_block

    def get_model(self):
        if not self.prompt_data:
            raise AppException(self.PROMPT_DATA_NOT_FOUND_ERROR)
        if self.prompt_data.ai == AIModelEnum.Deepseek:
            return DeepseekAI().get_model()
        elif self.prompt_data.ai == AIModelEnum.Grok:
            return GrokAI().get_model()
        elif self.prompt_data.ai == AIModelEnum.Perplexity:
            return PerplexityAI().get_model()
        elif self.prompt_data.ai == AIModelEnum.Qwen:
            return QwenAI().get_model()
        else:
            raise AppException(UNSUPPORTED_AI_MODEL_ERROR)

    def get_system_message(self) -> str:
        if not self.prompt_data:
            raise AppException(self.PROMPT_DATA_NOT_FOUND_ERROR)
        rendered = self.__render_template(self.prompt_data.system_message)
        return self.__inject_examples(rendered)

    def get_prompt(self) -> str:
        if not self.prompt_data:
            raise AppException(self.PROMPT_DATA_NOT_FOUND_ERROR)
        rendered = self.__render_template(self.prompt_data.prompt)
        return self.__inject_examples(rendered)
