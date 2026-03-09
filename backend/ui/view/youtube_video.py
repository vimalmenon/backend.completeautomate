from backend.ui.common.component_common import (
    render_common_header,
    render_separator,
)


def youtube_videos_page(channel_id: str, video_id: str, section: str | None = None):
    render_common_header(page_title="YouTube Videos")
    render_separator()
