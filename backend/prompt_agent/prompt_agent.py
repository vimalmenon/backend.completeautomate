from backend.prompt.youtube_video_summarization.youtube_video_summarization_agent import (
    YouTubeVideoSummarizationAgent,
)


class PromptAgent:
    def generate(self):
        return YouTubeVideoSummarizationAgent().generate()

    def review(self):
        return YouTubeVideoSummarizationAgent().review()
