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
                task=PromptTaskEnum.YouTubeVideoSummarization,
                description="Summarize a YouTube video transcript with key insights",
                active_version=uuid4(),
                prompt=(
                    "Summarize the following YouTube video transcript.\n\n"
                    "Transcript:\n{{ transcript }}\n"
                    "{% if user_message %}\n"
                    "Additional Instructions: {{ user_message }}\n"
                    "{% endif %}\n\n"
                    "Your summary should:\n"
                    "- Capture the main topic and key points\n"
                    "- Be 3-5 paragraphs\n"
                    "- Highlight any actionable takeaways\n"
                    "- Keep a neutral, informative tone"
                ),
                system_message=(
                    "You are a YouTube transcript analyst. "
                    "Create clear, concise summaries that capture "
                    "the essence of video content."
                ),
                ai=AIModelEnum.Grok,
            ),
            PromptDBData(
                task=PromptTaskEnum.YouTubeVideoMetadata,
                description="Generate SEO metadata from a video transcript",
                active_version=uuid4(),
                prompt=(
                    "Generate SEO metadata for a YouTube video based on "
                    "its transcript.\n\n"
                    "Transcript:\n{{ transcript }}\n"
                    "{% if user_message %}\n"
                    "Additional Context: {{ user_message }}\n"
                    "{% endif %}\n\n"
                    "Return your analysis in this format:\n\n"
                    "**Title:** <SEO-optimized title, max 70 chars>\n\n"
                    "**Description:** <2-3 paragraph description with keywords>\n\n"
                    "**Tags:** <comma-separated tags, 5-10 tags>\n\n"
                    "**Category:** <best YouTube category for this video>"
                ),
                system_message=(
                    "You are a YouTube SEO expert. "
                    "Generate optimized metadata that improves "
                    "discoverability and click-through rates."
                ),
                ai=AIModelEnum.Grok,
            ),
            PromptDBData(
                task=PromptTaskEnum.YouTubeVideoCommunityPost,
                description="Create an engaging YouTube community post from video content",
                active_version=uuid4(),
                prompt=(
                    "Create 2-3 engaging YouTube Community posts for this video.\n\n"
                    "Title: {{ title }}\n"
                    "Description: {{ description }}\n"
                    "Video Summary: {{ video_summary }}\n\n"
                    "Each post should:\n"
                    "- Be 2-4 sentences\n"
                    "- Include a hook or question to drive engagement\n"
                    "- Mention the video\n"
                    "- Use emojis naturally\n"
                    "- End with a call to action\n\n"
                    "Separate each post with ---"
                ),
                system_message=(
                    "You are a YouTube community manager. "
                    "Write engaging posts that drive comments, likes, "
                    "and viewer interaction."
                ),
                ai=AIModelEnum.Grok,
            ),
            PromptDBData(
                task=PromptTaskEnum.YouTubeThumbnailImageGenerationPrompt,
                description="Generate image generation prompts for YouTube video thumbnails",
                active_version=uuid4(),
                prompt=(
                    "Create image generation prompts for a YouTube thumbnail.\n\n"
                    "Video Title: {{ title }}\n"
                    "Description: {{ description }}\n"
                    "Summary: {{ video_summary }}\n\n"
                    "Generate 3 image prompts that would make compelling "
                    "YouTube thumbnails. Each prompt should be detailed "
                    "enough for an AI image generator.\n\n"
                    "Return as a list with each prompt on a new line."
                ),
                system_message=(
                    "You are a YouTube thumbnail designer. "
                    "Create vivid, clickable image prompts "
                    "that capture the video's essence."
                ),
                ai=AIModelEnum.Grok,
            ),
            PromptDBData(
                task=PromptTaskEnum.YouTubeShortSpeechGenerationPrompt,
                description="Generate a speech script for a YouTube Short",
                active_version=uuid4(),
                prompt=(
                    "Write a 45-60 second speech script for a YouTube Short.\n\n"
                    "Topic: {{ topic }}\n"
                    "Reference Content:\n{{ transcript }}\n\n"
                    "Guidelines:\n"
                    "- Fast-paced, engaging tone\n"
                    "- Approximately 120-160 words\n"
                    "- Start with a hook in the first 3 seconds\n"
                    "- End with a call to action\n"
                    "- Use conversational language\n"
                    "- Include pauses [...] for natural flow\n"
                    "- Write the script as plain text, one paragraph"
                ),
                system_message=(
                    "You are a YouTube Shorts scriptwriter. "
                    "Write fast-paced, engaging scripts optimized "
                    "for vertical short-form video."
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
                task=PromptTaskEnum.YouTubeVideoTwitterPost,
                description=(
                    "Generate Twitter/X thread from a YouTube video's "
                    "title, description, and summary"
                ),
                active_version=uuid4(),
                prompt=(
                    "You are a social media strategist. Create an engaging "
                    "Twitter/X thread (2-5 tweets) for this YouTube video.\n\n"
                    "Title: {{ title }}\n"
                    "Description: {{ description }}\n"
                    "Video Summary: {{ video_summary }}\n\n"
                    "Guidelines:\n"
                    "- Open with a hook that grabs attention\n"
                    "- Each tweet should be under 280 characters\n"
                    "- Use line breaks and emojis naturally\n"
                    "- Include a call-to-action (watch the video, comment, retweet)\n"
                    "- Thread should feel like one cohesive story\n"
                    "- End with a question or discussion starter\n\n"
                    "Return each tweet separated by a blank line."
                ),
                system_message=(
                    "You are a social media strategist. "
                    "Write compelling Twitter/X threads that drive engagement."
                ),
                ai=AIModelEnum.Grok,
            ),
            PromptDBData(
                task=PromptTaskEnum.BlogTopicSuggestion,
                description=(
                    "Suggest blog topics from trending data, niche, and audience"
                ),
                active_version=uuid4(),
                prompt=(
                    "You are a content strategist. Given trending topics, a niche, "
                    "and target audience, suggest blog post ideas.\n\n"
                    "Trending Data:\n{{ trending_data }}\n\n"
                    "Niche: {{ niche }}\n"
                    "Target Audience: {{ audience }}\n"
                    "Tone: {{ tone }}\n\n"
                    "For each suggestion, pick topics that are:\n"
                    "- Relevant to the niche\n"
                    "- Timely (connected to current trends)\n"
                    "- Likely to perform well in search\n\n"
                    "Return a JSON array of objects with:\n"
                    '  - "title": the blog post title\n'
                    '  - "keywords": array of 3-5 SEO keywords\n'
                    '  - "description": 1-2 sentence summary\n'
                    '  - "audience": the target audience\n'
                    '  - "tone": the writing tone\n\n'
                    "Example:\n"
                    '[{"title": "Why AI Agents Are the Next Big Thing", '
                    '"keywords": ["AI agents", "autonomous AI", "agentic workflows"], '
                    '"description": "A deep dive into how AI agents are transforming industries", '
                    '"audience": "Developers and tech enthusiasts", '
                    '"tone": "professional"}]\n\n'
                    "Respond with ONLY the JSON array, no extra text."
                ),
                system_message=(
                    "You are a content strategist who identifies timely, "
                    "high-impact blog topics from trending data."
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
