from langchain_xai import ChatXAI
from enum import Enum


class ModelEnum(Enum):
    GROK_BETA = "grok-beta"


class ChatXAI:
    models = ModelEnum

    def __init__(self, model: ModelEnum = ModelEnum.GROK_BETA):
        self.llm = ChatXAI(
            model=model.value,
            temperature=0,
        )

    def start(self, messages: list):
        self.llm.invoke(messages)
        return self.llm.content
