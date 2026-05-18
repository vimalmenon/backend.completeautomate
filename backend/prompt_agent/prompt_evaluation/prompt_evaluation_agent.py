"""Agent for evaluating prompt output quality on a 0-100 scale.

Uses the Prompt Agent system (DB-stored prompts rendered via Jinja2)
instead of hardcoded evaluation prompts.
"""

from uuid import UUID

from backend.enum import PromptTaskEnum
from backend.integration import GeneralAgent
from backend.services.agent_service import AgentService

_DEFAULT_SYSTEM_MESSAGE = """You are a prompt evaluation expert. Score the following prompt's output on a scale of 0-100."""

_DEFAULT_PROMPT = """Original Prompt: {{ prompt }}

Input Data: {{ test_data }}

AI Output: {{ response }}

Score based on:
- Relevance (0-25): Does the output match the expected format and context?
- Completeness (0-25): Does it use all required variables and produce complete output?
- Clarity (0-25): Is the language clear and unambiguous?
- Structure (0-25): Is the output well-organized and easy to parse?

Return ONLY a number between 0 and 100 representing the total score."""


class PromptEvaluationAgent:
    task = PromptTaskEnum.PromptEvaluation

    def __init__(self, job_id: UUID, data: dict):
        self.service = AgentService(
            prompt_task=self.task,
            task_id=f"{job_id}_eval_score",
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
    def parse_score(raw: str) -> int:
        """Extract the numeric score from the model response.

        Takes the first contiguous number found — avoids the old bug
        where '85 out of 100' would extract '85100' and clamp to 100.
        """
        import re

        match = re.search(r"\d+", raw.strip())
        if match:
            score = int(match.group())
            return max(0, min(100, score))
        return 50

    @staticmethod
    def default_prompt() -> str:
        return _DEFAULT_PROMPT

    @staticmethod
    def default_system_message() -> str:
        return _DEFAULT_SYSTEM_MESSAGE
