import os

from nicegui import app

from backend.config.env import env
from backend.config.session import set_offline_mode
from backend.manager import DataManager
from backend.ui.common.common_component import render_notify


def toggle_offline_mode(is_offline: bool):
    os.environ["OFFLINE"] = "true" if is_offline else "false"

    app.storage.user["OFFLINE"] = is_offline
    env.OFFLINE = is_offline

    set_offline_mode(is_offline)
    mode = "Offline (Moto mock AWS)" if is_offline else "Online (real AWS)"
    render_notify(f"Mode switched: {mode}")


def load_initial_data(offline: bool):
    is_offline = app.storage.user.get("OFFLINE", offline)
    set_offline_mode(is_offline)
    if is_offline:
        DataManager().upload()
