"""LangGraph-powered blog post generation pipeline.

Orchestrates multi-step blog content generation:
fetch_input → generate_blog → save_to_s3 → finalize
"""

import json
import logging
import re
from typing import Any, TypedDict, cast

from langgraph.graph import END, START, StateGraph

from backend.data.blog import BlogPostData
from backend.data.s3 import S3Data
from backend.enum.s3 import S3ContentTypeEnum
from backend.integration.storage.s3_storage import S3Storage
from backend.prompt_agent.blog_post_generation_prompt.blog_post_generation_prompt_agent import (
    BlogPostGenerationPromptAgent,
)

logger = logging.getLogger(__name__)


class BlogGenerationState(TypedDict, total=False):
    """State for the Blog generation pipeline.

    Tracks all data as it flows through the LangGraph nodes:
    fetch_input → generate_blog → save_to_s3 → finalize
    """

    # Input from job
    input: dict[str, Any]
    topic: str | None
    transcript: str | None
    instructions: str | None

    # Generated content
    blog_content: str | None
    blog_title: str | None
    blog_slug: str | None
    tags: list[str] | None

    # S3 reference
    blog_post: dict[str, Any] | None

    # Execution tracking
    messages: list[dict[str, Any]]
    status: str
    error: str | None
    output: dict[str, Any] | None


class BlogLangGraph:
    """LangGraph-based blog post content generator.

    Builds a state graph where each node generates and processes
    a stage of the blog post pipeline.

    Usage:
        runner = BlogLangGraph()
        result = runner.invoke({"topic": "...", "audience": "..."})
    """

    def __init__(self, job_id: str, checkpointer: Any = None) -> None:
        self.job_id = job_id
        self.checkpointer = checkpointer
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(BlogGenerationState)

        # Register nodes
        builder.add_node("fetch_input", self._fetch_input)
        builder.add_node("generate_blog", self._generate_blog)
        builder.add_node("save_to_s3", self._save_to_s3)
        builder.add_node("finalize", self._finalize)

        # Flow: START → fetch_input
        builder.add_edge(START, "fetch_input")

        # Conditional: fetch_input → generate_blog (on success) or END (on error)
        builder.add_conditional_edges(
            "fetch_input",
            self._route_on_error,
            {"continue": "generate_blog", "end": END},
        )

        # Conditional: generate_blog → save_to_s3 or END
        builder.add_conditional_edges(
            "generate_blog",
            self._route_on_error,
            {"continue": "save_to_s3", "end": END},
        )

        # Conditional: save_to_s3 → finalize or END
        builder.add_conditional_edges(
            "save_to_s3",
            self._route_on_error,
            {"continue": "finalize", "end": END},
        )

        builder.add_edge("finalize", END)

        return builder.compile(
            checkpointer=self.checkpointer,
        )

    # ── Routing ──

    @staticmethod
    def _route_on_error(state: BlogGenerationState) -> str:
        """Route to 'continue' if no error, 'end' if error is set."""
        if state.get("error"):
            return "end"
        return "continue"

    # ── Node: Fetch Input ──

    def _fetch_input(self, state: BlogGenerationState) -> BlogGenerationState:
        """Resolve input data — extract topic, audience, tone, etc."""
        try:
            inp = state.get("input", {})
            topic = inp.get("topic", inp.get("title", ""))
            transcript = inp.get("transcript", "")
            instructions = inp.get("instructions", "")

            if not topic:
                return _error_state("No topic found in input data")

            return {
                "topic": topic,
                "transcript": transcript,
                "instructions": instructions,
                "status": "input_fetched",
            }
        except Exception as e:
            logger.exception("Failed to fetch input for job %s", self.job_id)
            return _error_state(f"Input fetch failed: {e}")

    # ── Node: Generate Blog Post ──

    def _generate_blog(self, state: BlogGenerationState) -> BlogGenerationState:
        """Generate the blog post content using BlogPostGenerationPromptAgent."""
        from uuid import UUID

        try:
            topic: str = state.get("topic", "") or ""
            inp = state.get("input", {})

            agent = BlogPostGenerationPromptAgent(
                job_id=UUID(self.job_id[:36]),
                data={
                    "topic": topic,
                    "audience": inp.get("audience", "General audience"),
                    "tone": inp.get("tone", "professional"),
                    "word_count": inp.get("word_count", "1000"),
                    "keywords": inp.get("keywords", ""),
                    "outline": inp.get("outline", ""),
                    "extra_context": inp.get("extra_context", ""),
                },
            )
            raw_content = agent.generate()
            agent.clean_up()

            if not raw_content or not raw_content.strip():
                return _error_state("Blog post generation returned empty content")

            # Parse the structured response
            title = self._extract_title(raw_content)
            slug = self._generate_slug(title or topic)
            tags = self._extract_tags(inp)
            content = raw_content

            return {
                "blog_content": content,
                "blog_title": title or topic,
                "blog_slug": slug,
                "tags": tags,
                "status": "blog_generated",
            }
        except Exception as e:
            logger.exception("Failed to generate blog for job %s", self.job_id)
            return _error_state(f"Blog generation failed: {e}")

    # ── Node: Save to S3 ──

    def _save_to_s3(self, state: BlogGenerationState) -> BlogGenerationState:
        """Save the blog post as JSON to S3."""
        try:
            blog_content: str = state.get("blog_content", "") or ""
            blog_title: str = state.get("blog_title", "") or ""
            blog_slug: str = state.get("blog_slug", "") or ""
            tags: list[str] = state.get("tags", []) or []
            topic: str = state.get("topic", "") or ""
            inp = state.get("input", {})

            blog_post = BlogPostData(
                title=blog_title,
                content=blog_content,
                slug=blog_slug,
                tags=tags,
                meta_description=self._extract_meta_description(blog_content),
                tone=inp.get("tone", "professional"),
                topic=topic,
                word_count=len(blog_content.split()),
                job_id=self.job_id,
            )

            # Save to S3 as JSON
            filename = f"{blog_slug}.json"
            s3_data = S3Data(
                name=filename,
                content_type=S3ContentTypeEnum.JSON,
                key=f"blog-posts/{topic}" if topic else "blog-posts",
            )

            storage = S3Storage()
            blog_json = json.dumps(blog_post.to_json(), indent=2).encode("utf-8")
            upload_success = storage.upload_data(s3_data, blog_json)

            if not upload_success:
                return _error_state("Failed to upload blog post to S3")

            blog_post_dict = blog_post.to_json()
            blog_post_dict["s3_key"] = s3_data.s3_key

            logger.info(
                "Blog post saved to S3 for job %s: s3_key=%s",
                self.job_id,
                s3_data.s3_key,
            )

            return {
                "blog_post": blog_post_dict,
                "status": "saved_to_s3",
            }
        except Exception as e:
            logger.exception("Failed to save blog post to S3 for job %s", self.job_id)
            return _error_state(f"S3 save failed: {e}")

    # ── Node: Finalize ──

    def _finalize(self, state: BlogGenerationState) -> BlogGenerationState:
        """Compile final output and mark complete."""
        output = {
            "topic": state.get("topic"),
            "blog_title": state.get("blog_title"),
            "blog_slug": state.get("blog_slug"),
            "tags": state.get("tags"),
            "blog_post": state.get("blog_post"),
            "word_count": len((state.get("blog_content") or "").split()),
        }
        return {
            "output": output,
            "status": "completed",
        }

    # ── Public API ──

    def invoke(
        self, input_data: dict, config: dict | None = None
    ) -> BlogGenerationState:
        """Run the full blog post generation pipeline."""
        initial: BlogGenerationState = {
            "input": input_data,
            "messages": [],
            "status": "initialized",
        }
        if config and self.checkpointer:
            return cast(
                BlogGenerationState,
                self.graph.invoke(initial, config),
            )
        return cast(
            BlogGenerationState,
            self.graph.invoke(initial),
        )

    # ── Helpers ──

    @staticmethod
    def _extract_title(content: str) -> str:
        """Extract the blog title from the generated content."""
        match = re.search(r"^##\s+Title\s*\n(.+)", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        # Fallback: first non-empty line
        for line in content.strip().split("\n"):
            line = line.strip().strip("#").strip()
            if line and len(line) > 10:
                return line
        return ""

    @staticmethod
    def _extract_meta_description(content: str) -> str:
        """Extract the meta description from the generated content."""
        match = re.search(r"##\s+Meta Description\s*\n(.+)", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return ""

    @staticmethod
    def _generate_slug(title: str) -> str:
        """Generate a URL-friendly slug from a title."""
        slug = title.lower().strip()
        # Replace non-word chars with a space (keeps words separated)
        slug = re.sub(r"[^\w\s]", " ", slug)
        # Collapse whitespace to a single hyphen
        slug = re.sub(r"\s+", "-", slug)
        # Strip leading/trailing hyphens
        return slug.strip("-")

    @staticmethod
    def _extract_tags(inp: dict[str, Any]) -> list[str]:
        """Extract tags from input data."""
        tags = inp.get("tags", inp.get("keywords", ""))
        if isinstance(tags, str):
            return [t.strip() for t in tags.split(",") if t.strip()]
        if isinstance(tags, list):
            return tags
        return []


def _error_state(message: str) -> BlogGenerationState:
    """Create a state dict with an error."""
    return {
        "error": message,
        "status": "failed",
        "blog_content": None,
        "blog_post": None,
        "output": None,
    }
