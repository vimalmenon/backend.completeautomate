"""LangGraph-powered YouTube Shorts generation pipeline.

Orchestrates multi-step short video content generation using
LangGraph state machine with optional DynamoDB persistence.
"""

import json
import logging
import os
import subprocess
import tempfile
from typing import Any, TypedDict, cast

from langgraph.graph import END, START, StateGraph

from backend.ai.speech_generation.qwen_speech_generator import QwenSpeechGenerator
from backend.data import S3Data
from backend.enum import PromptTaskEnum
from backend.enum.s3 import S3ContentTypeEnum
from backend.integration import GeneralAgent
from backend.integration.storage.s3_storage import S3Storage
from backend.services.agent_service import AgentService

logger = logging.getLogger(__name__)


class YouTubeShortGenerationState(TypedDict, total=False):
    """State for the YouTube Short generation pipeline.

    Tracks all data as it flows through the LangGraph nodes:
    fetch_input → generate_speech → generate_audio → generate_image_prompts → generate_video → finalize
    """

    # Input from job
    input: dict[str, Any]
    # Resolved short data from DB or input
    video_data: dict[str, Any] | None
    topic: str | None
    transcript: str | None
    # Generated content
    speech_script: str | None
    # Generated audio
    audio_file: dict[str, str | None] | None
    audio_format: str | None
    image_prompts: list[dict[str, str]] | None
    # Generated video
    video_file: dict[str, Any] | None
    rendered_video_s3_key: str | None
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
        builder.add_node("generate_audio", self._generate_audio)
        builder.add_node("generate_image_prompts", self._generate_image_prompts)
        builder.add_node("generate_video", self._generate_video)
        builder.add_node("finalize", self._finalize)

        # Flow: START → fetch_input
        builder.add_edge(START, "fetch_input")

        # Conditional: fetch_input → generate_speech (on success) or END (on error)
        builder.add_conditional_edges(
            "fetch_input",
            self._route_on_error,
            {"continue": "generate_speech", "end": END},
        )

        # Conditional: generate_speech → generate_audio or END
        builder.add_conditional_edges(
            "generate_speech",
            self._route_on_error,
            {"continue": "generate_audio", "end": END},
        )

        # Conditional: generate_audio → generate_image_prompts or END
        builder.add_conditional_edges(
            "generate_audio",
            self._route_on_error,
            {"continue": "generate_image_prompts", "end": END},
        )

        # Conditional: generate_image_prompts → generate_video or END
        builder.add_conditional_edges(
            "generate_image_prompts",
            self._route_on_error,
            {"continue": "generate_video", "end": END},
        )

        # Conditional: generate_video → finalize or END
        builder.add_conditional_edges(
            "generate_video",
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
            topic: str = state.get("topic", "") or ""
            transcript: str = state.get("transcript", "") or ""

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
        except Exception:
            logger.exception("Failed to generate speech for job %s", self.job_id)
            return _error_state("Speech generation failed unexpectedly")

    # ── Node: Generate Audio ──

    def _generate_audio(
        self, state: YouTubeShortGenerationState
    ) -> YouTubeShortGenerationState:
        """Generate audio from the speech script using TTS, upload to S3."""
        try:
            speech_script: str = state.get("speech_script", "") or ""

            if not speech_script:
                logger.warning(
                    "No speech script to convert to audio for job %s",
                    self.job_id,
                )
                return {
                    "audio_file": None,
                    "audio_format": None,
                    "status": "audio_skipped",
                }

            # Determine audio format from input, default to mp3
            inp = state.get("input", {})
            audio_format: str = inp.get("audio_format", "mp3")
            audio_filename = f"speech.{audio_format}"

            tts = QwenSpeechGenerator(audio_format=audio_format)
            audio_bytes = tts.generate_speech(speech_script)
            if not audio_bytes:
                logger.warning("TTS returned empty audio for job %s", self.job_id)
                return {
                    "audio_file": None,
                    "audio_format": None,
                    "status": "audio_skipped",
                }

            s3_data = S3Data(
                name=audio_filename,
                content_type=S3Data.detect_content_type_from_name(audio_filename),
                key=f"youtube-shorts/{self.job_id}",
            )
            storage = S3Storage()
            success = storage.upload_data(s3_data, audio_bytes)

            if not success:
                logger.error("Failed to upload audio to S3 for job %s", self.job_id)
                return _error_state("Audio upload to S3 failed")

            logger.info(
                "Audio generated and uploaded for job %s — key: %s, size: %d bytes",
                self.job_id,
                s3_data.s3_key,
                len(audio_bytes),
            )
            return {
                "audio_file": s3_data.to_json(),
                "audio_format": audio_format,
                "status": "audio_generated",
            }
        except Exception as e:
            logger.exception("Failed to generate audio for job %s", self.job_id)
            return _error_state(f"Audio generation failed: {e}")

    # ── Node: Generate Image Prompts ──

    def _generate_image_prompts(
        self, state: YouTubeShortGenerationState
    ) -> YouTubeShortGenerationState:
        """Generate image prompt descriptions for the short's visuals."""
        try:
            topic: str = state.get("topic", "") or ""
            speech_script: str = state.get("speech_script", "") or ""

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

    # ── Node: Generate Video ──

    def _generate_video(  # noqa: C901
        self, state: YouTubeShortGenerationState
    ) -> YouTubeShortGenerationState:
        """Render the YouTube Short video using Remotion and upload to S3."""
        try:
            speech_script: str = state.get("speech_script", "") or ""
            topic: str = state.get("topic", "") or ""
            audio_file: dict[str, Any] | None = state.get("audio_file")

            if not speech_script:
                return _error_state("No speech script available for video rendering")

            # Create a temp directory for the render config and output
            tmpdir = tempfile.mkdtemp(prefix="youtube_short_render_")
            output_filename = f"{self.job_id}.mp4"
            output_path = os.path.join(tmpdir, output_filename)

            # Build the render config
            audio_url = ""
            if audio_file:
                audio_url = audio_file.get("downloaded_path", "") or audio_file.get(
                    "s3_key", ""
                )

            render_config = {
                "props": {
                    "speechScript": speech_script,
                    "audioUrl": audio_url,
                    "topic": topic,
                },
                "output": output_path,
            }

            config_path = os.path.join(tmpdir, "render_config.json")
            with open(config_path, "w") as f:
                json.dump(render_config, f)

            logger.info(
                "Rendering video for job %s via Remotion (topic=%s, words=%d)",
                self.job_id,
                topic,
                len(speech_script.split()),
            )

            # Call the Remotion render script
            render_script = "/home/hermes/video.completeautomate/render-shorts.mjs"
            result = subprocess.run(
                ["node", render_script, "--input", config_path],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode != 0:
                logger.error(
                    "Remotion render failed for job %s:\nstdout: %s\nstderr: %s",
                    self.job_id,
                    result.stdout,
                    result.stderr,
                )
                return _error_state(
                    f"Video rendering failed: {result.stderr.strip() or 'Unknown error'}"
                )

            if not os.path.exists(output_path):
                return _error_state(
                    "Video rendering completed but output file not found"
                )

            logger.info(
                "Video rendered successfully for job %s: %s",
                self.job_id,
                output_path,
            )

            # Upload to S3
            s3_name = f"{self.job_id}.mp4"
            s3_key_prefix = f"youtube-shorts/{topic}" if topic else "youtube-shorts"
            s3_data = S3Data(
                name=s3_name,
                content_type=S3ContentTypeEnum.MP4,
                key=s3_key_prefix,
            )

            storage = S3Storage()
            with open(output_path, "rb") as f:
                video_bytes = f.read()
            upload_success = storage.upload_data(s3_data, video_bytes)

            if not upload_success:
                return _error_state("Failed to upload rendered video to S3")

            video_file_dict = s3_data.to_json()

            logger.info(
                "Video uploaded to S3 for job %s: s3_key=%s",
                self.job_id,
                s3_data.s3_key,
            )

            # Clean up temp directory
            try:
                import shutil

                shutil.rmtree(tmpdir)
            except Exception:
                pass

            return {
                "video_file": video_file_dict,
                "rendered_video_s3_key": s3_data.s3_key,
                "status": "video_generated",
            }

        except subprocess.TimeoutExpired:
            logger.exception("Video rendering timed out for job %s", self.job_id)
            return _error_state("Video rendering timed out after 600 seconds")
        except Exception as e:
            logger.exception("Failed to generate video for job %s", self.job_id)
            return _error_state(f"Video generation failed: {e}")

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
            "audio_file": state.get("audio_file"),
            "audio_format": state.get("audio_format"),
            "video_file": state.get("video_file"),
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
        from uuid import UUID

        self.job_id = UUID(job_id[:36])
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
            return [p.to_json() for p in prompts] if prompts else []
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
        "audio_file": None,
        "audio_format": None,
        "output": None,
    }
