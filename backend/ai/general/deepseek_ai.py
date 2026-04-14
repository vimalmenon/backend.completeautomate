from enum import Enum

from langchain_deepseek import ChatDeepSeek

from backend.config.env import env
from backend.enum import AICreativityLevelEnum


class ModelEnum(Enum):
    DEEPSEEK_CHAT = "deepseek-chat"
    DEEPSEEK_REASONER = "deepseek-reasoner"


class DeepseekAI:
    def __init__(
        self,
        model: ModelEnum = ModelEnum.DEEPSEEK_CHAT,
        creativity_level: AICreativityLevelEnum = AICreativityLevelEnum.LOW,
    ):
        self.llm = ChatDeepSeek(
            model=model.value,
            temperature=creativity_level.value,
            api_key=env.DEEPSEEK_API_KEY,
        )

    def get_model(self):
        return self.llm
