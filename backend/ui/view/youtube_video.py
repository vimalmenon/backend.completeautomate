from nicegui import run, ui

from backend.data import PlatformDBData, PlatformYouTubeVideoDBData
from backend.data.task import TaskData
from backend.enum import JobEnum, PlatformEnum, TaskStatusEnum
from backend.manager import TaskManager, YouTubeVideoManager
from backend.ui.common.component_common import (
    render_common_header,
    render_separator,
)

FLOW_STEPS: list[tuple[JobEnum, str]] = [
    (JobEnum.YouTubeVideo, "Video"),
    (JobEnum.YouTubeVideoSummarizer, "Summarize"),
    (JobEnum.YouTubeVideoMetadataSuggester, "Metadata Suggest"),
    (JobEnum.YouTubeVideoMetadataUpdater, "Metadata Update"),
    (JobEnum.YouTubeVideoThumbnailPromptSuggester, "Thumbnail Prompt"),
    (JobEnum.YouTubeThumbnailUpdater, "Thumbnail Update"),
]

STATUS_STYLE: dict[TaskStatusEnum, dict[str, str]] = {
    TaskStatusEnum.COMPLETED: {
        "icon": "check_circle",
        "color": "green",
        "label": "Completed",
    },
    TaskStatusEnum.IN_PROGRESS: {
        "icon": "schedule",
        "color": "blue",
        "label": "In Progress",
    },
    TaskStatusEnum.REVIEW: {
        "icon": "rate_review",
        "color": "orange",
        "label": "Review",
    },
    TaskStatusEnum.FAILED: {"icon": "error", "color": "red", "label": "Failed"},
    TaskStatusEnum.NEW: {"icon": "fiber_new", "color": "grey", "label": "New"},
    TaskStatusEnum.PENDING: {"icon": "pending", "color": "grey", "label": "Pending"},
    TaskStatusEnum.APPROVED: {"icon": "verified", "color": "teal", "label": "Approved"},
    TaskStatusEnum.CLEAN_UP: {
        "icon": "cleaning_services",
        "color": "brown",
        "label": "Clean Up",
    },
}


def render_task_progress(tasks: list[TaskData]) -> None:
    task_by_job: dict[JobEnum, TaskData] = {}
    for task in sorted(tasks, key=lambda t: t.created_at):
        task_by_job[task.job_type] = task

    with ui.card().classes(
        "w-full p-4 shadow-sm border border-gray-200 dark:border-slate-700"
    ):
        ui.label("Task Flow").classes("text-sm font-bold mb-2")
        with ui.row().classes("w-full items-stretch gap-1 flex-wrap"):
            for index, (job_type, step_label) in enumerate(FLOW_STEPS):
                current_task = task_by_job.get(job_type)
                status = current_task.status if current_task else None
                style = (
                    STATUS_STYLE[status]
                    if status and status in STATUS_STYLE
                    else STATUS_STYLE[TaskStatusEnum.PENDING]
                )

                with ui.card().classes(
                    "min-w-[110px] flex-1 shadow-none border border-gray-200 dark:border-slate-700"
                ):
                    with ui.column().classes("px-2 py-1 gap-0"):
                        ui.label(step_label).classes("text-xs font-semibold")
                        with ui.row().classes("items-center gap-1"):
                            ui.icon(style["icon"]).classes(
                                f"text-{style['color']}-600 text-sm"
                            )
                            ui.badge(style["label"], color=style["color"]).classes(
                                "text-[10px] px-1 py-0"
                            ).props("outline")

                if index < len(FLOW_STEPS) - 1:
                    with ui.column().classes("justify-center hidden lg:flex"):
                        ui.icon("chevron_right").classes("text-gray-400 text-xs")


def _render_stat_card(icon: str, label: str, value: str) -> None:
    with ui.card().classes("flex-1 min-w-32 p-4 text-center"):
        ui.icon(icon).classes("text-3xl text-primary")
        ui.label(value).classes("text-2xl font-bold mt-1")
        ui.label(label).classes("text-sm text-gray-500")


def open_video_stats_chart_dialog(video) -> None:
    stats = getattr(video, "stats", [])

    if not stats:
        ui.notify("No stats data available", type="warning")
        return

    time_labels = []
    views = []
    likes = []
    comments = []

    for stat in stats:
        try:
            time_labels.append(stat.timestamp.strftime("%Y-%m-%d %H:%M"))
            views.append(int(stat.views))
            likes.append(int(stat.likes))
            comments.append(int(stat.comments))
        except (AttributeError, TypeError, ValueError):
            continue

    if not time_labels:
        ui.notify("No valid stats data to display", type="warning")
        return

    with ui.dialog() as dialog, ui.card().classes("w-[1100px] max-w-full"):
        ui.label(f"Stats for: {video.title}").classes("text-h6 mb-4")

        import plotly.graph_objects as go

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=time_labels,
                y=views,
                mode="lines+markers",
                name="Views",
                line=dict(color="#2563EB", width=2),
                marker=dict(size=6),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=time_labels,
                y=likes,
                mode="lines+markers",
                name="Likes",
                line=dict(color="#16A34A", width=2),
                marker=dict(size=6),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=time_labels,
                y=comments,
                mode="lines+markers",
                name="Comments",
                line=dict(color="#EA580C", width=2),
                marker=dict(size=6),
            )
        )
        fig.update_layout(
            title="Video Statistics Over Time",
            xaxis_title="Date/Time",
            yaxis_title="Count",
            hovermode="x unified",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            height=500,
        )

        ui.plotly(fig).classes("w-full")

        with ui.row().classes("w-full justify-end mt-4"):
            ui.button("Close", on_click=dialog.close).props("flat color=primary")

        dialog.open()


def _render_video_details(video) -> None:
    # Latest stats (last entry has the most recent data)
    latest_stats = video.stats[-1] if video.stats else None

    with ui.card().classes(
        "w-full p-4 shadow-sm border border-gray-200 dark:border-slate-700"
    ):
        with ui.row().classes("w-full gap-4 flex-wrap items-center"):
            with ui.column().classes("shrink-0 justify-center"):
                if video.thumbnail:
                    ui.image(video.thumbnail).classes("w-64 rounded-lg shadow-sm")

            with ui.column().classes("flex-1 gap-3 min-w-[280px]"):
                with ui.row().classes(
                    "w-full items-center justify-between gap-2 flex-wrap"
                ):
                    ui.label(video.title).classes("text-h5 font-bold leading-tight")
                    with ui.row().classes("gap-2 flex-wrap"):
                        ui.badge(
                            f"Published {video.published_at.strftime('%Y-%m-%d')}",
                            color="primary",
                        ).props("outline")
                        ui.badge(f"Language {video.language}", color="grey-7").props(
                            "outline"
                        )

                if video.tags:
                    with ui.row().classes("gap-2 flex-wrap"):
                        for tag in video.tags[:6]:
                            ui.badge(tag, color="grey-6").props("outline")

                if latest_stats:
                    with ui.row().classes("w-full gap-3 flex-wrap"):
                        _render_stat_card(
                            "visibility", "Views", f"{latest_stats.views:,}"
                        )
                        _render_stat_card(
                            "thumb_up", "Likes", f"{latest_stats.likes:,}"
                        )
                        _render_stat_card(
                            "comment", "Comments", f"{latest_stats.comments:,}"
                        )
                        _render_stat_card(
                            "update",
                            "Stats Updated",
                            latest_stats.timestamp.strftime("%Y-%m-%d"),
                        )

    # Description
    if video.description:
        with ui.card().classes(
            "w-full p-4 shadow-sm border border-gray-200 dark:border-slate-700"
        ):
            ui.label("Description").classes("text-h6 font-bold mb-2")
            ui.label(video.description).classes("text-sm whitespace-pre-wrap")


def _render_transcript_section(
    video, ref_id: str, video_id: str, transcript_dialog: ui.dialog
) -> None:
    with ui.column().classes("w-full gap-4"):
        with ui.card().classes(
            "w-full p-4 shadow-sm border border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-slate-800"
        ):
            ui.label("Transcript").classes("text-h6 font-bold mb-2")
            with ui.scroll_area().classes("w-full").style("height: 200px;"):
                ui.label(video.transcript or "(No transcript available)").classes(
                    "text-sm whitespace-pre-wrap font-mono leading-relaxed p-4"
                )
        if video.summarized_transcript:
            with ui.card().classes(
                "w-full p-4 shadow-sm border border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-slate-800"
            ):
                ui.label("Summarized Transcript").classes("text-h6 font-bold mb-2")
                with ui.scroll_area().classes("w-full").style("height: 200px;"):
                    ui.label(
                        video.summarized_transcript
                        or "(No summarized transcript available)"
                    ).classes("text-sm whitespace-pre-wrap leading-relaxed p-4")


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
    with ui.dialog().props("persistent") as transcript_dialog:
        with ui.card().style(
            "width:min(960px, 92vw); height:min(760px, 88vh); border-radius:16px; display:flex; flex-direction:column; "
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
                        ui.label("Edit Transcript").style(
                            "font-size:1.1rem; font-weight:700;"
                        )
                        ui.label(
                            f"{video.title} • Published {video.published_at.strftime('%Y-%m-%d')}"
                        ).style("font-size:0.8rem; opacity:0.75; max-width:680px;")
                ui.button(icon="close", on_click=transcript_dialog.close).props(
                    "flat round dense color=white"
                )

            # ── Hint ──────────────────────────────────────────────────────
            with ui.row().style(
                "flex-shrink:0; padding:8px 24px 0; align-items:center; gap:8px;"
            ):
                ui.icon("info").style("font-size:1rem; color:#6b7280;")
                ui.label(
                    "Edit the transcript below. Click Save Changes when done."
                ).style("font-size:0.85rem; color:#6b7280;")

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
                            lambda: YouTubeVideoManager(
                                ref_id=platform.ref_id
                            ).update_transcript(video_id, new_text)
                        )
                        save_btn.props("loading=false disabled=false")
                        transcript_dialog.close()
                        ui.notify("Transcript saved", type="positive", position="top")

                    save_btn = ui.button(
                        "Save Changes", icon="save", on_click=save_transcript
                    ).props("color=primary")

    with ui.column().classes("w-full max-w-7xl mx-auto gap-4"):
        with ui.card().classes(
            "w-full p-4 shadow-sm border border-gray-200 dark:border-slate-700"
        ):
            with ui.row().classes(
                "w-full items-center justify-between gap-3 flex-wrap"
            ):
                with ui.row().classes("items-center gap-2 flex-wrap"):
                    ui.button(icon="home", on_click=lambda: ui.navigate.to("/")).props(
                        "flat dense"
                    )
                    ui.button(
                        icon="arrow_back",
                        on_click=lambda: ui.navigate.to(f"/youtube/{channel_id}"),
                    ).props("flat dense")
                    ui.label(
                        f"Published {video.published_at.strftime('%Y-%m-%d')}"
                    ).classes("text-sm text-gray-500")

                with ui.row().classes("items-center gap-2 flex-wrap"):
                    ui.button(
                        "Show Graph",
                        icon="show_chart",
                        on_click=lambda: open_video_stats_chart_dialog(video),
                    ).props("outline color=primary")
                    ui.button(
                        "Edit Transcript",
                        icon="edit",
                        on_click=transcript_dialog.open,
                    ).props("color=primary outline")

        render_task_progress(tasks)
        _render_video_details(video)
        _render_transcript_section(video, platform.ref_id, video_id, transcript_dialog)
