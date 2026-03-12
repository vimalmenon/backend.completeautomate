from datetime import datetime
from uuid import uuid4

from nicegui import run, ui

from backend.config.env import env
from backend.data import (
    TaskData,
    YouTubeVideoThumbnailPromptSuggesterJobData,
)
from backend.database import TaskDB
from backend.database.image.image_prompt_db import ImagePromptDB
from backend.database.youtube import (
    YouTubeVideoDB,
    YouTubeVideoMetadataSuggesterDB,
)
from backend.enum import JobEnum, JobStatusEnum, TaskStatusEnum
from backend.ui.view.youtube_channel import render_breadcrumbs


def open_stats_chart_dialog(video_json: dict) -> None:
    """Open a dialog with line chart showing video stats over time."""
    stats = video_json.get("stats", [])

    if not stats:
        ui.notify("No stats data available", type="warning")
        return

    # Parse stats data
    timestamps = []
    views = []
    likes = []
    comments = []

    for stat in stats:
        try:
            timestamp_str = stat.get("timestamp", "")
            timestamps.append(datetime.fromisoformat(timestamp_str))
            views.append(int(stat.get("views", 0)))
            likes.append(int(stat.get("likes", 0)))
            comments.append(int(stat.get("comments", 0)))
        except (ValueError, TypeError):
            continue

    if not timestamps:
        ui.notify("No valid stats data to display", type="warning")
        return

    # Format timestamps for display
    time_labels = [ts.strftime("%Y-%m-%d %H:%M") for ts in timestamps]

    with ui.dialog() as dialog, ui.card().classes("w-[1100px] max-w-full"):
        ui.label(f"Stats for: {video_json.get('title', 'Video')}").classes(
            "text-h6 mb-4"
        )

        # Create plotly chart
        import plotly.graph_objects as go

        fig = go.Figure()

        # Add traces for each metric
        fig.add_trace(
            go.Scatter(
                x=time_labels,
                y=views,
                mode="lines+markers",
                name="Views",
                line=dict(color="#2196F3", width=2),
                marker=dict(size=6),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=time_labels,
                y=likes,
                mode="lines+markers",
                name="Likes",
                line=dict(color="#4CAF50", width=2),
                marker=dict(size=6),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=time_labels,
                y=comments,
                mode="lines+markers",
                name="Comments",
                line=dict(color="#FF9800", width=2),
                marker=dict(size=6),
            )
        )

        # Update layout
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

        # Summary stats
        with ui.row().classes("w-full gap-4 mt-4"):
            with ui.card().classes("flex-1"):
                ui.label("Latest Views").classes("text-sm text-gray-600")
                ui.label(f"{views[-1]:,}").classes("text-2xl font-bold text-blue-600")
            with ui.card().classes("flex-1"):
                ui.label("Latest Likes").classes("text-sm text-gray-600")
                ui.label(f"{likes[-1]:,}").classes("text-2xl font-bold text-green-600")
            with ui.card().classes("flex-1"):
                ui.label("Latest Comments").classes("text-sm text-gray-600")
                ui.label(f"{comments[-1]:,}").classes(
                    "text-2xl font-bold text-orange-600"
                )

        with ui.row().classes("w-full justify-end mt-4"):
            ui.button("Close", on_click=dialog.close).props("flat")

    dialog.open()


def open_text_dialog(title: str, text: str) -> None:
    with ui.dialog() as dialog, ui.card().classes("w-[1100px] max-w-full"):
        ui.label(title).classes("text-h6")
        with ui.element("pre").classes(
            "w-full max-h-[70vh] overflow-y-auto whitespace-pre-wrap text-sm bg-gray-50 dark:bg-slate-800 p-3 rounded border border-gray-300 dark:border-slate-600"
        ):
            ui.label(text).classes("whitespace-pre-wrap text-sm")
        with ui.row().classes("w-full justify-end"):
            ui.button("Close", on_click=dialog.close).props("flat")
    dialog.open()


def render_multiline_field(field_name: str, text: str) -> None:
    with ui.row().classes("w-full gap-4 items-start"):
        ui.label(f"**{field_name}:**").classes("w-1/5 font-bold text-blue-600 text-sm")
        with ui.column().classes("w-4/5 gap-2"):
            with ui.element("pre").classes(
                "w-full max-h-56 overflow-y-auto whitespace-pre-wrap text-sm bg-white dark:bg-slate-800 p-3 rounded border border-gray-300 dark:border-slate-600"
            ):
                ui.label(text).classes("whitespace-pre-wrap text-sm")
            ui.button(
                "View all",
                icon="open_in_full",
                on_click=lambda current_text=text, current_field=field_name: open_text_dialog(
                    current_field.title(), current_text
                ),
            ).props("flat dense").classes("self-end")


def update_metadata_option_status(
    video_id: str,
    option_index: int,
    status_value: str,
) -> None:
    try:
        is_updated = YouTubeVideoMetadataSuggesterDB().update_option_status(
            channel_id=env.YOUTUBE_CHANNEL_ID,
            video_id=video_id,
            option_index=option_index,
            status=JobStatusEnum(status_value),
        )
        if not is_updated:
            ui.notify("Unable to update option status", type="warning")
            return
        ui.notify("Option status updated", type="positive")
        ui.run_javascript('window.location.href = "/youtube"')
    except Exception:
        ui.notify("Failed to update option status", type="negative")


def _get_image_prompt_options(task_id: str) -> dict[str, str]:
    try:
        image_prompt_rows = ImagePromptDB().get_by_task_id(task_id)
    except Exception:
        return {}

    options: dict[str, str] = {}
    for row_index, row in enumerate(image_prompt_rows, start=1):
        for prompt_index, prompt in enumerate(row.prompts, start=1):
            option_key = f"{row.id}:{prompt_index}"
            options[option_key] = (
                f"{prompt.name} ({prompt.status.value}) [set {row_index}.{prompt_index}]"
            )
    return options


def render_metadata_suggestions(video_id: str) -> None:
    suggestion = YouTubeVideoMetadataSuggesterDB().fetch_suggestion(
        channel_id=env.YOUTUBE_CHANNEL_ID,
        video_id=video_id,
    )
    if not suggestion:
        return

    image_prompt_options = _get_image_prompt_options(str(suggestion.task_id))

    with ui.column().classes(
        "w-full gap-3 mt-2 p-3 bg-amber-50 dark:bg-amber-900/20 rounded border border-amber-200 dark:border-amber-700"
    ):
        ui.label("Metadata Suggestions").classes("text-subtitle1 font-semibold")
        if image_prompt_options:
            ui.label("ImagePromptDB options available for thumbnail selection").classes(
                "text-xs text-amber-700"
            )
        else:
            ui.label("No ImagePromptDB records found for this task").classes(
                "text-xs text-gray-500"
            )
        if suggestion.comment:
            with ui.row().classes("w-full gap-4 items-start"):
                ui.label("Comment:").classes("w-1/5 font-bold text-amber-700 text-sm")
                ui.label(str(suggestion.comment)).classes("w-4/5 text-wrap text-sm")

        for index, detail in enumerate(suggestion.video_details, start=1):
            with ui.card().classes("w-full bg-white dark:bg-slate-800"):
                ui.label(f"Option {index} ({detail.status.value})").classes(
                    "text-sm font-semibold text-amber-700"
                )
                with ui.row().classes("w-full justify-end items-center gap-2"):
                    if image_prompt_options:
                        ui.select(
                            label="Image Prompt (ImagePromptDB)",
                            options=image_prompt_options,
                        ).props("outlined dense").classes("w-80")

                    status_input = (
                        ui.select(
                            label="Status",
                            options=[status.value for status in JobStatusEnum],
                            value=detail.status.value,
                        )
                        .props("outlined dense")
                        .classes("w-48")
                    )
                    ui.button(
                        "Update Status",
                        icon="save",
                        on_click=lambda current_video_id=video_id, current_index=index - 1, current_status=status_input: update_metadata_option_status(
                            video_id=current_video_id,
                            option_index=current_index,
                            status_value=str(current_status.value),
                        ),
                    ).props("color=primary")
                with ui.row().classes("w-full gap-4 items-start"):
                    ui.label("Title:").classes("w-1/5 font-bold text-sm")
                    ui.label(detail.title).classes("w-4/5 text-wrap text-sm")
                render_multiline_field("description", detail.description)
                with ui.row().classes("w-full gap-4 items-start"):
                    ui.label("Tags:").classes("w-1/5 font-bold text-sm")
                    ui.label(", ".join(detail.tags) if detail.tags else "-").classes(
                        "w-4/5 text-wrap text-sm"
                    )


def open_metadata_suggestions_dialog(video_id: str) -> None:
    suggestion = YouTubeVideoMetadataSuggesterDB().fetch_suggestion(
        channel_id=env.YOUTUBE_CHANNEL_ID,
        video_id=video_id,
    )
    if not suggestion:
        ui.notify("No metadata suggestions found", type="warning")
        return

    with ui.dialog() as dialog, ui.card().classes("w-[1100px] max-w-full"):
        with ui.row().classes("w-full items-center justify-between"):
            ui.label("Metadata Suggestions").classes("text-h6")
            ui.button("Close", on_click=dialog.close).props("flat")
        ui.separator()
        render_metadata_suggestions(video_id)

    dialog.open()


# def save_video_details(ref_id: str, title: str, description: str) -> None:
#     try:
#         YouTubeVideoDB(channel_id=env.YOUTUBE_CHANNEL_ID).update_video_details(
#             video_id=ref_id, title=title, description=description, tags=[]
#         )
#         ui.notify("Video updated", type="positive")
#         ui.run_javascript('window.location.href = "/youtube"')
#     except Exception:
#         ui.notify("Failed to update video", type="negative")


# def save_transcript(ref_id: str, transcript_text: str, summarize_text: str) -> None:
#     try:
#         transcript = YouTubeTranscriptDBData(
#             transcript=transcript_text,
#             summarize=summarize_text,
#         )
#         YouTubeVideoDB(channel_id=env.YOUTUBE_CHANNEL_ID).update_transcript(
#             video_id=ref_id,
#             transcript=transcript,
#         )
#         ui.notify("Transcript updated", type="positive")
#         ui.run_javascript('window.location.href = "/youtube"')
#     except Exception:
#         ui.notify("Failed to update transcript", type="negative")


# def save_summarize(ref_id: str, transcript_text: str, summarize_text: str) -> None:
#     try:
#         transcript = YouTubeTranscriptDBData(
#             transcript=transcript_text,
#             summarize=summarize_text,
#         )
#         YouTubeVideoDB(channel_id=env.YOUTUBE_CHANNEL_ID).update_transcript(
#             video_id=ref_id,
#             transcript=transcript,
#         )
#         ui.notify("Summary updated", type="positive")
#         ui.run_javascript('window.location.href = "/youtube"')
#     except Exception:
#         ui.notify("Failed to update summary", type="negative")


def create_thumbnail_suggestion_task(ref_id: str) -> None:
    try:
        task_id = uuid4()
        payload = YouTubeVideoThumbnailPromptSuggesterJobData(
            task_id=task_id,
            ref_id=ref_id,
        ).to_json()
        task = TaskData(
            id=task_id,
            job_type=JobEnum.YouTubeVideoThumbnailPromptSuggester,
            payload=payload,
            created_at=datetime.now(),
            status=TaskStatusEnum.NEW,
            trail=[],
        )
        TaskDB().add_task(task)
        ui.notify("Thumbnail suggestion task created", type="positive")
    except Exception:
        ui.notify("Failed to create thumbnail suggestion task", type="negative")


def open_edit_video_dialog(video_json: dict) -> None:
    with ui.dialog() as dialog, ui.card().classes("w-[900px] max-w-full"):
        ui.label("Edit Video").classes("text-h6")
        # title_input = (
        #     ui.input(label="Title", value=str(video_json.get("title", "")))
        #     .props("outlined")
        #     .classes("w-full")
        # )
        # description_input = (
        #     ui.textarea(
        #         label="Description",
        #         value=str(video_json.get("description", "")),
        #     )
        #     .props("outlined autogrow")
        #     .classes("w-full")
        # )

        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button(
                "Save",
                icon="save",
                # on_click=lambda: save_video_details(
                #     _get_video_db_id(video_json),
                #     str(title_input.value),
                #     str(description_input.value),
                # ),
            ).props("color=primary")
    dialog.open()


def open_edit_transcript_dialog(video_json: dict) -> None:
    # transcript = video_json.get("transcript") or {}
    # current_transcript = str(transcript.get("transcript", ""))
    # current_summarize = str(transcript.get("summarize", ""))

    with ui.dialog() as dialog, ui.card().classes("w-[1000px] max-w-full"):
        ui.label("Edit Transcript").classes("text-h6")
        # transcript_input = (
        #     ui.textarea(label="Transcript", value=current_transcript)
        #     .props("outlined autogrow")
        #     .classes("w-full")
        # )

        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button(
                "Save",
                icon="save",
                # on_click=lambda: save_transcript(
                #     _get_video_db_id(video_json),
                #     str(transcript_input.value),
                #     current_summarize,
                # ),
            ).props("color=primary")
    dialog.open()


# def open_edit_summarize_dialog(video_json: dict) -> None:
#     transcript = video_json.get("transcript") or {}
#     current_transcript = str(transcript.get("transcript", ""))
#     current_summarize = str(transcript.get("summarize", ""))

#     with ui.dialog() as dialog, ui.card().classes("w-[1000px] max-w-full"):
#         ui.label("Edit Summarize").classes("text-h6")
#         # summarize_input = (
#         #     ui.textarea(label="Summarize", value=current_summarize)
#         #     .props("outlined autogrow")
#         #     .classes("w-full")
#         # )

#         with ui.row().classes("w-full justify-end gap-2"):
#             ui.button("Cancel", on_click=dialog.close).props("flat")
#             ui.button(
#                 "Save",
#                 icon="save",
#                 # on_click=lambda: save_summarize(
#                 #     _get_video_db_id(video_json),
#                 #     current_transcript,
#                 #     str(summarize_input.value),
#                 # ),
#             ).props("color=primary")
#     dialog.open()


def _get_video_id_from_platform(video) -> str:
    try:
        video_id = video.platform.video_id
        return video_id if isinstance(video_id, str) else str(video_id)
    except Exception:
        return ""


def _get_video_db_id(video_json: dict) -> str:
    video_id = str(video_json.get("video_id", "")).strip()
    if video_id:
        return video_id
    return str(video_json.get("ref_id", "")).strip()


def _render_video_action_buttons(video_json: dict, video_id: str = "") -> None:
    ref_id = str(video_json.get("ref_id", "")).strip()
    with ui.row().classes("w-full justify-end gap-2"):
        if ref_id:
            ui.button(
                "Suggest Thumbnail",
                icon="image_search",
                on_click=lambda current_ref_id=ref_id: create_thumbnail_suggestion_task(
                    current_ref_id
                ),
            ).props("flat")
        if video_id:
            ui.button(
                "Metadata Suggestions",
                icon="tips_and_updates",
                on_click=lambda current_video_id=video_id: open_metadata_suggestions_dialog(
                    current_video_id
                ),
            ).props("flat")
        ui.button(
            "View Stats",
            icon="show_chart",
            on_click=lambda current_video=video_json: open_stats_chart_dialog(
                current_video
            ),
        ).props("flat")
        ui.button(
            "Edit Video",
            icon="edit",
            on_click=lambda current_video=video_json: open_edit_video_dialog(
                current_video
            ),
        ).props("flat")
        ui.button(
            "Edit Transcript",
            icon="edit_note",
            on_click=lambda current_video=video_json: open_edit_transcript_dialog(
                current_video
            ),
        ).props("flat")
        ui.button(
            "Edit Summarize",
            icon="summarize",
            # on_click=lambda current_video=video_json: open_edit_summarize_dialog(
            #     current_video
            # ),
        ).props("flat")


def _resolve_video_thumbnail_url(thumbnail_url: str) -> str:
    if not thumbnail_url:
        return ""

    # Upgrade common YouTube thumbnail variants to a better quality image.
    known_suffixes = (
        "/default.jpg",
        "/mqdefault.jpg",
        "/hqdefault.jpg",
        "/sddefault.jpg",
        "/maxresdefault.jpg",
    )
    for suffix in known_suffixes:
        if thumbnail_url.endswith(suffix):
            return thumbnail_url[: -len(suffix)] + "/hqdefault.jpg"
    return thumbnail_url


def _render_video_json_details(video_json: dict) -> None:
    thumbnail_url = _resolve_video_thumbnail_url(
        str(video_json.get("thumbnail", "")).strip()
    )
    metadata_items: list[tuple[str, str]] = []
    transcript_text = ""
    summarize_text = ""

    for key, value in video_json.items():
        if key == "thumbnail":
            continue

        if key == "transcript" and isinstance(value, dict):
            transcript_text = str(value.get("transcript", ""))
            summarize_text = str(value.get("summarize", ""))
            continue

        if value is not None and not isinstance(value, list):
            display_val = (
                str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
            )
            metadata_items.append((key, display_val))

    with ui.row().classes("w-full gap-4 items-start flex-wrap lg:flex-nowrap"):
        with ui.column().classes("w-full lg:flex-1"):
            for key, display_val in metadata_items:
                with ui.row().classes("w-full gap-4 items-start"):
                    ui.label(f"{key}:").classes("w-1/5 font-bold text-blue-600 text-sm")
                    ui.label(display_val).classes("w-4/5 text-wrap text-sm")

        if thumbnail_url:
            with ui.column().classes("w-full lg:w-[360px] lg:shrink-0"):
                with ui.image(thumbnail_url).classes(
                    "w-full aspect-video object-cover rounded border border-gray-200 dark:border-slate-700"
                ):
                    pass

    if transcript_text:
        render_multiline_field("transcript", transcript_text)
    if summarize_text:
        render_multiline_field("summarize", summarize_text)


def _render_video_row(video) -> None:
    video_json = video.to_json()
    ref_id = str(video_json.get("ref_id", ""))
    video_id_full = _get_video_id_from_platform(video)
    route_id = video_id_full or ref_id
    video_id = route_id[:16]
    title = video_json.get("title", "Untitled")
    description = video_json.get("description", "")
    short_description = (
        description[:50] + "..." if len(description) > 50 else description
    )
    published = video_json.get("published_at", "")

    with ui.column().classes(
        "w-full gap-0 border-b border-gray-200 dark:border-slate-700"
    ):
        with ui.row().classes(
            "w-full p-3 hover:bg-blue-50 dark:hover:bg-blue-900/40 items-center flex-nowrap"
        ):
            ui.label(video_id).classes("w-1/6 text-sm")
            ui.label(title).classes("w-1/4 text-sm font-medium")
            ui.label(short_description).classes("w-1/4 text-sm")
            ui.label(published).classes("w-1/6 text-sm")
            with ui.row().classes("w-1/6 justify-center items-center gap-1 shrink-0"):
                if ref_id:
                    ui.button(
                        icon="image_search",
                        on_click=lambda current_ref_id=ref_id: create_thumbnail_suggestion_task(
                            current_ref_id
                        ),
                    ).props("flat dense")
                if video_id_full:
                    ui.button(
                        icon="tips_and_updates",
                        on_click=lambda current_video_id=video_id_full: open_metadata_suggestions_dialog(
                            current_video_id
                        ),
                    ).props("flat dense")
                ui.button(
                    icon="open_in_new",
                    on_click=lambda current_route_id=route_id: ui.run_javascript(
                        f'window.location.href = "/video/{current_route_id}"'
                    ),
                ).props("flat dense")


def _render_video_table(videos: list) -> None:
    ui.label(f"Found {len(videos)} video(s)").classes("text-subtitle1 mb-4")

    with ui.column().classes(
        "w-full gap-0 border border-gray-300 dark:border-slate-600 rounded"
    ):
        with ui.row().classes(
            "w-full bg-gray-100 dark:bg-slate-800 border-b border-gray-300 dark:border-slate-600 p-3 font-bold flex-nowrap items-center"
        ):
            ui.label("Ref ID").classes("w-1/6")
            ui.label("Title").classes("w-1/4")
            ui.label("Description").classes("w-1/4")
            ui.label("Published").classes("w-1/6")
            ui.label("Actions").classes("w-1/6 text-center shrink-0")

        for video in videos:
            _render_video_row(video)


async def youtube_page():
    with ui.card().classes("w-full page-transition"):
        with ui.row().classes("items-center justify-between w-full mb-4"):
            ui.label("YouTube Videos").classes("text-h4")
            with ui.row().classes("gap-2"):
                ui.button(
                    "View Channel",
                    icon="live_tv",
                    on_click=lambda: ui.run_javascript(
                        f'window.location.href = "/youtube/{env.YOUTUBE_CHANNEL_ID}"'
                    ),
                ).props("color=primary")
                ui.button(
                    icon="refresh",
                    on_click=lambda: ui.run_javascript(
                        "window.location.href = window.location.pathname + window.location.search"
                    ),
                ).props("flat")
                ui.button(
                    icon="home",
                    on_click=lambda: ui.run_javascript('window.location.href = "/"'),
                ).props("flat")

        render_breadcrumbs(
            [("Home", "/"), ("YouTube Videos", "/youtube")],
            right_text=f"Channel: {env.YOUTUBE_CHANNEL_ID}",
        )
        ui.separator()

        # Show loading spinner while fetching data
        with ui.row().classes("w-full items-center my-4") as loading_row:
            ui.spinner(size="lg", color="primary")
            ui.label("Loading YouTube videos...")

            # Fetch videos (non-blocking)
            videos = await run.io_bound(
                YouTubeVideoDB(ref_id=env.YOUTUBE_CHANNEL_ID).get_all_videos_from_db
            )
        videos = sorted(videos, key=lambda video: video.published_at, reverse=True)

        # Remove loading spinner and row
        loading_row.delete()

        if videos:
            _render_video_table(videos)
        else:
            with ui.card().classes("w-full bg-gray-100 dark:bg-slate-800"):
                ui.icon("video_library", size="xl").classes("text-gray-400")
                ui.label("No videos found").classes("text-h6 text-gray-500")

        ui.separator().classes("my-4")


async def video_detail_page(ref_id: str) -> None:
    video_db = YouTubeVideoDB(ref_id=ref_id)
    video = await run.io_bound(video_db.fetch_video_from_db)

    # Backward compatibility for old ref_id-based URLs.
    if not video:
        all_videos = await run.io_bound(video_db.get_all_videos_from_db)
        for candidate in all_videos:
            candidate_video_id = _get_video_id_from_platform(candidate)
            if ref_id == candidate.ref_id or ref_id == candidate_video_id:
                video = candidate
                break

    with ui.card().classes("w-full page-transition"):
        with ui.row().classes("items-center justify-between w-full mb-4"):
            ui.label("Video Details").classes("text-h4")
            with ui.row().classes("gap-2"):
                ui.button(
                    "Back to Videos",
                    icon="arrow_back",
                    on_click=lambda: ui.run_javascript(
                        'window.location.href = "/youtube"'
                    ),
                ).props("flat")
                ui.button(
                    icon="home",
                    on_click=lambda: ui.run_javascript('window.location.href = "/"'),
                ).props("flat")

        # Fetch video title for breadcrumb
        video_title = video.title if video else ref_id
        breadcrumb_title = (
            video_title[:30] + "..." if len(video_title) > 30 else video_title
        )
        video_status = "Published" if video and video.published_at else "Draft"
        render_breadcrumbs(
            [
                ("Home", "/"),
                ("YouTube Videos", "/youtube"),
                (breadcrumb_title, f"/video/{ref_id}"),
            ],
            right_text=f"Status: {video_status}",
        )
        ui.separator()

        if not video:
            with ui.card().classes("w-full bg-red-50 dark:bg-red-900/20"):
                ui.label(f"Video not found for ref_id: {ref_id}").classes(
                    "text-negative text-subtitle1"
                )
            return

        video_id_full = _get_video_id_from_platform(video)
        video_json = video.to_json()
        video_json["video_id"] = video_id_full

        _render_video_action_buttons(video_json, video_id_full)
        _render_video_json_details(video_json)
