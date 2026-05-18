"""Generator that fetches trending topics and suggests blog topics."""

import json
import logging
from dataclasses import dataclass
from uuid import UUID, uuid4

from backend.generator.trending.trending_topic_fetcher import (
    TrendingTopicFetcher,
    TrendingSource,
)
from backend.prompt_agent import BlogTopicSuggestionAgent

logger = logging.getLogger(__name__)


@dataclass
class BlogTopicSuggestion:
    """A single blog topic suggestion from the AI agent."""

    title: str
    keywords: list[str]
    description: str
    audience: str
    tone: str = "professional"


class TrendingBlogTopicGenerator:
    """Fetch trending data → ask AI for topic suggestions → return curated list."""

    def __init__(
        self,
        niche: str = "",
        audience: str = "General audience",
        tone: str = "professional",
        max_suggestions: int = 5,
    ):
        self.niche = niche
        self.audience = audience
        self.tone = tone
        self.max_suggestions = max_suggestions
        self._fetcher = TrendingTopicFetcher()

    def generate(self) -> list[dict]:
        """Fetch trending → AI suggest → return structured topic list."""
        raw_sources = self._fetcher.fetch_all(niche=self.niche)
        deduped = TrendingTopicFetcher.deduplicate(raw_sources)

        if not deduped:
            logger.warning("No trending data found for niche=%s", self.niche)
            return []

        trending_text = self._format_trending_for_agent(deduped)
        suggestions_text = self._ask_agent(trending_text)
        parsed = self._parse_suggestions(suggestions_text)

        return parsed[: self.max_suggestions]

    @staticmethod
    def _format_trending_for_agent(sources: list[TrendingSource]) -> str:
        lines = [f"Found {len(sources)} trending items:"]
        for s in sources:
            lines.append(f"- [{s.source}] {s.title}")
        return "\n".join(lines)

    def _ask_agent(self, trending_text: str) -> str:
        job_id = uuid4()
        data = {
            "trending_data": trending_text,
            "niche": self.niche or "general",
            "audience": self.audience,
            "tone": self.tone,
        }
        agent = BlogTopicSuggestionAgent(job_id=job_id, data=data)
        try:
            result = agent.generate()
            return result
        finally:
            agent.clean_up()

    @staticmethod
    def _parse_suggestions(raw: str) -> list[dict]:
        """Parse structured JSON output or fall back to line-based parsing."""
        # Try JSON first
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict) and "suggestions" in parsed:
                return parsed["suggestions"]
        except (json.JSONDecodeError, TypeError):
            pass

        # Fallback: split by numbered entries
        suggestions: list[dict] = []
        current: dict[str, str | list[str]] = {}
        for line in raw.split("\n"):
            line = line.strip()
            if line.startswith("##") or (line and line[0].isdigit() and ". " in line[:4]):
                if current.get("title"):
                    suggestions.append(current)
                current = {"title": line.lstrip("0123456789.#. ").strip(), "keywords": []}
            elif line.lower().startswith("keywords"):
                kw_text = line.split(":", 1)[-1].strip()
                current["keywords"] = [k.strip() for k in kw_text.split(",") if k.strip()]
            elif line.lower().startswith("description"):
                current["description"] = line.split(":", 1)[-1].strip()
            elif line.lower().startswith("audience"):
                current["audience"] = line.split(":", 1)[-1].strip()
            elif line.lower().startswith("tone"):
                current["tone"] = line.split(":", 1)[-1].strip()

        if current.get("title"):
            suggestions.append(current)

        if not suggestions:
            # Last resort: treat each line as a topic
            for line in raw.strip().split("\n"):
                line = line.strip()
                if line and len(line) > 10 and not line.startswith("```"):
                    suggestions.append({"title": line, "keywords": []})

        return suggestions
