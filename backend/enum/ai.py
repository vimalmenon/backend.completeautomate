from enum import Enum


class AICreativityLevelEnum(str, Enum):
    LOW = 0
    MEDIUM = 4
    HIGH = 7


class AIModelEnum(str, Enum):
    Deepseek = "Deepseek"
    Perplexity = "Perplexity"
    Qwen = "Qwen"
    Grok = "Grok"


class AIImageModelEnum(str, Enum):
    Qwen = "Qwen"
    Grok = "Grok"
    OpenRouter = "OpenRouter"


class AIVideoModelEnum(str, Enum):
    Manus = "Manus"


class AISpeechModelEnum(str, Enum):
    Qwen = "Qwen"
