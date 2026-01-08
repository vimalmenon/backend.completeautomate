from enum import Enum


class AICreativityLevelEnum(str, Enum):
    LOW = 0
    MEDIUM = 4
    HIGH = 7


class AIModelEnum(str, Enum):
    Deepseek = "Deepseek"
    Perplexity = "Perplexity"
    QWEN = "QWEN"
    Groq = "Groq"
