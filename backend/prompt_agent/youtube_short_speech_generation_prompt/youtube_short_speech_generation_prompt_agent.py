from dataclasses import dataclass, field

from langgraph.graph import StateGraph

from backend.ai.text_generation.deepseek_ai import DeepseekAI, ModelEnum
from backend.data import YouTubeShortDBData
from backend.enum import PromptTaskEnum
from backend.prompt_agent.agent.base_agent import BaseAgent


@dataclass
class GraphState:
    video: YouTubeShortDBData
    comment: str
    error: str | None
    iterate: int = 0
    agent_message: list[dict] = field(default_factory=list)
    reflect_message: list[dict] = field(default_factory=list)


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

    def __create_prompt(self, state: GraphState): ...

    def generate_node(self):
        self.__generate_state()

    def __generate_state(self):
        builder = StateGraph(GraphState)
        builder.add_node("create_prompt", self.__create_prompt)
        return builder
