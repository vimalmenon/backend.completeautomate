"""Tests for prompt template rendering across all PromptTaskEnum tasks.

This test suite verifies that every prompt template in the system:
  - Renders without Jinja2 TemplateError when given valid data
  - Handles optional template variables gracefully
  - Fails on missing required variables (StrictUndefined)
  - Injects few-shot examples correctly
"""

from unittest.mock import patch
from uuid import UUID, uuid4

import pytest

from backend.data import PromptDBData
from backend.data.prompt import PromptVersionDBData
from backend.enum import AIModelEnum
from backend.enum.prompt import PromptTaskEnum
from backend.services.agent_service import AgentService

# ── Mock prompt templates ──────────────────────────────────────────────
# These test templates exercise ALL template variables each task expects.
# The actual DB templates are richer, but the variable set is the same.

MOCK_VIDEO_SUMMARY_TEMPLATE = (
    "Summarize this transcript:\n\n{{ transcript }}\n\n"
    "{% if user_message %}Extra instructions: {{ user_message }}{% endif %}"
)

MOCK_VIDEO_SUMMARY_SYSTEM = (
    "You are a YouTube transcript summarizer.\n"
    "{% if user_message %}Follow: {{ user_message }}{% endif %}"
)

MOCK_METADATA_TEMPLATE = (
    "Given transcript: {{ transcript }}\n\n"
    "{% if user_message %}User request: {{ user_message }}{% endif %}\n"
    "Suggest: title, description, tags, category."
)

MOCK_COMMUNITY_POST_TEMPLATE = (
    "Create a YouTube community post for:\n"
    "Title: {{ title }}\n"
    "Description: {{ description }}\n"
    "Summary: {{ video_summary }}"
)

MOCK_THUMBNAIL_TEMPLATE = MOCK_COMMUNITY_POST_TEMPLATE  # Same data shape
MOCK_TWITTER_POST_TEMPLATE = (
    "Draft a Twitter/X thread for this video:\n"
    "Title: {{ title }}\n"
    "Description: {{ description }}"
)
MOCK_SHORT_SPEECH_TEMPLATE = (
    "Write a 60-second short script about {{ topic }}.\n\n"
    "Reference transcript:\n{{ transcript }}"
)

MOCK_BLOG_TEMPLATE = (
    "Topic: {{ topic }}\nAudience: {{ audience }}\nTone: {{ tone }}\n"
    "Word count: {{ word_count }}\n"
    "{% if keywords %}Keywords: {{ keywords }}{% endif %}\n"
    "{% if outline %}Outline: {{ outline }}{% endif %}"
)

MOCK_EVALUATION_TEMPLATE = (
    "Prompt: {{ prompt }}\nInput: {{ test_data }}\nOutput: {{ response }}\n"
    "Score 0-100."
)

MOCK_IMPROVEMENT_TEMPLATE = (
    "Current: {{ prompt }}\nSystem: {{ system_message }}\n"
    "Eval: {{ eval_summary }}\n\n"
    "Generate NEW_PROMPT / NEW_SYSTEM_MESSAGE / REFLECTION."
)


# ── Test data fixtures per task ────────────────────────────────────────

@pytest.fixture
def default_task_id() -> str:
    return "test-task-1234"


@pytest.fixture
def video_summary_prompt() -> PromptDBData:
    return PromptDBData(
        task=PromptTaskEnum.YouTubeVideoSummarization,
        description="Summarize a transcript",
        active_version=uuid4(),
        prompt=MOCK_VIDEO_SUMMARY_TEMPLATE,
        system_message=MOCK_VIDEO_SUMMARY_SYSTEM,
        ai=AIModelEnum.Grok,
        comment="",
    )


@pytest.fixture
def video_summary_data() -> dict:
    return {"transcript": "A long video about AI agents", "user_message": "Keep it concise"}


@pytest.fixture
def metadata_prompt() -> PromptDBData:
    return PromptDBData(
        task=PromptTaskEnum.YouTubeVideoMetadata,
        description="Suggest metadata",
        active_version=uuid4(),
        prompt=MOCK_METADATA_TEMPLATE,
        system_message="You are a YouTube SEO expert.",
        ai=AIModelEnum.Grok,
    )


@pytest.fixture
def metadata_data() -> dict:
    return {"transcript": "Introduction to machine learning", "user_message": "Focus on beginners"}


@pytest.fixture
def community_post_prompt() -> PromptDBData:
    return PromptDBData(
        task=PromptTaskEnum.YouTubeVideoCommunityPost,
        description="Generate community post",
        active_version=uuid4(),
        prompt=MOCK_COMMUNITY_POST_TEMPLATE,
        system_message="You are a YouTube community manager.",
        ai=AIModelEnum.Grok,
    )


@pytest.fixture
def community_post_data() -> dict:
    return {
        "title": "How to build a chatbot",
        "description": "Full tutorial on building chatbots with Python",
        "video_summary": "We built a chatbot using LangChain and OpenAI",
    }


@pytest.fixture
def thumbnail_prompt() -> PromptDBData:
    return PromptDBData(
        task=PromptTaskEnum.YouTubeThumbnailImageGenerationPrompt,
        description="Generate thumbnail prompt",
        active_version=uuid4(),
        prompt=MOCK_THUMBNAIL_TEMPLATE,
        system_message="You are a thumbnail designer.",
        ai=AIModelEnum.Grok,
    )


@pytest.fixture
def short_speech_prompt() -> PromptDBData:
    return PromptDBData(
        task=PromptTaskEnum.YouTubeShortSpeechGenerationPrompt,
        description="Generate short script",
        active_version=uuid4(),
        prompt=MOCK_SHORT_SPEECH_TEMPLATE,
        system_message="You are a short-form script writer.",
        ai=AIModelEnum.Grok,
    )


@pytest.fixture
def short_speech_data() -> dict:
    return {
        "topic": "RAG vs Fine-tuning",
        "transcript": "RAG retrieves documents, fine-tuning updates weights...",
    }


@pytest.fixture
def twitter_post_prompt() -> PromptDBData:
    return PromptDBData(
        task=PromptTaskEnum.YouTubeVideoTwitterPost,
        description="Generate Twitter thread",
        active_version=uuid4(),
        prompt=MOCK_TWITTER_POST_TEMPLATE,
        system_message="You are a social media strategist.",
        ai=AIModelEnum.Grok,
    )


@pytest.fixture
def twitter_post_data() -> dict:
    return {
        "title": "RAG vs Fine-tuning explained",
        "description": "A detailed comparison of two popular LLM techniques",
    }


@pytest.fixture
def blog_prompt() -> PromptDBData:
    return PromptDBData(
        task=PromptTaskEnum.BlogPostGenerationPrompt,
        description="Write blog post",
        active_version=uuid4(),
        prompt=MOCK_BLOG_TEMPLATE,
        system_message="You are an expert blog writer.",
        ai=AIModelEnum.Grok,
    )


@pytest.fixture
def blog_data() -> dict:
    return {
        "topic": "Prompt Engineering",
        "audience": "Developers",
        "tone": "Professional",
        "word_count": "1500",
        "keywords": "prompt engineering, LLM",
        "outline": "1. Intro 2. Techniques 3. Conclusion",
    }


@pytest.fixture
def evaluation_prompt() -> PromptDBData:
    return PromptDBData(
        task=PromptTaskEnum.PromptEvaluation,
        description="Evaluate prompt output",
        active_version=uuid4(),
        prompt=MOCK_EVALUATION_TEMPLATE,
        system_message="You are a prompt evaluation expert.",
        ai=AIModelEnum.Grok,
    )


@pytest.fixture
def evaluation_data() -> dict:
    return {
        "prompt": "Summarize: {{ transcript }}",
        "test_data": "transcript=AI video",
        "response": "This video covers AI basics.",
    }


@pytest.fixture
def improvement_prompt() -> PromptDBData:
    return PromptDBData(
        task=PromptTaskEnum.PromptImprovement,
        description="Improve prompt",
        active_version=uuid4(),
        prompt=MOCK_IMPROVEMENT_TEMPLATE,
        system_message="You are a prompt engineering expert.",
        ai=AIModelEnum.Grok,
    )


@pytest.fixture
def improvement_data() -> dict:
    return {
        "prompt": "Summarize: {{ transcript }}",
        "system_message": "You are a summarizer.",
        "eval_summary": "Score: 65/100. Missing clarity.",
    }


# ── Task-to-test-data registry for parameterized tests ─────────────────

TASK_TEST_DATA: list[tuple[PromptTaskEnum, str, str]] = [
    (
        PromptTaskEnum.YouTubeVideoSummarization,
        "video_summary_prompt",
        "video_summary_data",
    ),
    (
        PromptTaskEnum.YouTubeVideoMetadata,
        "metadata_prompt",
        "metadata_data",
    ),
    (
        PromptTaskEnum.YouTubeVideoCommunityPost,
        "community_post_prompt",
        "community_post_data",
    ),
    (
        PromptTaskEnum.YouTubeThumbnailImageGenerationPrompt,
        "thumbnail_prompt",
        "community_post_data",
    ),
    (
        PromptTaskEnum.YouTubeShortSpeechGenerationPrompt,
        "short_speech_prompt",
        "short_speech_data",
    ),
    (
        PromptTaskEnum.YouTubeVideoTwitterPost,
        "twitter_post_prompt",
        "twitter_post_data",
    ),
    (
        PromptTaskEnum.BlogPostGenerationPrompt,
        "blog_prompt",
        "blog_data",
    ),
    (
        PromptTaskEnum.PromptEvaluation,
        "evaluation_prompt",
        "evaluation_data",
    ),
    (
        PromptTaskEnum.PromptImprovement,
        "improvement_prompt",
        "improvement_data",
    ),
]


# ── Helper ─────────────────────────────────────────────────────────────

def _agent_service_with_mock_db(
    task: PromptTaskEnum,
    prompt_db_data: PromptDBData,
    data: dict,
    task_id: str = "test-helper-0000",
) -> AgentService:
    """Return an AgentService whose PromptDB.get_prompt_by_task returns the given data."""
    with patch("backend.services.agent_service.PromptDB") as mock_db_cls:
        mock_db = mock_db_cls.return_value
        mock_db.get_prompt_by_task.return_value = prompt_db_data
        service = AgentService(prompt_task=task, task_id=task_id, data=data)
    return service


# ── Tests ──────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestPromptTemplateRendering:
    """Verify every prompt template renders without errors."""

    @pytest.mark.parametrize(
        "task, prompt_fixture_name, data_fixture_name",
        [
            pytest.param(t, p, d, id=t.value)
            for t, p, d in TASK_TEST_DATA
        ],
    )
    def test_all_templates_render(
        self,
        request: pytest.FixtureRequest,
        task: PromptTaskEnum,
        prompt_fixture_name: str,
        data_fixture_name: str,
    ) -> None:
        prompt_db_data: PromptDBData = request.getfixturevalue(prompt_fixture_name)
        data: dict = request.getfixturevalue(data_fixture_name)

        service = _agent_service_with_mock_db(task, prompt_db_data, data)

        rendered_system = service.get_system_message()
        rendered_prompt = service.get_prompt()

        assert isinstance(rendered_system, str)
        assert len(rendered_system) > 0
        assert isinstance(rendered_prompt, str)
        assert len(rendered_prompt) > 0

        # Verify data variables are present in the rendered output
        for key, value in data.items():
            if isinstance(value, str) and len(value) > 10:
                assert value in rendered_prompt or value in rendered_system, (
                    f"Variable '{key}' value not found in rendered output"
                )


@pytest.mark.unit
class TestOptionalVariables:
    """Test that optional template variables ({% if var %}) can be omitted."""

    @staticmethod
    def _make_blog_prompt(include_optional: bool) -> PromptDBData:
        template = (
            "Topic: {{ topic }}\nAudience: {{ audience }}\n"
            "{% if keywords %}Keywords: {{ keywords }}{% endif %}"
        )
        if include_optional:
            template += "\n{% if outline %}Outline: {{ outline }}{% endif %}"
        return PromptDBData(
            task=PromptTaskEnum.BlogPostGenerationPrompt,
            description="Blog",
            active_version=uuid4(),
            prompt=template,
            system_message="You are a writer.",
            ai=AIModelEnum.Grok,
        )

    def test_optional_variable_omitted(self) -> None:
        """Omitting optional vars with empty string should render without the block."""
        prompt = self._make_blog_prompt(include_optional=True)
        data = {"topic": "AI", "audience": "Devs", "keywords": "", "outline": ""}

        service = _agent_service_with_mock_db(
            PromptTaskEnum.BlogPostGenerationPrompt, prompt, data
        )

        result = service.get_prompt()
        assert "Topic: AI" in result
        assert "Outline:" not in result  # Empty string, not in {% if %} block
        assert "Keywords:" not in result  # Same

    def test_optional_variable_provided(self) -> None:
        """Providing optional variables should render them."""
        prompt = self._make_blog_prompt(include_optional=True)
        data = {"topic": "AI", "audience": "Devs", "keywords": "LLM, RAG", "outline": ""}

        service = _agent_service_with_mock_db(
            PromptTaskEnum.BlogPostGenerationPrompt, prompt, data
        )

        result = service.get_prompt()
        assert "Keywords: LLM, RAG" in result


@pytest.mark.unit
class TestMissingRequiredVariable:
    """StrictUndefined should raise on missing required variables."""

    def test_missing_required_raises(self) -> None:
        prompt = PromptDBData(
            task=PromptTaskEnum.YouTubeVideoSummarization,
            description="Summary",
            active_version=uuid4(),
            prompt="Transcript: {{ transcript }}",
            system_message="System: {{ required_var }}",
            ai=AIModelEnum.Grok,
        )
        data = {"transcript": "Some transcript"}  # Missing 'required_var'

        service = _agent_service_with_mock_db(
            PromptTaskEnum.YouTubeVideoSummarization, prompt, data
        )

        # System message has an unfulfilled required var → should raise
        with pytest.raises(Exception, match="undefined"):
            service.get_system_message()

    def test_empty_string_allowed_for_required(self) -> None:
        """Empty strings are VALID values, not 'undefined'."""
        prompt = PromptDBData(
            task=PromptTaskEnum.YouTubeVideoSummarization,
            description="Summary",
            active_version=uuid4(),
            prompt="Transcript: {{ transcript }}",
            system_message="System message",
            ai=AIModelEnum.Grok,
        )
        data = {"transcript": ""}  # Empty string, not missing

        service = _agent_service_with_mock_db(
            PromptTaskEnum.YouTubeVideoSummarization, prompt, data
        )

        result = service.get_prompt()
        assert "Transcript:" in result


@pytest.mark.unit
class TestExamplesInjection:
    """Few-shot examples should be appended to the rendered prompt."""

    def test_examples_appended(self) -> None:
        """Examples from PromptDBData should appear in the final rendered output."""
        examples: list[dict] = [
            {"input": "Example topic 1", "output": "Summary 1"},
            {"input": "Example topic 2", "output": "Summary 2"},
        ]

        prompt = PromptDBData(
            task=PromptTaskEnum.YouTubeVideoSummarization,
            description="Summary",
            active_version=uuid4(),
            prompt="Transcript: {{ transcript }}",
            system_message="System message",
            ai=AIModelEnum.Grok,
            examples=examples,
        )
        data = {"transcript": "Test transcript"}

        service = _agent_service_with_mock_db(
            PromptTaskEnum.YouTubeVideoSummarization, prompt, data
        )

        result = service.get_prompt()

        assert "Few-shot Examples:" in result
        assert "Example 1 Input: Example topic 1" in result
        assert "Example 1 Output: Summary 1" in result
        assert "Example 2 Input: Example topic 2" in result
        assert "Example 2 Output: Summary 2" in result

    def test_no_examples_when_list_empty(self) -> None:
        """Empty examples list should not inject anything."""
        prompt = PromptDBData(
            task=PromptTaskEnum.YouTubeVideoSummarization,
            description="Summary",
            active_version=uuid4(),
            prompt="Transcript: {{ transcript }}",
            system_message="System message",
            ai=AIModelEnum.Grok,
            examples=[],
        )

        service = _agent_service_with_mock_db(
            PromptTaskEnum.YouTubeVideoSummarization, prompt, {"transcript": "Test"}
        )

        result = service.get_prompt()
        assert "Few-shot Examples:" not in result

    def test_no_examples_when_none(self) -> None:
        """None examples should not inject anything."""
        prompt = PromptDBData(
            task=PromptTaskEnum.YouTubeVideoSummarization,
            description="Summary",
            active_version=uuid4(),
            prompt="Transcript: {{ transcript }}",
            system_message="System message",
            ai=AIModelEnum.Grok,
        )

        service = _agent_service_with_mock_db(
            PromptTaskEnum.YouTubeVideoSummarization, prompt, {"transcript": "Test"}
        )

        result = service.get_prompt()
        assert "Few-shot Examples:" not in result


@pytest.mark.unit
class TestAllPromptTasksCovered:
    """Ensure every PromptTaskEnum has a corresponding test fixture."""

    def test_every_task_has_test_data(self) -> None:
        """Fail if a new PromptTaskEnum is added without test coverage."""
        tested_tasks = {t for t, _, _ in TASK_TEST_DATA}
        all_tasks = set(PromptTaskEnum)

        missing = all_tasks - tested_tasks
        assert not missing, (
            f"PromptTaskEnum values without test coverage: "
            f"{[m.value for m in sorted(missing, key=lambda x: x.value)]}"
        )


@pytest.mark.unit
class TestEdgeCases:
    """Edge cases: empty strings, null-like values, very long input."""

    @pytest.mark.parametrize(
        "data",
        [
            {"transcript": "", "user_message": ""},
            {"transcript": "A" * 10_000, "user_message": "Keep it short"},
        ],
        ids=["empty strings", "very long transcript"],
    )
    def test_summarization_edge_cases(self, data: dict) -> None:
        prompt = PromptDBData(
            task=PromptTaskEnum.YouTubeVideoSummarization,
            description="Summary",
            active_version=uuid4(),
            prompt=MOCK_VIDEO_SUMMARY_TEMPLATE,
            system_message=MOCK_VIDEO_SUMMARY_SYSTEM,
            ai=AIModelEnum.Grok,
        )
        service = _agent_service_with_mock_db(
            PromptTaskEnum.YouTubeVideoSummarization, prompt, data
        )
        rendered_prompt = service.get_prompt()
        rendered_system = service.get_system_message()
        assert isinstance(rendered_prompt, str)
        assert isinstance(rendered_system, str)

    def test_seed_prompt_evaluation_renders(self) -> None:
        """Test the actual seed template for PromptEvaluation with realistic data."""
        from backend.manager.prompt_manager import PromptManager

        # The seed prompts are created by PromptManager.seed_default_prompts()
        # but in tests we mock DB, so construct a PromptDBData matching the seed
        seed_template = (
            "Original Prompt: {{ prompt }}\n\n"
            "Input Data: {{ test_data }}\n\n"
            "AI Output: {{ response }}\n\n"
            "Score based on:\n"
            "- Relevance (0-25): Does the output match the expected format and context?\n"
            "- Completeness (0-25): Does it use all required variables and produce complete output?\n"
            "- Clarity (0-25): Is the language clear and unambiguous?\n"
            "- Structure (0-25): Is the output well-organized and easy to parse?\n\n"
            "Return ONLY a number between 0 and 100 representing the total score."
        )
        prompt = PromptDBData(
            task=PromptTaskEnum.PromptEvaluation,
            description="Evaluate prompt output quality on a 0-100 scale",
            active_version=uuid4(),
            prompt=seed_template,
            system_message=(
                "You are a prompt evaluation expert. "
                "Score the following prompt's output on a scale of 0-100."
            ),
            ai=AIModelEnum.Grok,
        )
        data = {
            "prompt": "Summarize this: {{ transcript }}",
            "test_data": "transcript='AI video about agents'",
            "response": "This video discusses AI agents and their applications.",
        }

        service = _agent_service_with_mock_db(
            PromptTaskEnum.PromptEvaluation, prompt, data
        )
        rendered_prompt = service.get_prompt()
        rendered_system = service.get_system_message()

        assert "Original Prompt:" in rendered_prompt
        assert "Input Data:" in rendered_prompt
        assert "AI Output:" in rendered_prompt
        assert "Score based on:" in rendered_prompt
        assert "prompt evaluation expert" in rendered_system
