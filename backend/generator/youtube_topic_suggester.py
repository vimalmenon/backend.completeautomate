from backend.enum import TaskStatusEnum
from backend.generator.base_generator import BaseGenerator

# Get Trends from Google and other sources
# Come up topics based on trends and past videos
# Review suggestions
# Generate pointers to speak


class YouTubeTopicSuggester(BaseGenerator):

    def generate(self) -> TaskStatusEnum:
        return TaskStatusEnum.IN_PROGRESS
