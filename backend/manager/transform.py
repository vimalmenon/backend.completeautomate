from backend.database import AgentMessageDB, PromptDB, YouTubeVideoDB

video_mapping = {
    "first video": """
This is first video in series of videos created for AI teams.
In this series of videos, I am breaking down various AI teams used as many of us are not aware of these terms.
Make sure you have proper part number at the end or beginnering of video title as per best youtube title convension

First video link is as below
""",
    "second video": """
This is second video in series of videos created for AI teams.
In this series of videos, I am breaking down various AI teams used as many of us are not aware of these terms.
Make sure you have proper part number at the end or beginnering of video title as per best youtube title convension

First video link is as below
""",
}

prompt_mapping = {

}

IS_READY = False


def transform_data() -> bool:
    update_videos()
    update_prompt()
    return False


def update_videos():
    videos = YouTubeVideoDB(ref_id="").get_all_videos_from_db()
    if IS_READY:
        for video in videos:
            if user_message := video_mapping.get(video.platform.video_id):
                YouTubeVideoDB(ref_id=video.ref_id).update_values(
                    {"user_message": user_message.strip()}
                )


def update_prompt():
    if IS_READY:
        prompts = PromptDB().get_all_prompts()
        for prompt in prompts:
            PromptDB().update_prompt(prompt.task, values={"prompt": prompt.prompt})
