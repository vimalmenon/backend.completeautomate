from uuid import uuid4

from backend.data import PromptDBData, PromptVersionDBData
from backend.enum import AIModelEnum, PromptTaskEnum


def transform_data() -> bool:
    version_id = uuid4()
    
    version = PromptVersionDBData(
        prompt="",
        system_message ="",
        version=version_id,
        ai=AIModelEnum.Deepseek
    )
    PromptDBData(
        task=PromptTaskEnum.YouTubeShortSpeechGenerationPrompt,
        description="",        
        versions=[version],
        version=version_id,
        prompt_data=[]
    )
    return False
