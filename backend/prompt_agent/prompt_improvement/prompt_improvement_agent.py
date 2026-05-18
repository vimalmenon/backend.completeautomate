"""Agent for improving prompt templates based on evaluation results.

Uses the Prompt Agent system (DB-stored prompts rendered via Jinja2)
instead of hardcoded improvement prompts.
"""

from uuid import UUID

from backend.enum import PromptTaskEnum
from backend.integration import GeneralAgent
from backend.services.agent_service import AgentService


class PromptImprovementAgent:
    task = PromptTaskEnum.PromptImprovement

    def __init__(self, job_id: UUID, data: dict):
        self.service = AgentService(
            prompt_task=self.task,
            task_id=f"{job_id}_improve",
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
    def extract_section(text: str, section_name: str) -> str | None:
        """Extract a named section from the improvement response."""
        import re

        pattern = re.compile(rf"{section_name}:\s*(.*?)(?=\n[A-Z_]+:|\Z)", re.DOTALL)
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
        return None
