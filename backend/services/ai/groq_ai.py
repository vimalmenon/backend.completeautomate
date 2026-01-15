from langchain_groq import ChatGroq
from enum import Enum
from backend.config.env import env
from backend.config.enum import AICreativityLevelEnum
from pydantic import SecretStr


class ModelEnum(Enum):
    QWEN_32B = "qwen/qwen3-32b"
    LLAMA_3_1_8B_INSTANT = "llama-3.1-8b-instant"


class GroqAI:
    def __init__(
        self,
        model: ModelEnum = ModelEnum.LLAMA_3_1_8B_INSTANT,
        creativity_level: AICreativityLevelEnum = AICreativityLevelEnum.LOW,
    ):
        self.llm = ChatGroq(
            model=model.value,
            temperature=creativity_level.value,
            api_key=SecretStr(env.GROQ_API_KEY),
        )

    def get_model(self):
        return self.llm
