"""Agent for evaluating prompt output quality on a 0-100 scale.

Uses the Prompt Agent system (DB-stored prompts rendered via Jinja2)
instead of hardcoded evaluation prompts.
"""

from uuid import UUID

from backend.enum import PromptTaskEnum
from backend.integration import GeneralAgent
from backend.services.agent_service import AgentService


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
