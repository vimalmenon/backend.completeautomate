from nicegui import ui


def render_notify(msg: str):
    ui.notify(msg, type="positive", position="top")
