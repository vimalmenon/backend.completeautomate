"""LangGraph-powered YouTube Shorts generation pipeline.

Orchestrates multi-step short video content generation using
LangGraph state machine with optional DynamoDB persistence.
"""

import logging
from typing import Any, TypedDict, cast

from langgraph.graph import END, START, StateGraph

from backend.config.langgraph_session import get_checkpointer
from backend.data import YouTubeShortDBData
from backend.enum import PromptTaskEnum
from backend.exception import AppException
from backend.integration import GeneralAgent
from backend.services.agent_service import AgentService

logger = logging.getLogger(__name__)


class YouTubeShortGenerationState(TypedDict, total=False):
    """State for the YouTube Short generation pipeline.

    Tracks all data as it flows through the LangGraph nodes:
    fetch_input → generate_speech → generate_image_prompts → finalize
    """

    # Input from job
    input: dict[str, Any]
    # Resolved short data from DB or input
    video_data: dict[str, Any] | None
    topic: str | None
    transcript: str | None
    # Generated content
    speech_script: str | None
    image_prompts: list[dict[str, str]] | None
    # Execution tracking
    messages: list[dict[str, Any]]
    status: str
    error: str | None
    output: dict[str, Any] | None


class YouTubeShortLangGraph:
    """LangGraph-based YouTube Shorts content generator.

    Builds a state graph with nodes for each generation step,
    supports DynamoDB checkpointing for fault-tolerant long-running jobs.

    Usage:
        runner = YouTubeShortLangGraph()
        result = runner.invoke({"input": {"topic": "...", "transcript": "..."}})
    """

    def __init__(self, job_id: str, checkpointer: Any = None) -> None:
        self.job_id = job_id
        self.checkpointer = checkpointer
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(YouTubeShortGenerationState)

        # Register nodes
        builder.add_node("fetch_input", self._fetch_input)
        builder.add_node("generate_speech", self._generate_speech)
        builder.add_node("generate_image_prompts", self._generate_image_prompts)
        builder.add_node("finalize", self._finalize)

        # Flow: START → fetch_input
        builder.add_edge(START, "fetch_input")

        # Conditional: fetch_input → generate_speech (on success) or END (on error)
        builder.add_conditional_edges(
            "fetch_input",
            self._route_on_error,
            {"continue": "generate_speech", "end": END},
        )

        # Conditional: generate_speech → generate_image_prompts or END
        builder.add_conditional_edges(
            "generate_speech",
            self._route_on_error,
            {"continue": "generate_image_prompts", "end": END},
        )

        # Conditional: generate_image_prompts → finalize or END
        builder.add_conditional_edges(
            "generate_image_prompts",
            self._route_on_error,
            {"continue": "finalize", "end": END},
        )

        builder.add_edge("finalize", END)

        return builder.compile(
            checkpointer=self.checkpointer,
        )

    # ── Routing ──

    @staticmethod
    def _route_on_error(state: YouTubeShortGenerationState) -> str:
        """Route to 'continue' if no error, 'end' if error is set."""
        if state.get("error"):
            return "end"
        return "continue"

    # ── Node: Fetch Input ──

    def _fetch_input(
        self, state: YouTubeShortGenerationState
    ) -> YouTubeShortGenerationState:
        """Resolve input data — extract topic and transcript."""
        try:
            inp = state.get("input", {})
            topic = inp.get("topic", inp.get("title", ""))
            transcript = inp.get("transcript", "")

            if not topic:
                return _error_state("No topic found in input data")

            return {
                "topic": topic,
                "transcript": transcript,
                "video_data": inp.get("video_data"),
                "status": "input_fetched",
            }
        except Exception as e:
            logger.exception("Failed to fetch input for job %s", self.job_id)
            return _error_state(f"Input fetch failed: {e}")

    # ── Node: Generate Speech Script ──

    def _generate_speech(
        self, state: YouTubeShortGenerationState
    ) -> YouTubeShortGenerationState:
        """Generate the speech/voiceover script for the short."""
        try:
            topic = state.get("topic", "")
            transcript = state.get("transcript", "")

            agent = YouTubeShortSpeechGenerator(
                job_id=self.job_id,
                topic=topic,
                transcript=transcript,
            )
            speech_script = agent.generate()
            agent.clean_up()

            if not speech_script:
                return _error_state("Speech script generation returned empty")

            return {
                "speech_script": speech_script,
                "status": "speech_generated",
            }
        except Exception as e:
            logger.exception("Failed to generate speech for job %s", self.job_id)
            return _error_state(f"Speech generation failed: {e}")

    # ── Node: Generate Image Prompts ──

    def _generate_image_prompts(
        self, state: YouTubeShortGenerationState
    ) -> YouTubeShortGenerationState:
        """Generate image prompt descriptions for the short's visuals."""
        try:
            topic = state.get("topic", "")
            speech_script = state.get("speech_script", "")

            prompts = YouTubeShortImagePromptGenerator(
                job_id=self.job_id,
                topic=topic,
                speech_script=speech_script,
            ).generate()

            return {
                "image_prompts": prompts or [],
                "status": "image_prompts_generated",
            }
        except Exception as e:
            logger.exception("Failed to generate image prompts for job %s", self.job_id)
            return _error_state(f"Image prompt generation failed: {e}")

    # ── Node: Finalize ──

    def _finalize(
        self, state: YouTubeShortGenerationState
    ) -> YouTubeShortGenerationState:
        """Compile final output and mark complete."""
        output = {
            "topic": state.get("topic"),
            "transcript": state.get("transcript"),
            "speech_script": state.get("speech_script"),
            "image_prompts": state.get("image_prompts"),
        }
        return {
            "output": output,
            "status": "completed",
        }

    # ── Public API ──

    def invoke(
        self, input_data: dict, config: dict | None = None
    ) -> YouTubeShortGenerationState:
        """Run the full YouTube Short generation pipeline."""
        initial: YouTubeShortGenerationState = {
            "input": input_data,
            "messages": [],
            "status": "initialized",
        }
        if config and self.checkpointer:
            return cast(
                YouTubeShortGenerationState,
                self.graph.invoke(initial, config),
            )
        return cast(
            YouTubeShortGenerationState,
            self.graph.invoke(initial),
        )


# ── Helper Agents ──


class YouTubeShortSpeechGenerator:
    """Generate speech script for a YouTube Short using prompt agent."""

    TASK = PromptTaskEnum.YouTubeShortSpeechGenerationPrompt

    def __init__(self, job_id: str, topic: str, transcript: str):
        data = {"topic": topic, "transcript": transcript}
        self.service = AgentService(
            prompt_task=self.TASK,
            task_id=f"{job_id}_short_speech_gen",
            data=data,
        )
        self.agent = GeneralAgent(self.service)

    def generate(self) -> str | None:
        try:
            result = self.agent.invoke()
            content: str = result["messages"][-1].content
            return content
        except Exception:
            logger.exception("YouTubeShortSpeechGenerator failed")
            return None

    def clean_up(self) -> None:
        self.agent.clean_up_messages()


class YouTubeShortImagePromptGenerator:
    """Generate image prompts for a YouTube Short's visuals."""

    def __init__(self, job_id: str, topic: str, speech_script: str):
        self.job_id = job_id
        self.topic = topic
        self.speech_script = speech_script

    def generate(self) -> list[dict[str, str]] | None:
        """Generate a list of image prompt descriptions.

        Returns list of dicts like [{"name": "...", "prompt": "..."}]
        """
        try:
            from backend.prompt_agent import (
                YouTubeThumbnailImageGenerationPromptAgent,
            )

            data = {"topic": self.topic, "script": self.speech_script}
            agent = YouTubeThumbnailImageGenerationPromptAgent(
                job_id=self.job_id,
                data=data,
            )
            structured_response = agent.generate()
            prompts = YouTubeThumbnailImageGenerationPromptAgent.get_prompts(
                structured_response
            )
            agent.clean_up()
            return prompts
        except Exception:
            logger.exception("YouTubeShortImagePromptGenerator failed")
            return []


def _error_state(message: str) -> YouTubeShortGenerationState:
    """Create a state dict with an error."""
    return {
        "error": message,
        "status": "failed",
        "speech_script": None,
        "image_prompts": None,
        "output": None,
    }
