import logging
from typing import Any

from backend.data import (
    TaskData,
    YouTubeTranscriptDBData,
    YouTubeVideoSummarizeJobData,
)
from backend.database import YouTubeVideoDB
from backend.enum import PromptTaskEnum, TaskStatusEnum
from backend.exception.app_exception import AppException
from backend.generator.base_generator import BaseGenerator
from backend.integration.agent.general_agent import GeneralAgent
from backend.integration.youtube.youtube_api import YouTubeAPI
from backend.services.agent_service import AgentService

logger = logging.getLogger(__name__)


class YouTubeVideoSummarizeGenerator(BaseGenerator):

    def __init__(self, task: TaskData):
        super().__init__(task)
        logger.info(f"Initializing YouTubeVideoSummarizeGenerator for video: {task.id}")
        self.payload = YouTubeVideoSummarizeJobData.to_cls(task.payload)
        self.youtube_api = YouTubeAPI()
        self.db = YouTubeVideoDB(self.payload.platform.channel_id)

    def generate(self) -> TaskStatusEnum:
        logger.info(f"Fetching transcript for video: {self.payload.platform.video_id}")
        try:
            result = self.youtube_api.get_transcript(self.payload.platform.video_id)
            if not result:
                raise AppException(
                    f"No transcript found for video: {self.payload.platform.video_id}"
                )
            if result:
                logger.info("Processing transcript")
                text_transcript = self.__convert_transcript_to_text(result)
                logger.info("Summarizing transcript")
                summarize = self.__summarize_transcript(text_transcript)
                logger.info(
                    f"Successfully generated transcript and summary for video: {self.payload.platform.video_id}"
                )
                data = YouTubeTranscriptDBData(
                    transcript=text_transcript, summarize=summarize
                )
                self.__update_db_with_transcript(data)
        except Exception as e:
            logger.error(
                f"Error processing transcript for video: {self.payload.platform.video_id}, error: {str(e)}"
            )
            raise AppException(
                f"Error processing transcript for video: {self.payload.platform.video_id}, error: {str(e)}"
            )
        return TaskStatusEnum.COMPLETED

    def __convert_transcript_to_text(self, result) -> str:
        logger.debug("Converting raw transcript data to text")
        text = [self.__process_transcript(snippet) for snippet in result.snippets]
        return "\n".join(text)

    def __process_transcript(self, snippet: Any) -> str:
        text = (
            snippet.get("text", "")
            if isinstance(snippet, dict)
            else getattr(snippet, "text", "")
        )
        start = float(
            snippet.get("start", 0.0)
            if isinstance(snippet, dict)
            else getattr(snippet, "start", 0.0)
        )
        duration = float(
            snippet.get("duration", 0.0)
            if isinstance(snippet, dict)
            else getattr(snippet, "duration", 0.0)
        )
        end = start + duration

        logger.debug("Processing transcript snippet from %.3f to %.3f", start, end)
        return f"[{start:.3f} {end:.3f}] {text}"

    def __summarize_transcript(self, text_transcript: str) -> Any:
        logger.debug(
            f"Summarizing transcript with length: {len(text_transcript)} characters"
        )
        service = AgentService(
            prompt_task=PromptTaskEnum.YouTubeVideoSummarization,
            task_id=str(self.task.id),
            data={
                "transcript": text_transcript,
            },
        )
        agent = GeneralAgent(
            service,
        )
        result = agent.invoke()
        return result["messages"][-1].content

    def __update_db_with_transcript(self, transcript: YouTubeTranscriptDBData) -> None:
        logger.info(
            f"Updating database with transcript for video: {self.payload.platform.video_id}"
        )
        self.db.update_transcript(self.payload.platform.video_id, transcript)
