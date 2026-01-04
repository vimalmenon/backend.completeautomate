from langchain_deepseek import ChatDeepSeek
from enum import Enum
from backend.config.env import env
from backend.config.enum import AICreativityLevelEnum


class ModelEnum(Enum):
    DEEPSEEK_CHAT = "deepseek-chat"


class DeepseekAI:
    models = ModelEnum

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

    def start(self, messages: list):
        self.llm.invoke(messages)
        return self.llm.content

    def get_model(self):
        return self.llm
