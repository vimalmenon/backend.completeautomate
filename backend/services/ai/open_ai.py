from langchain_openai import ChatOpenAI
from enum import Enum
from backend.config.env import env


class ModelEnum(Enum):
    GPT_5_NANO = "gpt-5-nano"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_5 = "gpt-5"


class OpenAI:
    models = ModelEnum

    def __init__(
        self, model: ModelEnum = ModelEnum.GPT_5_NANO, use_open_route: bool = False
    ):
        extra_args = {}
        if use_open_route:
            extra_args["base_url"] = "https://openrouter.ai/api/v1"
            extra_args["api_key"] = env.OPEN_ROUTE_API_KEY

        self.llm = ChatOpenAI(model=model.value, temperature=0, **extra_args)

    def get_model(self):
        return self.llm
