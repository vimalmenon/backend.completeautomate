from enum import Enum

from langchain_qwq import ChatQwen

from backend.config.env import env
from backend.enum.ai import AICreativityLevelEnum


class ModelEnum(Enum):
    QWEN_CODER_FREE = "qwen/qwen3-coder:free"
    QWEN_CODER = "qwen/qwen3-coder"


class QwenAI:
    def __init__(
        self,
        model: ModelEnum = ModelEnum.QWEN_CODER,
        creativity_level: AICreativityLevelEnum = AICreativityLevelEnum.LOW,
    ):

        self.llm = ChatQwen(
            model=model.value,
            temperature=creativity_level.value,
            base_url="https://openrouter.ai/api/v1",
            api_key=env.OPEN_ROUTE_API_KEY,
        )

    def get_model(self):
        return self.llm
