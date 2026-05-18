import logging

from backend.data import JobData
from backend.enum import JobsStatusEnum
from backend.generator.base_generator import BaseGenerator
from backend.generator.youtube.youtube_short_langgraph import YouTubeShortLangGraph

logger = logging.getLogger(__name__)


class YouTubeShortGenerator(BaseGenerator):

    def __init__(self, job: JobData):
        super().__init__(job=job)
        self.input_data = job.task_data or {}

    def generate(self) -> tuple[JobsStatusEnum, dict]:
        logger.info(
            "Starting YouTube Short LangGraph pipeline for job %s",
            self.job.id,
        )
        try:
            runner = YouTubeShortLangGraph(job_id=str(self.job.id))
            result = runner.invoke(self.input_data)

            if result.get("error"):
                logger.error(
                    "YouTube Short generation failed for job %s: %s",
                    self.job.id,
                    result["error"],
                )
                return JobsStatusEnum.FAILED, {
                    "error": result["error"],
                    "status": result.get("status", "failed"),
                }

            output = result.get("output") or {}
            logger.info(
                "YouTube Short generation complete for job %s — "
                "speech: %s chars, images: %s, audio: %s, video: %s",
                self.job.id,
                len(output.get("speech_script", "") or ""),
                len(output.get("image_prompts", []) or []),
                "yes" if output.get("audio_file") else "no",
                "yes" if output.get("video_file") else "no",
            )
            return JobsStatusEnum.COMPLETE, {
                "speech_script": output.get("speech_script"),
                "image_prompts": output.get("image_prompts"),
                "topic": output.get("topic"),
                "transcript": output.get("transcript"),
                "audio_file": output.get("audio_file"),
                "video_file": output.get("video_file"),
            }

        except Exception as e:
            logger.exception(
                "YouTube Short generation raised exception for job %s",
                self.job.id,
            )
            return JobsStatusEnum.FAILED, {"error": str(e)}
