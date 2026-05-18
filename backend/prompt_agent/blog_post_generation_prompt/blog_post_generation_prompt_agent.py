"""Agent for generating blog posts using the prompt agent system.

Uses the Prompt Agent system (DB-stored prompts rendered via Jinja2)
to generate structured blog post content from topic, audience, and tone data.
"""

from uuid import UUID

from backend.enum import PromptTaskEnum
from backend.integration import GeneralAgent
from backend.services.agent_service import AgentService

_DEFAULT_SYSTEM_MESSAGE = """You are an expert blog writer. Generate well-structured, engaging blog posts that balance depth with readability."""

_DEFAULT_PROMPT = """Write a blog post on the following topic.

Topic: {{ topic }}
Target Audience: {{ audience }}
Tone: {{ tone }}
Target Word Count: {{ word_count }}{% if keywords %}
SEO Keywords: {{ keywords }}{% endif %}{% if outline %}
Outline:
{{ outline }}{% endif %}{% if extra_context %}
Additional Context:
{{ extra_context }}{% endif %}

Your response must follow this structure:

## Title
<compelling blog title>

## Meta Description
<2-3 sentence SEO description>

## Table of Contents
<bullet list of main sections>

## Content
<full blog post with proper headings (##), subheadings (###), and paragraphs>

Guidelines:
- Use the specified tone throughout
- Include the SEO keywords naturally
- Break up text with headings every 2-3 paragraphs
- Write for the specified target audience
- Aim for the target word count
- Include a strong call-to-action in the conclusion"""


class BlogPostGenerationPromptAgent:
    task = PromptTaskEnum.BlogPostGenerationPrompt

    def __init__(self, job_id: UUID, data: dict):
        self.service = AgentService(
            prompt_task=self.task,
            task_id=f"{job_id}_blog_gen",
            data=data,
        )
        self.agent = GeneralAgent(self.service)

    def generate(self) -> str:
        result = self.agent.invoke()
        content: str = result["messages"][-1].content
        return content

    def clean_up(self) -> None:
        self.agent.clean_up_messages()

    @staticmethod
    def default_prompt() -> str:
        return _DEFAULT_PROMPT

    @staticmethod
    def default_system_message() -> str:
        return _DEFAULT_SYSTEM_MESSAGE
