from langchain_perplexity import ChatPerplexity
from backend.config.env import env
from backend.config.enum import AICreativityLevelEnum
from enum import Enum
from pydantic import SecretStr


class ModelEnum(Enum):
    SONAR = "sonar"


class PerplexityAI:

    def __init__(
        self,
        model: ModelEnum = ModelEnum.SONAR,
        creativity_level: AICreativityLevelEnum = AICreativityLevelEnum.LOW,
    ):
        self.llm = ChatPerplexity(
            model=model.value,
            temperature=creativity_level.value,
            api_key=SecretStr(env.PPLX_API_KEY),
        )

    def start(self, messages: list):
        return self.llm.invoke(messages)

    def get_model(self):
        return self.llm
