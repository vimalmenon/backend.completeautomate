"""Generator for producing Twitter/X post suggestions from a YouTube video."""

import logging
from uuid import UUID

from backend.data import YouTubeThumbnailImageGenerationPromptData
from backend.prompt_agent import YouTubeVideoTwitterPostAgent

logger = logging.getLogger(__name__)


class YouTubeVideoTwitterPostGenerator:
    """Generate Twitter/X thread suggestions for a completed YouTube video.

    Uses the YouTubeVideoTwitterPostAgent to create engaging social media
    posts from the video's title, description, and summary.
    """

    def __init__(self, job_id: UUID, title: str, description: str, video_summary: str):
        self.job_id = job_id
        self.data = YouTubeThumbnailImageGenerationPromptData(
            title=title,
            description=description,
            video_summary=video_summary,
        ).to_json()

    def generate(self) -> list[str]:
        agent = YouTubeVideoTwitterPostAgent(
            job_id=self.job_id,
            data=self.data,
        )
        try:
            result = agent.generate()
            posts = self._parse_posts(result)
            logger.info(
                "Generated %d Twitter post(s) for job %s", len(posts), self.job_id
            )
            return posts
        except Exception:
            logger.exception(
                "YouTubeVideoTwitterPostGenerator failed for job %s", self.job_id
            )
            return []
        finally:
            agent.clean_up()

    @staticmethod
    def _parse_posts(raw: str) -> list[str]:
        """Split the raw agent output into individual post suggestions."""
        blocks = raw.strip().split("\n\n")
        # Filter out empty blocks and comments
        posts = []
        for block in blocks:
            line = block.strip()
            if not line or line.startswith("Here") or line.startswith("---"):
                continue
            posts.append(line)
        # If splitting didn't work, return the whole thing as a single post
        return posts if posts else [raw.strip()]
