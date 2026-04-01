from backend.database import PromptDB, YouTubeVideoDB

video_mapping = {
    "first video": """
This is first video on series of videos created for AI teams.
In this series of videos, I am breaking down various AI teams used as many of us are not aware of these terms.
Make sure you have proper part number at the end or beginnering of video title as per test youtube title convention

First video link is as below
""",
    "second video": """
This is second video on series of videos created for AI teams.
In this series of videos, I am breaking down various AI teams used as many of us are not aware of these terms.
Make sure you have proper part number at the end or beginnering of video title as per test youtube title convention

First video link is as below
""",
}

IS_READY = False


def transform_data() -> bool:
    update_videos()
    update_prompt()
    return False


def update_videos():
    if IS_READY:
        videos = YouTubeVideoDB(ref_id="").get_all_videos_from_db()
        for video in videos:
            if user_message := video_mapping.get(video.platform.video_id):
                YouTubeVideoDB(ref_id=video.ref_id).update_values(
                    {"user_message": user_message.strip()}
                )


def update_prompt():
    prompts = PromptDB().get_all_prompts()
    for prompt in prompts:
        PromptDB().update_prompt(prompt.task, values={"prompt": prompt.prompt})
