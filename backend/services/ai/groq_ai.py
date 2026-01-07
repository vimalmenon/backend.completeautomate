from langchain_groq import ChatGroq
from enum import Enum
from backend.config.env import env
from backend.config.enum import AICreativityLevelEnum


class ModelEnum(Enum):
    QWEN_32B = "qwen/qwen3-32b"

class GroqAI:
    def __init__(
        self,
        model: ModelEnum = ModelEnum.QWEN_32B,
        creativity_level: AICreativityLevelEnum = AICreativityLevelEnum.LOW,
    ):
        self.llm = ChatGroq(
            model=model.value,
            temperature=creativity_level.value,
            api_key=env.GROQ_API_KEY,
        )

    def get_model(self):
        return self.llm
