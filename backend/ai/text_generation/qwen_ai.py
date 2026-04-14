from enum import Enum

from langchain_qwq import ChatQwen

from backend.config.env import env
from backend.enum.ai import AICreativityLevelEnum


class ModelEnum(Enum):
    QWEN_3_5_PLUS = "qwen3.5-plus"


class QwenAI:
    def __init__(
        self,
        model: ModelEnum = ModelEnum.QWEN_3_5_PLUS,
        creativity_level: AICreativityLevelEnum = AICreativityLevelEnum.LOW,
    ):

        self.llm = ChatQwen(
            model=model.value,
            temperature=creativity_level.value,
            api_key=env.QWEN_API_KEY,
            extra_body={"enable_thinking": True},
        )

    def get_model(self):
        return self.llm
