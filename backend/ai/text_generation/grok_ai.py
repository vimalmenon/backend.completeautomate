from enum import Enum

from langchain_xai import ChatXAI

from backend.config.env import env
from backend.enum.ai import AICreativityLevelEnum


class ModelEnum(Enum):
    GROK_3 = "grok-3"


class GrokAI:
    def __init__(
        self,
        model: ModelEnum = ModelEnum.GROK_3,
        creativity_level: AICreativityLevelEnum = AICreativityLevelEnum.LOW,
    ):
        self.llm = ChatXAI(
            model=model.value,
            temperature=creativity_level.value,
            api_key=env.GROK_API_KEY,
        )

    def get_model(self):
        return self.llm
