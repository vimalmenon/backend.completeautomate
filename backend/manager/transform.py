from backend.database import PromptDB, YouTubeVideoDB

video_mapping = {
    "Vw_ilJWdzK8": """
This is the first video in a series of videos created for AI terms.
In this series of videos, I break down various AI terms, as many of us are not familiar with these terms.
Ensure the proper part number is given at the end or beginning of the video title as per the best YouTube title convention.


The first video link is as follows.

https://youtu.be/Vw_ilJWdzK8
""",
    "d4j2OTJdO94": """
This is the second video in a series of videos created for AI terms.
In this series of videos, I break down various AI terms, as many of us are not familiar with these terms.
Ensure the proper part number is given at the end or beginning of the video title as per the best YouTube title convention.

The first video link is as follows.
https://youtu.be/Vw_ilJWdzK8
""",
}

# prompt_mapping = {

# }

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
