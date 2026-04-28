from dataclasses import dataclass, field

from langgraph.graph import END, START, StateGraph

from backend.ai.text_generation.deepseek_ai import DeepseekAI, ModelEnum
from backend.data import YouTubeShortDBData
from backend.enum import PromptTaskEnum
from backend.prompt_agent.agent.base_agent import BaseAgent


@dataclass
class GraphState:
    video: YouTubeShortDBData
    comment: str | None
    error: str | None
    iterate: int = 0
    agent_message: list[dict] = field(default_factory=list)
    reflect_message: list[dict] = field(default_factory=list)


class YouTubeShortSpeechGenerationPromptAgent(BaseAgent):
    task = PromptTaskEnum.YouTubeShortSpeechGenerationPrompt

    def __init__(self):
        super().__init__()
        self.llm = DeepseekAI(model=ModelEnum.DEEPSEEK_REASONER).get_model()
        self.prompt = self.get_prompt()

    def generate(self, video_short: YouTubeShortDBData):
        graph = self.__generate_state()
        graph.invoke(
            GraphState(
                video=video_short,
            )
        )

    def improve(self): ...

    def __generate(self): ...

    def __reflect(self): ...

    def __format_output(self, state: GraphState) -> dict:
        return {}

    def __create_prompt(self, state: GraphState) -> dict:
        return {}

    def generate_node(self):
        self.__generate_state()

    def __generate_state(self):
        builder = StateGraph(GraphState)
        builder.add_node("create_prompt", self.__create_prompt)
        builder.add_node("format_output", self.__format_output)
        builder.add_edge(START, "create_prompt")
        builder.add_edge("create_prompt", "format_output")
        builder.add_edge("format_output", END)

        return builder.compile()
