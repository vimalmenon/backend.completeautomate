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
        use_open_route: bool = False,
    ):
        extra_args = {}
        if use_open_route:
            extra_args["base_url"] = "https://openrouter.ai/api/v1"
            extra_args["api_key"] = env.OPEN_ROUTE_API_KEY
        else:
            extra_args["api_key"] = env.DEEPSEEK_API_KEY

        self.llm = ChatDeepSeek(
            model=model.value, temperature=creativity_level.value, **extra_args
        )

    def start(self, messages: list):
        return self.llm.invoke(messages)

    def get_model(self):
        return self.llm
