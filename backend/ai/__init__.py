from importlib import import_module
from typing import Any

TEXT_GENERATION_MODULE = "backend.ai.text_generation"

__all__ = [
    "DeepseekAI",
    "GrokAI",
    "PerplexityAI",
    "QwenAI",
    "GrokImageGeneration",
    "QwenImageGeneration",
    "OpenRouterImageGeneration",
    "QwenSpeechGenerator",
]


_EXPORTS = {
    "DeepseekAI": (TEXT_GENERATION_MODULE, "DeepseekAI"),
    "GrokAI": (TEXT_GENERATION_MODULE, "GrokAI"),
    "PerplexityAI": (TEXT_GENERATION_MODULE, "PerplexityAI"),
    "QwenAI": (TEXT_GENERATION_MODULE, "QwenAI"),
    "GrokImageGeneration": (
        "backend.ai.image_generation.grok_image_generation",
        "GrokImageGeneration",
    ),
    "QwenImageGeneration": (
        "backend.ai.image_generation.qwen_image_generation",
        "QwenImageGeneration",
    ),
    "OpenRouterImageGeneration": (
        "backend.ai.image_generation.open_router_image_generation",
        "OpenRouterImageGeneration",
    ),
    "QwenSpeechGenerator": (
        "backend.ai.speech_generation.qwen_speech_generator",
        "QwenSpeechGenerator",
    ),
}


def __getattr__(name: str) -> Any:
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attribute_name = _EXPORTS[name]
    value = getattr(import_module(module_name), attribute_name)
    globals()[name] = value
    return value
