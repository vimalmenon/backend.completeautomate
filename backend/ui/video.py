from datetime import datetime

from nicegui import ui

from backend.config.env import env
from backend.data import YouTubeTranscriptDBData
from backend.database.youtube import YouTubeVideoDB, YouTubeVideoMetadataSuggesterDB


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


def render_metadata_suggestions(video_id: str) -> None:
    suggestion = YouTubeVideoMetadataSuggesterDB().fetch_suggestion(
        channel_id=env.YOUTUBE_CHANNEL_ID,
        video_id=video_id,
    )
    if not suggestion:
        return

    with ui.column().classes(
        "w-full gap-3 mt-2 p-3 bg-amber-50 dark:bg-amber-900/20 rounded border border-amber-200 dark:border-amber-700"
    ):
        ui.label("Metadata Suggestions").classes("text-subtitle1 font-semibold")
        if suggestion.comment:
            with ui.row().classes("w-full gap-4 items-start"):
                ui.label("Comment:").classes("w-1/5 font-bold text-amber-700 text-sm")
                ui.label(str(suggestion.comment)).classes("w-4/5 text-wrap text-sm")

        for index, detail in enumerate(suggestion.video_details, start=1):
            with ui.card().classes("w-full bg-white dark:bg-slate-800"):
                ui.label(f"Option {index} ({detail.status.value})").classes(
                    "text-sm font-semibold text-amber-700"
                )
                with ui.row().classes("w-full gap-4 items-start"):
                    ui.label("Title:").classes("w-1/5 font-bold text-sm")
                    ui.label(detail.title).classes("w-4/5 text-wrap text-sm")
                render_multiline_field("description", detail.description)
                with ui.row().classes("w-full gap-4 items-start"):
                    ui.label("Tags:").classes("w-1/5 font-bold text-sm")
                    ui.label(", ".join(detail.tags) if detail.tags else "-").classes(
                        "w-4/5 text-wrap text-sm"
                    )


def save_video_details(ref_id: str, title: str, description: str) -> None:
    try:
        YouTubeVideoDB(channel_id=env.YOUTUBE_CHANNEL_ID).update_video_details(
            video_id=ref_id,
            title=title,
            description=description,
        )
        ui.notify("Video updated", type="positive")
        ui.run_javascript('window.location.href = "/youtube"')
    except Exception:
        ui.notify("Failed to update video", type="negative")


def save_transcript(ref_id: str, transcript_text: str, summarize_text: str) -> None:
    try:
        transcript = YouTubeTranscriptDBData(
            transcript=transcript_text,
            summarize=summarize_text,
        )
        YouTubeVideoDB(channel_id=env.YOUTUBE_CHANNEL_ID).update_transcript(
            video_id=ref_id,
            transcript=transcript,
        )
        ui.notify("Transcript updated", type="positive")
        ui.run_javascript('window.location.href = "/youtube"')
    except Exception:
        ui.notify("Failed to update transcript", type="negative")


def save_summarize(ref_id: str, transcript_text: str, summarize_text: str) -> None:
    try:
        transcript = YouTubeTranscriptDBData(
            transcript=transcript_text,
            summarize=summarize_text,
        )
        YouTubeVideoDB(channel_id=env.YOUTUBE_CHANNEL_ID).update_transcript(
            video_id=ref_id,
            transcript=transcript,
        )
        ui.notify("Summary updated", type="positive")
        ui.run_javascript('window.location.href = "/youtube"')
    except Exception:
        ui.notify("Failed to update summary", type="negative")


def open_edit_video_dialog(video_json: dict) -> None:
    with ui.dialog() as dialog, ui.card().classes("w-[900px] max-w-full"):
        ui.label("Edit Video").classes("text-h6")
        title_input = (
            ui.input(label="Title", value=str(video_json.get("title", "")))
            .props("outlined")
            .classes("w-full")
        )
        description_input = (
            ui.textarea(
                label="Description",
                value=str(video_json.get("description", "")),
            )
            .props("outlined autogrow")
            .classes("w-full")
        )

        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button(
                "Save",
                icon="save",
                on_click=lambda: save_video_details(
                    str(video_json.get("ref_id", "")),
                    str(title_input.value),
                    str(description_input.value),
                ),
            ).props("color=primary")
    dialog.open()


def open_edit_transcript_dialog(video_json: dict) -> None:
    transcript = video_json.get("transcript") or {}
    current_transcript = str(transcript.get("transcript", ""))
    current_summarize = str(transcript.get("summarize", ""))

    with ui.dialog() as dialog, ui.card().classes("w-[1000px] max-w-full"):
        ui.label("Edit Transcript").classes("text-h6")
        transcript_input = (
            ui.textarea(label="Transcript", value=current_transcript)
            .props("outlined autogrow")
            .classes("w-full")
        )

        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button(
                "Save",
                icon="save",
                on_click=lambda: save_transcript(
                    str(video_json.get("ref_id", "")),
                    str(transcript_input.value),
                    current_summarize,
                ),
            ).props("color=primary")
    dialog.open()


def open_edit_summarize_dialog(video_json: dict) -> None:
    transcript = video_json.get("transcript") or {}
    current_transcript = str(transcript.get("transcript", ""))
    current_summarize = str(transcript.get("summarize", ""))

    with ui.dialog() as dialog, ui.card().classes("w-[1000px] max-w-full"):
        ui.label("Edit Summarize").classes("text-h6")
        summarize_input = (
            ui.textarea(label="Summarize", value=current_summarize)
            .props("outlined autogrow")
            .classes("w-full")
        )

        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button(
                "Save",
                icon="save",
                on_click=lambda: save_summarize(
                    str(video_json.get("ref_id", "")),
                    current_transcript,
                    str(summarize_input.value),
                ),
            ).props("color=primary")
    dialog.open()


def youtube_page(page: str):
    with ui.card().classes("w-full page-transition"):
        with ui.row().classes("items-center justify-between w-full mb-4"):
            ui.label("YouTube Videos").classes("text-h4")
            with ui.row().classes("gap-2"):
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

        ui.separator()

        # Show loading spinner while fetching data
        with ui.row().classes("w-full items-center my-4") as loading_row:
            ui.spinner(size="lg", color="primary")
            ui.label("Loading YouTube videos...")

        # Fetch videos
        videos = YouTubeVideoDB(
            channel_id=env.YOUTUBE_CHANNEL_ID
        ).get_all_videos_from_db()
        videos = sorted(videos, key=lambda video: video.published_at, reverse=True)

        # Remove loading spinner and row
        loading_row.delete()

        if videos:
            ui.label(f"Found {len(videos)} video(s)").classes("text-subtitle1 mb-4")

            # Create custom expandable table
            with ui.column().classes(
                "w-full gap-0 border border-gray-300 dark:border-slate-600 rounded"
            ):
                # Table header
                with ui.row().classes(
                    "w-full bg-gray-100 dark:bg-slate-800 border-b border-gray-300 dark:border-slate-600 p-3 font-bold flex-nowrap items-center"
                ):
                    ui.label("Ref ID").classes("w-1/6")
                    ui.label("Title").classes("w-1/4")
                    ui.label("Description").classes("w-1/3")
                    ui.label("Published").classes("w-1/6")
                    ui.label("Expand").classes("w-1/12 text-center shrink-0")

                # Table rows
                for video in videos:
                    video_id_full = ""
                    try:
                        video_id_full = video.platform.video_id
                    except Exception:
                        video_id_full = ""

                    video_json = video.to_json()
                    video_id = video_json.get("ref_id", "")[:16]
                    title = video_json.get("title", "Untitled")
                    description = video_json.get("description", "")
                    short_description = (
                        description[:50] + "..."
                        if len(description) > 50
                        else description
                    )
                    published = video_json.get("published_at", "")

                    # Row container
                    with ui.column().classes(
                        "w-full gap-0 border-b border-gray-200 dark:border-slate-700"
                    ):
                        # Clickable row header
                        with ui.row().classes(
                            "w-full p-3 hover:bg-blue-50 dark:hover:bg-blue-900/40 items-center flex-nowrap"
                        ) as row_header:
                            ui.label(video_id).classes("w-1/6 text-sm")
                            ui.label(title).classes("w-1/4 text-sm font-medium")
                            ui.label(short_description).classes("w-1/3 text-sm")
                            ui.label(published).classes("w-1/6 text-sm")
                            # Icon container for toggling
                            with ui.row().classes(
                                "w-1/12 justify-center items-center shrink-0"
                            ):
                                expand_button = ui.button(icon="expand_more").props(
                                    'flat dense onclick="event.stopPropagation()" '
                                    'onmousedown="event.stopPropagation()"'
                                )

                        # Expandable details section
                        detail_section = ui.column().classes(
                            "w-full bg-blue-50 dark:bg-slate-800 p-4 gap-3 hidden"
                        )

                        def toggle_row(section, header, expand_btn):
                            """Toggle row expansion"""
                            is_hidden = "hidden" in section.classes
                            if is_hidden:
                                section.classes(remove="hidden")
                                expand_btn.props("icon=expand_less")
                                expand_btn.update()
                                header.classes(add="bg-blue-100 dark:bg-blue-900/40")
                            else:
                                section.classes(add="hidden")
                                expand_btn.props("icon=expand_more")
                                expand_btn.update()
                                header.classes(remove="bg-blue-100 dark:bg-blue-900/40")

                        def on_expand_click(
                            s=detail_section, h=row_header, eb=expand_button
                        ):
                            toggle_row(s, h, eb)

                        expand_button.on("click", on_expand_click)

                        # Populate detail section
                        with detail_section:
                            if video_id_full:
                                render_metadata_suggestions(video_id_full)

                            with ui.row().classes("w-full justify-end gap-2"):
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
                                    on_click=lambda current_video=video_json: open_edit_summarize_dialog(
                                        current_video
                                    ),
                                ).props("flat")

                            for key, value in video_json.items():
                                if key == "transcript" and isinstance(value, dict):
                                    transcript_text = str(value.get("transcript", ""))
                                    summarize_text = str(value.get("summarize", ""))

                                    render_multiline_field(
                                        "transcript", transcript_text
                                    )
                                    render_multiline_field("summarize", summarize_text)
                                    continue

                                if value is not None and not isinstance(value, list):
                                    display_val = (
                                        str(value)[:100] + "..."
                                        if len(str(value)) > 100
                                        else str(value)
                                    )
                                    with ui.row().classes("w-full gap-4 items-start"):
                                        ui.label(f"**{key}:**").classes(
                                            "w-1/5 font-bold text-blue-600 text-sm"
                                        )
                                        ui.label(display_val).classes(
                                            "w-4/5 text-wrap text-sm"
                                        )
        else:
            with ui.card().classes("w-full bg-gray-100 dark:bg-slate-800"):
                ui.icon("video_library", size="xl").classes("text-gray-400")
                ui.label("No videos found").classes("text-h6 text-gray-500")

        ui.separator().classes("my-4")
