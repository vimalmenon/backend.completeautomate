from langchain_anthropic import ChatAnthropic
from enum import Enum
from backend.config.env import env
from backend.config.enum import AICreativityLevelEnum
from pydantic import SecretStr


class ModelEnum(Enum):
    claude_haiku = "claude-haiku-4-5-20251001"


class AnthropicAI:
    models = ModelEnum

    def __init__(
        self,
        model: ModelEnum = ModelEnum.claude_haiku,
        creativity_level: AICreativityLevelEnum = AICreativityLevelEnum.LOW,
    ):
        self.llm = ChatAnthropic(
            model=model.value,
            temperature=creativity_level.value,
            api_key=SecretStr(env.ANTHROPIC_API_KEY),
        )

    def start(self, messages: list):
        return self.llm.invoke(messages)

    def get_model(self):
        return self.llm
