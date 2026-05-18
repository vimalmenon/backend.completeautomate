"""Agent for generating blog posts using the prompt agent system.

Uses the Prompt Agent system (DB-stored prompts rendered via Jinja2)
to generate structured blog post content from topic, audience, and tone data.
"""

from uuid import UUID

from backend.enum import PromptTaskEnum
from backend.integration import GeneralAgent
from backend.services.agent_service import AgentService


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
