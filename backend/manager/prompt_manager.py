import logging
from datetime import datetime
from uuid import UUID, uuid4

from backend.data import PromptDBData, PromptResultDBData, PromptVersionDBData
from backend.data.api import PromptUpdateResult
from backend.database import PromptDB, PromptResultDB, PromptVersionDB
from backend.enum import AIModelEnum, PromptTaskEnum
from backend.exception import AppException

logger = logging.getLogger(__name__)


class PromptManager:

    def get_prompt_by_task(self, task: PromptTaskEnum) -> PromptDBData | None:
        return PromptDB().get_prompt_by_task(task)

    def get_prompts(self) -> list[PromptDBData]:
        return PromptDB().get_all_prompts()

    def add_prompt(self, data: PromptDBData | PromptUpdateResult) -> PromptDBData:
        if isinstance(data, PromptDBData):
            PromptDB().save_prompt(data)
            version = PromptVersionDBData(
                task=data.task,
                version=data.active_version,
                prompt=data.prompt,
                system_message=data.system_message,
                reflect_message="",
                ai=data.ai,
                created_at=data.last_updated,
                examples=data.examples,
            )
            PromptVersionDB().save_version(data=version)
            return data

        task = PromptTaskEnum(data.task)
        existing_prompt = self.get_prompt_by_task(task=task)
        if existing_prompt is not None:
            raise AppException(f"Prompt already exists for task {task.value}")

        version_id = data.version or uuid4()
        created_at = datetime.now()
        examples = data.examples or []

        prompt = PromptDBData(
            task=task,
            description=data.description,
            active_version=version_id,
            prompt=data.prompt,
            system_message=data.system_message,
            ai=AIModelEnum(data.ai),
            comment=data.comment,
            last_updated=created_at,
            examples=examples,
        )

        version = PromptVersionDBData(
            task=task,
            version=version_id,
            prompt=data.prompt,
            system_message=data.system_message,
            reflect_message="",
            ai=AIModelEnum(data.ai),
            created_at=created_at,
            examples=examples,
        )

        PromptDB().save_prompt(data=prompt)
        PromptVersionDB().save_version(data=version)
        return prompt

    def update_prompt(
        self, task: PromptTaskEnum, data: PromptUpdateResult
    ) -> PromptDBData:
        existing = self.get_prompt_by_task(task=task)
        if existing is None:
            raise AppException(f"Prompt not found for task {task.value}")

        version_id = data.version or uuid4()
        created_at = datetime.now()
        examples = data.examples or existing.examples

        version = PromptVersionDBData(
            task=task,
            version=version_id,
            prompt=data.prompt,
            system_message=data.system_message,
            reflect_message="",
            ai=AIModelEnum(data.ai),
            created_at=created_at,
            examples=examples,
        )
        PromptVersionDB().save_version(data=version)

        updated_prompt = PromptDBData(
            task=task,
            description=data.description,
            active_version=version_id,
            prompt=data.prompt,
            system_message=data.system_message,
            ai=AIModelEnum(data.ai),
            comment=data.comment,
            last_updated=created_at,
            examples=examples,
        )
        PromptDB().update_prompt(prompt_task=task, values=updated_prompt.to_json())
        return updated_prompt

    def delete_prompt(self, prompt_task: PromptTaskEnum) -> None:
        PromptDB().delete_prompt(prompt_task=prompt_task)

    def get_version_history(self, task: PromptTaskEnum) -> list[PromptVersionDBData]:
        return PromptVersionDB().get_version_history(task)

    def get_version(
        self, task: PromptTaskEnum, version_id: UUID
    ) -> PromptVersionDBData | None:
        return PromptVersionDB().get_version(prompt_task=task, version_id=version_id)

    def rollback_prompt(self, task: PromptTaskEnum, version_id: UUID) -> PromptDBData:
        """Restore a prompt to a historical version.

        Creates a NEW version entry with the historical data so the rollback
        itself is recorded in the audit trail. Returns the updated prompt.
        """
        target = self.get_version(task=task, version_id=version_id)
        if target is None:
            raise AppException(f"Version {version_id} not found for task {task.value}")

        current = self.get_prompt_by_task(task=task)
        if current is None:
            raise AppException(f"Prompt not found for task {task.value}")

        # Create a new version to record this rollback
        new_version_id = uuid4()
        now = datetime.now()

        version = PromptVersionDBData(
            task=task,
            version=new_version_id,
            prompt=target.prompt,
            system_message=target.system_message,
            reflect_message=(
                f"Rolled back from version {current.active_version} "
                f"to version {version_id}"
            ),
            ai=target.ai,
            created_at=now,
            examples=target.examples,
        )
        PromptVersionDB().save_version(data=version)

        updated_prompt = PromptDBData(
            task=task,
            description=current.description,
            active_version=new_version_id,
            prompt=target.prompt,
            system_message=target.system_message,
            ai=target.ai,
            comment=current.comment,
            last_updated=now,
            examples=target.examples,
        )
        PromptDB().update_prompt(prompt_task=task, values=updated_prompt.to_json())
        return updated_prompt

    def add_result(self, data: PromptResultDBData) -> None:
        PromptResultDB().save_result(data)

    def get_results(self, task: PromptTaskEnum) -> list[PromptResultDBData]:
        return PromptResultDB().get_results_by_task(task)

    # ── Example Management ──

    def get_examples(self, task: PromptTaskEnum) -> list[dict]:
        prompt = self.get_prompt_by_task(task)
        if not prompt:
            raise AppException(f"Prompt not found for task {task.value}")
        return prompt.examples

    def add_example(self, task: PromptTaskEnum, example: dict) -> list[dict]:
        prompt = self.get_prompt_by_task(task)
        if not prompt:
            raise AppException(f"Prompt not found for task {task.value}")
        examples = prompt.examples + [example]
        PromptDB().update_prompt(
            prompt_task=task,
            values={"examples": examples},
        )
        return examples

    def remove_example(self, task: PromptTaskEnum, index: int) -> list[dict]:
        prompt = self.get_prompt_by_task(task)
        if not prompt:
            raise AppException(f"Prompt not found for task {task.value}")
        if index < 0 or index >= len(prompt.examples):
            raise AppException(
                f"Example index {index} out of range (0-{len(prompt.examples) - 1})"
            )
        examples = prompt.examples[:index] + prompt.examples[index + 1 :]
        PromptDB().update_prompt(
            prompt_task=task,
            values={"examples": examples},
        )
        return examples

    def clear_examples(self, task: PromptTaskEnum) -> None:
        prompt = self.get_prompt_by_task(task)
        if not prompt:
            raise AppException(f"Prompt not found for task {task.value}")
        PromptDB().update_prompt(
            prompt_task=task,
            values={"examples": []},
        )

    # ── Default Prompt Seeding ──

    def seed_default_prompts(self) -> None:
        """Create default prompt entries in DB if they don't exist yet.

        These are the meta-prompts for the prompt review/evaluation system
        (PromptEvaluation, PromptImprovement). Called once at startup.
        """
        defaults: list[PromptDBData] = [
            PromptDBData(
                task=PromptTaskEnum.BlogPostGenerationPrompt,
                description="Generate a blog post from topic, audience, and tone data",
                active_version=uuid4(),
                prompt=(
                    "Write a blog post on the following topic.\n\n"
                    "Topic: {{ topic }}\n"
                    "Target Audience: {{ audience }}\n"
                    "Tone: {{ tone }}\n"
                    "Target Word Count: {{ word_count }}"
                    "{% if keywords %}\nSEO Keywords: {{ keywords }}{% endif %}"
                    "{% if outline %}\nOutline:\n{{ outline }}{% endif %}"
                    "{% if extra_context %}\nAdditional Context:\n{{ extra_context }}{% endif %}\n\n"
                    "Your response must follow this structure:\n\n"
                    "## Title\n"
                    "<compelling blog title>\n\n"
                    "## Meta Description\n"
                    "<2-3 sentence SEO description>\n\n"
                    "## Table of Contents\n"
                    "<bullet list of main sections>\n\n"
                    "## Content\n"
                    "<full blog post with proper headings (##), subheadings (###), and paragraphs>\n\n"
                    "Guidelines:\n"
                    "- Use the specified tone throughout\n"
                    "- Include the SEO keywords naturally\n"
                    "- Break up text with headings every 2-3 paragraphs\n"
                    "- Write for the specified target audience\n"
                    "- Aim for the target word count\n"
                    "- Include a strong call-to-action in the conclusion"
                ),
                system_message=(
                    "You are an expert blog writer. "
                    "Generate well-structured, engaging blog posts "
                    "that balance depth with readability."
                ),
                ai=AIModelEnum.Grok,
            ),
            PromptDBData(
                task=PromptTaskEnum.PromptEvaluation,
                description="Evaluate prompt output quality on a 0-100 scale",
                active_version=uuid4(),
                prompt=(
                    "Original Prompt: {{ prompt }}\n\n"
                    "Input Data: {{ test_data }}\n\n"
                    "AI Output: {{ response }}\n\n"
                    "Score based on:\n"
                    "- Relevance (0-25): Does the output match the expected format and context?\n"
                    "- Completeness (0-25): Does it use all required variables and produce complete output?\n"
                    "- Clarity (0-25): Is the language clear and unambiguous?\n"
                    "- Structure (0-25): Is the output well-organized and easy to parse?\n\n"
                    "Return ONLY a number between 0 and 100 representing the total score."
                ),
                system_message=(
                    "You are a prompt evaluation expert. "
                    "Score the following prompt's output on a scale of 0-100."
                ),
                ai=AIModelEnum.Grok,
            ),
            PromptDBData(
                task=PromptTaskEnum.PromptImprovement,
                description="Improve a prompt template based on evaluation results",
                active_version=uuid4(),
                prompt=(
                    "Current Prompt: {{ prompt }}\n\n"
                    "Current System Message: {{ system_message }}\n\n"
                    "Evaluation Results:\n"
                    "{{ eval_summary }}\n\n"
                    "Generate an improved version that addresses weaknesses. "
                    "Return your response in this exact format:\n\n"
                    "NEW_PROMPT:\n"
                    "<the improved prompt template>\n\n"
                    "NEW_SYSTEM_MESSAGE:\n"
                    "<the improved system message>\n\n"
                    "REFLECTION:\n"
                    "<brief explanation of what you changed and why>"
                ),
                system_message=(
                    "You are a prompt engineering expert. "
                    "Improve the following prompt based on evaluation results."
                ),
                ai=AIModelEnum.Grok,
            ),
        ]

        for default in defaults:
            existing = self.get_prompt_by_task(default.task)
            if existing is None:
                logger.info("Seeding default prompt for %s", default.task.value)
                self.add_prompt(default)

    def set_examples(self, task: PromptTaskEnum, examples: list[dict]) -> list[dict]:
        prompt = self.get_prompt_by_task(task)
        if not prompt:
            raise AppException(f"Prompt not found for task {task.value}")
        PromptDB().update_prompt(
            prompt_task=task,
            values={"examples": examples},
        )
        return examples
