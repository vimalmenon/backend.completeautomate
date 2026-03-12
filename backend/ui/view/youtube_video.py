from nicegui import run, ui

from backend.data import PlatformDBData, PlatformYouTubeVideoDBData
from backend.enum import PlatformEnum
from backend.manager import TaskManager, YouTubeVideoManager
from backend.ui.common.component_common import (
    render_common_header,
    render_separator,
)

steps = [
    "YouTubeVideoCreate",
    "YouTubeSummarize",
    "YoutubeMetadataGenerator",
    "YouTubeMetadataUpdater",
    "YouTubeThumbnailGenerator",
    "YouTubeThumbnailUpdater",
]


def render_task_progress(tasks):
    # TODO Show video status Progress
    pass


def _render_stat_card(icon: str, label: str, value: str) -> None:
    with ui.card().classes("flex-1 min-w-32 p-4 text-center"):
        ui.icon(icon).classes("text-3xl text-primary")
        ui.label(value).classes("text-2xl font-bold mt-1")
        ui.label(label).classes("text-sm text-gray-500")


def _render_video_details(video) -> None:
    # Latest stats (last entry has the most recent data)
    latest_stats = video.stats[-1] if video.stats else None

    with ui.row().classes("w-full gap-4 flex-wrap"):
        # Left column: thumbnail
        with ui.column().classes("shrink-0"):
            if video.thumbnail:
                ui.image(video.thumbnail).classes("w-64 rounded shadow")

        # Right column: title + metadata
        with ui.column().classes("flex-1 gap-2"):
            ui.label(video.title).classes("text-h5 font-bold")

            with ui.row().classes("gap-4 flex-wrap text-sm text-gray-500"):
                ui.label(f"Published: {video.published_at.strftime('%Y-%m-%d')}")
                ui.label(f"Language: {video.language}")
                if video.tags:
                    ui.label(f"Tags: {', '.join(video.tags[:6])}")

    ui.separator().classes("my-4")

    # Stats row
    if latest_stats:
        with ui.row().classes("w-full gap-4 flex-wrap"):
            _render_stat_card("visibility", "Views", f"{latest_stats.views:,}")
            _render_stat_card("thumb_up", "Likes", f"{latest_stats.likes:,}")
            _render_stat_card("comment", "Comments", f"{latest_stats.comments:,}")
            _render_stat_card(
                "update",
                "Stats Updated",
                latest_stats.timestamp.strftime("%Y-%m-%d"),
            )

    # Description
    if video.description:
        ui.separator().classes("my-4")
        ui.label("Description").classes("text-h6 font-bold")
        with ui.card().classes("w-full"):
            ui.label(video.description).classes("text-sm whitespace-pre-wrap")


def _render_transcript_section(
    video, ref_id: str, video_id: str, transcript_dialog: ui.dialog
) -> None:
    ui.separator().classes("my-4")
    ui.label("Transcript").classes("text-h6 font-bold mb-2")
    with ui.card().classes("w-full bg-gray-50 dark:bg-slate-800"):
        with ui.scroll_area().classes("w-full").style("height: 200px;"):
            ui.label(
                video.transcript or "(No transcript available)"
            ).classes("text-sm whitespace-pre-wrap font-mono leading-relaxed p-4")


async def youtube_video_page(
    channel_id: str, video_id: str, section: str | None = None
):
    platform = PlatformDBData(
        platform_type=PlatformEnum.YouTubeVideo,
        data=PlatformYouTubeVideoDBData(channel_id=channel_id, video_id=video_id),
    )
    render_common_header(page_title=f"YouTube Video: {video_id}")
    render_separator()

    # Show loading spinner while fetching
    with ui.row().classes("w-full items-center my-4") as loading_row:
        ui.spinner(size="lg", color="primary")
        ui.label("Loading video...")

        video, tasks = await run.io_bound(
            lambda: (
                YouTubeVideoManager(ref_id=platform.ref_id).get_video(),
                TaskManager().get_task_by_ref_id(ref_id=platform.ref_id),
            )
        )

    loading_row.delete()

    if not video:
        with ui.row().classes("w-full"):
            ui.label(f"No video found with {video_id}")
        return

    # Build transcript dialog before the top bar so the button can open it
    with ui.dialog().props("maximized persistent") as transcript_dialog:
        with ui.card().style(
            "width:100%; height:100%; border-radius:0; display:flex; flex-direction:column; "
            "padding:0; gap:0; overflow:hidden;"
        ):
            # ── Header ────────────────────────────────────────────────────
            with ui.row().style(
                "flex-shrink:0; background:var(--q-primary); color:white; "
                "padding:12px 24px; align-items:center; justify-content:space-between; width:100%;"
            ):
                with ui.row().style("align-items:center; gap:12px;"):
                    ui.icon("subtitles").style("font-size:1.5rem;")
                    with ui.column().style("gap:2px;"):
                        ui.label("Edit Transcript").style("font-size:1.1rem; font-weight:700;")
                        ui.label(video.title).style("font-size:0.8rem; opacity:0.75; max-width:60vw;")
                ui.button(icon="close", on_click=transcript_dialog.close).props(
                    "flat round dense color=white"
                )

            # ── Hint ──────────────────────────────────────────────────────
            with ui.row().style(
                "flex-shrink:0; padding:8px 24px 0; align-items:center; gap:8px;"
            ):
                ui.icon("info").style("font-size:1rem; color:#6b7280;")
                ui.label("Edit the transcript below. Click Save Changes when done.").style(
                    "font-size:0.85rem; color:#6b7280;"
                )

            # ── Textarea ──────────────────────────────────────────────────
            with ui.element("div").style(
                "flex:1; min-height:0; width:100%; height:100%; padding:12px 24px; overflow:hidden; display:flex; flex-direction:column;"
            ):
                transcript_area = (
                    ui.textarea(value=video.transcript or "")
                    .classes(
                        "w-full h-full "
                        "[&_.q-field__inner]:h-full "
                        "[&_.q-field__control]:h-full "
                        "[&_.q-field__native]:h-full"
                    )
                    .props(
                        "input-class=h-full "
                        "input-style=width:100%; height:100%; min-height:100%;"
                    )
                    .style(
                        "flex:1 1 auto; width:100%; height:100%; min-height:100%; "
                        "font-family:ui-monospace,SFMono-Regular,Menlo,monospace; "
                        "font-size:0.85rem; line-height:1.7; resize:none;"
                    )
                )

            # ── Footer ────────────────────────────────────────────────────
            with ui.row().style(
                "flex-shrink:0; padding:12px 24px; border-top:1px solid #e2e8f0; "
                "align-items:center; justify-content:space-between; width:100%;"
            ):
                char_hint = ui.label("").style("font-size:0.8rem; color:#9ca3af;")
                transcript_area.on(
                    "input",
                    lambda e, lbl=char_hint: lbl.set_text(
                        f"{len(e.args.get('value', '') if isinstance(e.args, dict) else '')} characters"
                    ),
                )
                with ui.row().style("gap:12px; align-items:center;"):
                    ui.button("Cancel", on_click=transcript_dialog.close).props("flat")

                    async def save_transcript() -> None:
                        new_text = transcript_area.value
                        save_btn.props("loading=true disabled=true")
                        await run.io_bound(
                            lambda: YouTubeVideoManager(ref_id=platform.ref_id).update_transcript(
                                video_id, new_text
                            )
                        )
                        save_btn.props("loading=false disabled=false")
                        transcript_dialog.close()
                        ui.notify("Transcript saved", type="positive", position="top")

                    save_btn = ui.button(
                        "Save Changes", icon="save", on_click=save_transcript
                    ).props("color=primary")

    # Top navigation bar (rendered after load so dialog reference is available)
    with ui.row().classes("w-full items-center justify-between mb-4"):
        with ui.row().classes("items-center gap-2"):
            ui.button(icon="home", on_click=lambda: ui.navigate.to("/")).props("flat dense")
            ui.button(
                icon="arrow_back",
                on_click=lambda: ui.navigate.to(f"/youtube/{channel_id}"),
            ).props("flat dense")
            ui.label(video_id).classes("text-sm text-gray-500")
        ui.button(
            "Edit Transcript", icon="edit", on_click=transcript_dialog.open
        ).props("color=primary outline")

    render_task_progress(tasks)
    _render_video_details(video)
    _render_transcript_section(video, platform.ref_id, video_id, transcript_dialog)
