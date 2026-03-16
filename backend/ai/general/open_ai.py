from enum import Enum

from langchain_openai import ChatOpenAI

from backend.config.env import env
from backend.enum.ai import AICreativityLevelEnum


class ModelEnum(Enum):
    GPT_5_NANO = "gpt-5-nano"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_5 = "gpt-5"


class OpenAI:
    def __init__(
        self,
        model: ModelEnum = ModelEnum.GPT_5_NANO,
        creativity_level: AICreativityLevelEnum = AICreativityLevelEnum.LOW,
    ):

        self.llm = ChatOpenAI(
            model=model.value,
            temperature=creativity_level.value,
            api_key=env.OPENAI_API_KEY,
        )

    def get_model(self):
        return self.llm
