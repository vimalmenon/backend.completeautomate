from dataclasses import dataclass

from langgraph.graph import StateGraph

from backend.ai.text_generation.deepseek_ai import DeepseekAI, ModelEnum
from backend.data import YouTubeShortDBData
from backend.enum import PromptTaskEnum
from backend.prompt_agent.agent.base_agent import BaseAgent


@dataclass
class GraphState:
    message: list[dict]
    comment: str
    iterate: int
    error: str


class YouTubeShortSpeechGenerationPromptAgent(BaseAgent):
    task = PromptTaskEnum.YouTubeShortSpeechGenerationPrompt

    def __init__(self):
        super().__init__()
        self.llm = DeepseekAI(model=ModelEnum.DEEPSEEK_REASONER).get_model()

    def generate(self, video_short: YouTubeShortDBData):

        self.get_prompt()

    def improve(self): ...

    def __generate(self): ...

    def __reflect(self): ...

    def __format_output(self): ...

    def generate_node(self): ...

    def __generate_state(self) -> GraphState:
        builder = StateGraph(GraphState)
        return builder
