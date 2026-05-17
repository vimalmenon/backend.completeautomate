import logging
from uuid import uuid4

from backend.ai.text_generation.grok_ai import GrokAI
from backend.data import PromptDBData, PromptResultDBData
from backend.enum import JobsStatusEnum
from backend.generator.base_generator import BaseGenerator
from backend.manager import PromptManager

logger = logging.getLogger(__name__)

_EVALUATION_LLM = GrokAI().get_model()


class PromptReviewer(BaseGenerator):
    """Evaluates all prompts against their test data and generates improvements."""

    def __init__(self, job):
        super().__init__(job)
        self.prompt_manager = PromptManager()

    def generate(self) -> tuple[JobsStatusEnum, dict | None]:
        logger.info("Starting prompt review for job %s", self.job.id)
        prompts = self.prompt_manager.get_prompts()
        for prompt in prompts:
            self.process_prompt(prompt=prompt)
        logger.info("Completed prompt review for job %s", self.job.id)
        return JobsStatusEnum.IN_PROGRESS, None

    def process_prompt(self, prompt: PromptDBData) -> None:
        if not prompt.prompt_data:
            logger.info(
                "Skipping prompt %s — no test data available", prompt.task.value
            )
            return

        logger.info(
            "Evaluating prompt %s with %s test data sets",
            prompt.task.value,
            len(prompt.prompt_data),
        )
        results: list[PromptResultDBData] = []
        for test_data in prompt.prompt_data:
            try:
                result = self.__evaluate_test_data(prompt, test_data)
                if result:
                    self.prompt_manager.add_result(result)
                    results.append(result)
            except Exception:
                logger.exception(
                    "Failed to evaluate test data for prompt %s", prompt.task.value
                )

        if not results:
            logger.info("No successful evaluations for prompt %s", prompt.task.value)
            return

        avg_score = sum(r.score or 0 for r in results) / len(results)
        logger.info(
            "Prompt %s average score: %.1f/100 across %s evaluations",
            prompt.task.value,
            avg_score,
            len(results),
        )

        if avg_score < 80:
            logger.info(
                "Prompt %s score below 80 — generating improvement",
                prompt.task.value,
            )
            self.__generate_improvement(prompt, results)

    def __evaluate_test_data(
        self, prompt: PromptDBData, test_data: dict
    ) -> PromptResultDBData | None:
        from backend.services.agent_service import AgentService
        from backend.integration import GeneralAgent
        from backend.ai.text_generation.grok_ai import GrokAI

        service = AgentService(
            prompt_task=prompt.task,
            task_id=f"{self.job.id}_eval_{uuid4()}",
            data=test_data,
        )
        agent = GeneralAgent(service)
        result = agent.invoke()
        ai_response = result["messages"][-1].content

        score = self.__score_response(
            prompt=prompt.prompt,
            response=ai_response,
            test_data=test_data,
        )

        agent.clean_up_messages()
        return PromptResultDBData(
            task=prompt.task,
            result_id=uuid4(),
            version=prompt.active_version,
            response=ai_response,
            score=score,
            prompt_data_snapshot=test_data,
        )

    def __score_response(
        self,
        prompt: str,
        response: str,
        test_data: dict,
    ) -> int:
        scoring_prompt = f"""You are a prompt evaluation expert. Score the following prompt's output on a scale of 0-100.

Original Prompt: {prompt}

Input Data: {test_data}

AI Output: {response}

Score based on:
- Relevance (0-25): Does the output match the expected format and context?
- Completeness (0-25): Does it use all required variables and produce complete output?
- Clarity (0-25): Is the language clear and unambiguous?
- Structure (0-25): Is the output well-organized and easy to parse?

Return ONLY a number between 0 and 100 representing the total score."""

        try:
            score_result = _EVALUATION_LLM.invoke(scoring_prompt)
            score_text = score_result.content.strip()
            score = int("".join(c for c in score_text if c.isdigit()))
            return max(0, min(100, score))
        except Exception:
            logger.exception("Failed to score response, defaulting to 50")
            return 50

    def __generate_improvement(
        self, prompt: PromptDBData, results: list[PromptResultDBData]
    ) -> None:
        from backend.ai.text_generation.grok_ai import GrokAI

        eval_summary = "\n".join(
            f"Test data: {r.prompt_data_snapshot}\nScore: {r.score}\nResponse: {r.response[:200]}..."
            for r in results
        )

        reflection_prompt = f"""You are a prompt engineering expert. Improve the following prompt based on evaluation results.

Current Prompt: {prompt.prompt}

Current System Message: {prompt.system_message}

Evaluation Results:
{eval_summary}

Generate an improved version that addresses weaknesses. Return your response in this exact format:

NEW_PROMPT:
<the improved prompt template>

NEW_SYSTEM_MESSAGE:
<the improved system message>

REFLECTION:
<brief explanation of what you changed and why>"""

        try:
            improvement_result = _EVALUATION_LLM.invoke(reflection_prompt)
            improvement_text = improvement_result.content

            new_prompt = self.__extract_section(improvement_text, "NEW_PROMPT")
            new_system_message = self.__extract_section(
                improvement_text, "NEW_SYSTEM_MESSAGE"
            )
            reflect_message = self.__extract_section(improvement_text, "REFLECTION")

            if new_prompt and new_system_message:
                from backend.data.api import PromptUpdateResult

                self.prompt_manager.update_prompt(
                    task=prompt.task,
                    data=PromptUpdateResult(
                        task=prompt.task,
                        description=prompt.description,
                        prompt=new_prompt,
                        system_message=new_system_message,
                        ai=prompt.ai,
                        comment=reflect_message,
                    ),
                )
                logger.info(
                    "Improved prompt %s with new version",
                    prompt.task.value,
                )
        except Exception:
            logger.exception(
                "Failed to generate improvement for prompt %s", prompt.task.value
            )

    @staticmethod
    def __extract_section(text: str, section_name: str) -> str | None:
        import re

        pattern = re.compile(rf"{section_name}:\s*(.*?)(?=\n[A-Z_]+:|\Z)", re.DOTALL)
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
        return None
