from langchain_openai import ChatOpenAI
from enum import Enum
from backend.config.env import env
from backend.config.enum import AICreativityLevelEnum


class ModelEnum(Enum):
    GPT_5_NANO = "gpt-5-nano"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_5 = "gpt-5"


class OpenAI:
    models = ModelEnum

    def __init__(
        self,
        model: ModelEnum = ModelEnum.GPT_5_NANO,
        creativity_level: AICreativityLevelEnum = AICreativityLevelEnum.LOW,
        use_open_route: bool = False,
    ):
        extra_args = {}
        if use_open_route:
            extra_args["base_url"] = "https://openrouter.ai/api/v1"
            extra_args["api_key"] = env.OPEN_ROUTE_API_KEY
        else:
            extra_args["api_key"] = env.OPENAI_API_KEY

        self.llm = ChatOpenAI(
            model=model.value, temperature=creativity_level.value, **extra_args
        )

    def get_model(self):
        return self.llm
