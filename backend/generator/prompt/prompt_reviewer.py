import logging
from uuid import UUID, uuid4

from backend.data import PromptDBData, PromptResultDBData
from backend.enum import JobsStatusEnum
from backend.generator.base_generator import BaseGenerator
from backend.manager import PromptManager
from backend.prompt_agent import (
    PromptEvaluationAgent,
    PromptImprovementAgent,
)

logger = logging.getLogger(__name__)


class PromptReviewer(BaseGenerator):
    """Evaluates all prompts against their test data and generates improvements.

    Uses the Prompt Agent system for both the evaluation (scoring) and
    improvement (reflection) meta-prompts — no hardcoded prompts.
    """

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
        from backend.integration import GeneralAgent
        from backend.services.agent_service import AgentService

        service = AgentService(
            prompt_task=prompt.task,
            task_id=f"{self.job.id}_eval_{uuid4()}",
            data=test_data,
        )
        agent = GeneralAgent(service)
        result = agent.invoke()
        ai_response = result["messages"][-1].content

        # Score the response using the Prompt Evaluation meta-agent
        score = self.__score_response(
            prompt_text=prompt.prompt,
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
        prompt_text: str,
        response: str,
        test_data: dict,
    ) -> int:
        """Score a prompt's output using the PromptEvaluationAgent.

        The evaluation prompt is stored in the Prompt Agent DB, not hardcoded.
        """
        try:
            eval_agent = PromptEvaluationAgent(
                job_id=UUID(str(self.job.id)[:36]),
                data={
                    "prompt": prompt_text,
                    "response": response,
                    "test_data": str(test_data),
                },
            )
            raw = eval_agent.generate()
            score = PromptEvaluationAgent.parse_score(raw)
            eval_agent.clean_up()
            return score
        except Exception:
            logger.exception("Failed to score response, defaulting to 50")
            return 50

    def __generate_improvement(
        self, prompt: PromptDBData, results: list[PromptResultDBData]
    ) -> None:
        """Generate an improved version of a prompt using PromptImprovementAgent.

        The improvement prompt is stored in the Prompt Agent DB, not hardcoded.
        """
        eval_summary = "\n".join(
            f"Test data: {r.prompt_data_snapshot}\nScore: {r.score}\nResponse: {r.response[:200]}..."
            for r in results
        )

        try:
            improvement_agent = PromptImprovementAgent(
                job_id=UUID(str(self.job.id)[:36]),
                data={
                    "prompt": prompt.prompt,
                    "system_message": prompt.system_message,
                    "eval_summary": eval_summary,
                },
            )
            improvement_text = improvement_agent.generate()

            new_prompt = PromptImprovementAgent.extract_section(
                improvement_text, "NEW_PROMPT"
            )
            new_system_message = PromptImprovementAgent.extract_section(
                improvement_text, "NEW_SYSTEM_MESSAGE"
            )
            reflect_message = PromptImprovementAgent.extract_section(
                improvement_text, "REFLECTION"
            )

            improvement_agent.clean_up()

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
