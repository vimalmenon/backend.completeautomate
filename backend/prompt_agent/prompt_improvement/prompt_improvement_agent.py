"""Agent for improving prompt templates based on evaluation results.

Uses the Prompt Agent system (DB-stored prompts rendered via Jinja2)
instead of hardcoded improvement prompts.
"""

from uuid import UUID

from backend.enum import PromptTaskEnum
from backend.integration import GeneralAgent
from backend.services.agent_service import AgentService

_DEFAULT_SYSTEM_MESSAGE = """You are a prompt engineering expert. Improve the following prompt based on evaluation results."""

_DEFAULT_PROMPT = """Current Prompt: {{ prompt }}

Current System Message: {{ system_message }}

Evaluation Results:
{{ eval_summary }}

Generate an improved version that addresses weaknesses. Return your response in this exact format:

NEW_PROMPT:
<the improved prompt template>

NEW_SYSTEM_MESSAGE:
<the improved system message>

REFLECTION:
<brief explanation of what you changed and why>"""


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

    @staticmethod
    def default_prompt() -> str:
        return _DEFAULT_PROMPT

    @staticmethod
    def default_system_message() -> str:
        return _DEFAULT_SYSTEM_MESSAGE
