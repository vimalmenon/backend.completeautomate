from backend.ai import ManusVideoGenerator
from backend.enum import AIVideoModelEnum
from backend.exception import AppException

UNSUPPORTED_AI_MODEL_ERROR = "Unsupported AI model"


class AgentVideoService:
    def __init__(
        self,
        prompt: str,
        video_ai: AIVideoModelEnum = AIVideoModelEnum.Manus,
    ) -> None:
        self.prompt = prompt
        self.video_ai = video_ai

    def get_model(self) -> ManusVideoGenerator:
        if self.video_ai == AIVideoModelEnum.Manus:
            return ManusVideoGenerator()
        raise AppException(UNSUPPORTED_AI_MODEL_ERROR)

    def get_prompt(self) -> str:
        return self.prompt