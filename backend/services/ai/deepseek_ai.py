from langchain_deepseek import ChatDeepSeek
from enum import Enum


class ModelEnum(Enum):
    DEEPSEEK_CHAT = "deepseek-chat"


class DeepseekAI:
    models = ModelEnum

    def __init__(self, model: ModelEnum = ModelEnum.DEEPSEEK_CHAT):
        self.llm = ChatDeepSeek(
            model=model.value,
            temperature=0,
        )

    def start(self, messages: list):
        self.llm.invoke(messages)
        return self.llm.content
