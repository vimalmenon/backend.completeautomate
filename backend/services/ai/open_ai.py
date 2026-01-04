from langchain_openai import ChatOpenAI
from enum import Enum


class ModelEnum(Enum):
    GPT_5_NANO = "gpt-5-nano"
    GPT_4O_MINI = "gpt-4o-mini"


class OpenAI:
    models = ModelEnum

    def __init__(self, model: ModelEnum = ModelEnum.GPT_5_NANO):
        self.llm = ChatOpenAI(
            model=model.value,
            temperature=0,
        )

    def start(self, messages: list):
        self.llm.invoke(messages)
        return self.llm.content
