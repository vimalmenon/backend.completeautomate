from enum import Enum

from langchain_openai import ChatOpenAI

from backend.config.env import env
from backend.enum.ai import AICreativityLevelEnum


class ModelEnum(Enum):
    QWEN_QWEN3_MAX_THINKING = "qwen/qwen3-max-thinking"
    QWEN_QWEN3_CODER_FREE = "qwen/qwen3-coder:free"
    QWEN_QWEN3_CODER = "qwen/qwen3-coder"


class OpenRouterAI:
    def __init__(
        self,
        model: ModelEnum = ModelEnum.QWEN_QWEN3_CODER,
        creativity_level: AICreativityLevelEnum = AICreativityLevelEnum.LOW,
    ):
        self.llm = ChatOpenAI(
            api_key=env.OPEN_ROUTE_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            model=model.value,
            temperature=creativity_level.value,
        )

    def get_model(self):
        return self.llm
