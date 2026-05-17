from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from langgraph.graph import END, START, StateGraph

from backend.data import YouTubeShortDBData
from backend.enum import PromptTaskEnum
from backend.integration import GeneralAgent
from backend.services.agent_service import AgentService


@dataclass
class GraphState:
    video: YouTubeShortDBData
    comment: str | None = None
    error: str | None = None
    iterate: int = 0
    agent_message: list[dict] = field(default_factory=list)
    reflect_message: list[dict] = field(default_factory=list)
    generated_text: str | None = None


class YouTubeShortSpeechGenerationPromptAgent:
    task = PromptTaskEnum.YouTubeShortSpeechGenerationPrompt

    def __init__(self, job_id: UUID, data: dict):
        self.service = AgentService(
            prompt_task=self.task,
            task_id=f"{job_id}_short_speech",
            data=data,
        )
        self.agent = GeneralAgent(self.service)

    def generate(self) -> str:
        result = self.agent.invoke()
        content: str = result["messages"][-1].content
        return content

    def generate_with_graph(self, video_short: YouTubeShortDBData) -> str | None:
        graph = self._build_graph()
        state: dict = graph.invoke(
            GraphState(
                video=video_short,
            )
        )
        return state.get("generated_text")

    def clean_up(self) -> None:
        self.agent.clean_up_messages()

    def improve(self) -> None:
        pass

    def _build_graph(self):
        builder = StateGraph(GraphState)
        builder.add_node("generate_speech", self._generate_speech)
        builder.add_edge(START, "generate_speech")
        builder.add_edge("generate_speech", END)
        return builder.compile()

    def _generate_speech(self, state: GraphState) -> dict[str, Any]:
        try:
            result = self.agent.invoke()
            text: str = result["messages"][-1].content
            return {"generated_text": text}
        except Exception as e:
            return {"error": str(e), "generated_text": None}
