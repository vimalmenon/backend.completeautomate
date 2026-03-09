import os
from uuid import uuid4

from nicegui import app

from backend.config.env import env
from backend.config.session import set_offline_mode
from backend.factory import platform_channel_factory, platform_video_factory
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
    channel_id = uuid4()
    channel = platform_channel_factory(channel_id=str(channel_id))
    video = platform_video_factory(channel_id=str(channel_id))
    print(channel, video)
