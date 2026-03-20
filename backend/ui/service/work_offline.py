import os

from nicegui import app

from backend.config.env import env
from backend.config.session import set_offline_mode
from backend.factory import (
    create_youtube_channel_job_factory,
    fake_uuid,
    platform_channel_factory,
    platform_video_factory,
    youtube_channel_factory,
    youtube_video_factory,
)
from backend.manager import (
    JobManager,
    PlatformManager,
    YouTubeChannelManager,
    YouTubeVideoManager,
)
from backend.ui.common.component_common import render_notify


def toggle_offline_mode(is_offline: bool):
    os.environ["OFFLINE"] = "true" if is_offline else "false"

    app.storage.user["OFFLINE"] = is_offline
    env.OFFLINE = is_offline

    set_offline_mode(is_offline)
    mode = "Offline (Moto mock AWS)" if is_offline else "Online (real AWS)"
    render_notify(f"Mode switched: {mode}")


def load_initial_data():
    is_offline = app.storage.user.get("OFFLINE", False)
    set_offline_mode(is_offline)
    if is_offline:
        load_mock_data()


def load_mock_data():
    channel_id = str(fake_uuid())
    platform_manager = PlatformManager()
    channel_platform = platform_channel_factory(channel_id=channel_id)
    video_platform = platform_video_factory(channel_id=channel_id)
    platform_manager.save_data(channel_platform)
    platform_manager.save_data(video_platform)
    channel = youtube_channel_factory(ref_id=channel_platform.ref_id)
    video = youtube_video_factory(ref_id=video_platform.ref_id)
    YouTubeChannelManager(channel_id).save_data(channel)
    YouTubeVideoManager(ref_id=video_platform.ref_id).save_data(video)

    # Adding Tasks
    # payload = create_youtube_channel_job_factory(ref_id=channel_platform.ref_id)
    # task = create_task_factory(payload=payload.to_json())
    # JobManager().add_task(task)
