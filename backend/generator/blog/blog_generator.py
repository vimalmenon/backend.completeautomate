"""Blog post generator that wraps the BlogLangGraph pipeline.

Entry point for blog generation jobs. Delegates to BlogLangGraph
for the full pipeline (generate → S3 → finalize).
"""

import logging

from backend.data import JobData
from backend.enum import JobsStatusEnum
from backend.generator.base_generator import BaseGenerator
from backend.generator.blog.blog_langgraph import BlogLangGraph

logger = logging.getLogger(__name__)


class BlogGenerator(BaseGenerator):
    """Generates a blog post using the BlogLangGraph pipeline.

    Accepts job task_data with:
        topic (required): Blog topic
        audience: Target audience (default: "General audience")
        tone: Writing tone (default: "professional")
        word_count: Target word count (default: "1000")
        keywords: Comma-separated SEO keywords
        outline: Optional blog outline
        extra_context: Additional context for the writer
        tags: List or comma-separated tags
        instructions: Additional instructions
    """

    def __init__(self, job: JobData):
        super().__init__(job=job)
        self.input_data = job.task_data or {}

    def generate(self) -> tuple[JobsStatusEnum, dict]:
        logger.info(
            "Starting blog generation pipeline for job %s",
            self.job.id,
        )
        try:
            runner = BlogLangGraph(job_id=str(self.job.id))
            result = runner.invoke(self.input_data)

            if result.get("error"):
                logger.error(
                    "Blog generation failed for job %s: %s",
                    self.job.id,
                    result["error"],
                )
                return JobsStatusEnum.FAILED, {
                    "error": result["error"],
                    "status": result.get("status", "failed"),
                }

            output = result.get("output") or {}
            blog_post = output.get("blog_post") or {}

            logger.info(
                "Blog generation complete for job %s — "
                "title: %s, slug: %s, words: %s",
                self.job.id,
                output.get("blog_title", ""),
                output.get("blog_slug", ""),
                output.get("word_count", 0),
            )

            return JobsStatusEnum.COMPLETE, {
                "blog_title": output.get("blog_title"),
                "blog_slug": output.get("blog_slug"),
                "tags": output.get("tags"),
                "blog_post": blog_post,
                "word_count": output.get("word_count", 0),
            }

        except Exception as e:
            logger.exception(
                "Blog generation raised exception for job %s",
                self.job.id,
            )
            return JobsStatusEnum.FAILED, {"error": str(e)}
