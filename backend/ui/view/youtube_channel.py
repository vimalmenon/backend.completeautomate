from datetime import datetime

from nicegui import run, ui

from backend.data import PlatformDBData, PlatformYouTubeChannelDBData
from backend.database.youtube import YouTubeChannelDB
from backend.enum import PlatformEnum


def render_breadcrumbs(items: list[tuple[str, str]], right_text: str = "") -> None:
    """Render breadcrumb navigation.

    Args:
        items: List of (label, url) tuples. Last item is current page (no link).
        right_text: Optional text to display on the right side.
    """
    with ui.row().classes("items-center justify-between w-full mb-3 text-sm"):
        with ui.row().classes("items-center gap-2"):
            for index, (label, url) in enumerate(items):
                if index > 0:
                    ui.label("/").classes("text-gray-400")

                if index == len(items) - 1:
                    # Current page - no link
                    ui.label(label).classes(
                        "text-gray-600 dark:text-gray-400 font-medium"
                    )
                else:
                    # Clickable breadcrumb
                    ui.link(label, url).classes(
                        "text-blue-600 dark:text-blue-400 hover:underline"
                    )

        if right_text:
            ui.label(right_text).classes("text-gray-500 dark:text-gray-400 text-xs")


def open_channel_stats_chart_dialog(channel_json: dict) -> None:
    """Open a dialog with line chart showing channel stats over time."""
    stats = channel_json.get("stats", [])

    if not stats:
        ui.notify("No stats data available", type="warning")
        return

    # Parse stats data
    timestamps = []
    subscribers = []
    views = []
    videos = []

    for stat in stats:
        try:
            timestamp_str = stat.get("timestamp", "")
            timestamps.append(datetime.fromisoformat(timestamp_str))
            subscribers.append(int(stat.get("subscriber_count", 0)))
            views.append(int(stat.get("view_count", 0)))
            videos.append(int(stat.get("video_count", 0)))
        except (ValueError, TypeError):
            continue

    if not timestamps:
        ui.notify("No valid stats data to display", type="warning")
        return

    # Format timestamps for display
    time_labels = [ts.strftime("%Y-%m-%d %H:%M") for ts in timestamps]

    with ui.dialog() as dialog, ui.card().classes("w-[1100px] max-w-full"):
        ui.label(f"Stats for: {channel_json.get('title', 'Channel')}").classes(
            "text-h6 mb-4"
        )

        # Create plotly chart
        import plotly.graph_objects as go

        fig = go.Figure()

        # Add traces for each metric
        fig.add_trace(
            go.Scatter(
                x=time_labels,
                y=subscribers,
                mode="lines+markers",
                name="Subscribers",
                line=dict(color="#2196F3", width=2),
                marker=dict(size=6),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=time_labels,
                y=views,
                mode="lines+markers",
                name="Views",
                line=dict(color="#4CAF50", width=2),
                marker=dict(size=6),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=time_labels,
                y=videos,
                mode="lines+markers",
                name="Videos",
                line=dict(color="#FF9800", width=2),
                marker=dict(size=6),
            )
        )

        # Update layout
        fig.update_layout(
            title="Channel Statistics Over Time",
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
                ui.label("Latest Subscribers").classes("text-sm text-gray-600")
                ui.label(f"{subscribers[-1]:,}").classes(
                    "text-2xl font-bold text-blue-600"
                )
            with ui.card().classes("flex-1"):
                ui.label("Latest Views").classes("text-sm text-gray-600")
                ui.label(f"{views[-1]:,}").classes("text-2xl font-bold text-green-600")
            with ui.card().classes("flex-1"):
                ui.label("Latest Videos").classes("text-sm text-gray-600")
                ui.label(f"{videos[-1]:,}").classes(
                    "text-2xl font-bold text-orange-600"
                )

        with ui.row().classes("w-full justify-end mt-4"):
            ui.button("Close", on_click=dialog.close).props("flat")

    dialog.open()


def _render_channel_page_header(channel_json: dict | None = None) -> None:
    with ui.row().classes("items-center justify-between w-full mb-4"):
        ui.label("Channel Details").classes("text-h4")
        with ui.row().classes("gap-2"):
            if channel_json and channel_json.get("stats"):
                ui.button(
                    "View Stats",
                    icon="bar_chart",
                    on_click=lambda: open_channel_stats_chart_dialog(channel_json),
                ).props("color=primary")
            ui.button(
                "Back to Videos",
                icon="arrow_back",
                on_click=lambda: ui.run_javascript('window.location.href = "/youtube"'),
            ).props("flat")
            ui.button(
                icon="home",
                on_click=lambda: ui.run_javascript('window.location.href = "/"'),
            ).props("flat")


def _render_channel_identity(channel_json: dict) -> None:
    # Channel banner if available.
    if channel_json.get("banner_image_url"):
        with ui.image(channel_json["banner_image_url"]).classes(
            "w-full h-48 object-cover mb-4 rounded"
        ):
            pass

    with ui.row().classes("w-full gap-6 items-start"):
        # Thumbnail on the left
        if channel_json.get("thumbnail_url"):
            ui.image(channel_json["thumbnail_url"]).classes(
                "w-32 h-32 rounded-full flex-shrink-0"
            )

        # Channel info in the middle
        with ui.column().classes("flex-1 gap-3"):
            # Channel name
            ui.label(channel_json.get("title", "")).classes(
                "text-h5 font-bold text-gray-900 dark:text-white"
            )

            # URL
            if channel_json.get("custom_url"):
                url_text = channel_json["custom_url"]
                with ui.row().classes("w-full items-center gap-2"):
                    ui.label("URL:").classes(
                        "font-semibold text-sm text-gray-700 dark:text-gray-300"
                    )
                    ui.label(url_text).classes(
                        "text-sm text-blue-600 dark:text-blue-400"
                    )

            # Country
            if channel_json.get("country"):
                with ui.row().classes("w-full items-center gap-2"):
                    ui.label("Country:").classes(
                        "font-semibold text-sm text-gray-700 dark:text-gray-300"
                    )
                    ui.label(channel_json["country"]).classes(
                        "text-sm text-gray-600 dark:text-gray-400"
                    )

            # Description
            description = channel_json.get("description", "").strip()
            if description:
                with ui.column().classes("w-full mt-2"):
                    ui.label("About").classes(
                        "text-sm font-semibold text-gray-700 dark:text-gray-300"
                    )
                    ui.label(description).classes(
                        "text-sm text-gray-600 dark:text-gray-400 text-wrap"
                    )


def _render_channel_metadata(channel_json: dict) -> None:
    with ui.card().classes("w-full dark:bg-slate-800"):
        ui.label("Metadata").classes("text-h6 mb-3")

        with ui.row().classes("w-full gap-4 items-start"):
            ui.label("Status:").classes("w-1/4 font-bold")
            ui.label(channel_json.get("privacy_status", "")).classes("w-3/4")

        with ui.row().classes("w-full gap-4 items-start"):
            ui.label("Made for Kids:").classes("w-1/4 font-bold")
            ui.label(str(channel_json.get("made_for_kids", False))).classes("w-3/4")

        with ui.row().classes("w-full gap-4 items-start"):
            ui.label("Published:").classes("w-1/4 font-bold")
            ui.label(channel_json.get("published_at", "")).classes("w-3/4")

        with ui.row().classes("w-full gap-4 items-start"):
            ui.label("Last Updated:").classes("w-1/4 font-bold")
            ui.label(channel_json.get("last_updated_at", "")).classes("w-3/4")


def _render_channel_description(channel_json: dict) -> None:
    description = channel_json.get("description")
    if description:
        with ui.card().classes("w-full dark:bg-slate-800"):
            ui.label("Description").classes("text-h6 mb-3")
            ui.label(description).classes("w-full text-wrap text-sm")


def _render_channel_statistics(channel_json: dict) -> None:
    stats = channel_json.get("stats")
    latest_stats = None

    # Get latest stats from the stats array, or use channel-level stats
    if stats and len(stats) > 0:
        latest_stats = stats[-1]

    # If no stats array, try to get stats from channel_json directly
    if not latest_stats:
        latest_stats = {
            "subscriber_count": channel_json.get("subscriber_count", 0),
            "view_count": channel_json.get("view_count", 0),
            "video_count": channel_json.get("video_count", 0),
        }

    # Only render if we have at least some stats
    if not latest_stats or all(v in (None, 0, "0") for v in latest_stats.values()):
        return

    with ui.card().classes("w-full dark:bg-slate-800"):
        ui.label("Channel Statistics").classes("text-h6 mb-4 font-bold")

        with ui.row().classes("w-full gap-4 justify-between"):
            # Subscribers card
            subscriber_count = latest_stats.get("subscriber_count", 0)
            if isinstance(subscriber_count, str):
                sub_display = subscriber_count
            else:
                sub_display = f"{int(subscriber_count):,}" if subscriber_count else "0"

            with ui.column().classes(
                "flex-1 px-4 py-3 bg-blue-50 dark:bg-blue-900/20 rounded"
            ):
                ui.label("Subscribers").classes(
                    "text-sm font-semibold text-gray-700 dark:text-gray-300"
                )
                ui.label(sub_display).classes(
                    "text-h5 font-bold text-blue-600 dark:text-blue-400 mt-2"
                )

            # Views card
            view_count = latest_stats.get("view_count", 0)
            if isinstance(view_count, str):
                view_display = view_count
            else:
                view_display = f"{int(view_count):,}" if view_count else "0"

            with ui.column().classes(
                "flex-1 px-4 py-3 bg-green-50 dark:bg-green-900/20 rounded"
            ):
                ui.label("Total Views").classes(
                    "text-sm font-semibold text-gray-700 dark:text-gray-300"
                )
                ui.label(view_display).classes(
                    "text-h5 font-bold text-green-600 dark:text-green-400 mt-2"
                )

            # Videos card
            video_count = latest_stats.get("video_count", 0)
            if isinstance(video_count, str):
                video_display = video_count
            else:
                video_display = f"{int(video_count):,}" if video_count else "0"

            with ui.column().classes(
                "flex-1 px-4 py-3 bg-purple-50 dark:bg-purple-900/20 rounded"
            ):
                ui.label("Videos").classes(
                    "text-sm font-semibold text-gray-700 dark:text-gray-300"
                )
                ui.label(video_display).classes(
                    "text-h5 font-bold text-purple-600 dark:text-purple-400 mt-2"
                )


def _render_channel_detail_header() -> None:
    """Render channel detail page header with navigation."""
    with ui.row().classes("items-center justify-between w-full mb-4"):
        ui.label("Channel Details").classes("text-h4")
        with ui.row().classes("gap-2"):
            ui.button(
                "Back to Videos",
                icon="arrow_back",
                on_click=lambda: ui.run_javascript('window.location.href = "/youtube"'),
            ).props("flat")
            ui.button(
                icon="home",
                on_click=lambda: ui.run_javascript('window.location.href = "/"'),
            ).props("flat")


def _render_channel_identity_with_button(channel_json: dict, channel_id: str) -> None:
    """Render channel identity card with image, info, and visit button."""
    with ui.card().classes("w-full border-t-4 border-red-500"):
        # Top section: Image, info, and button
        with ui.row().classes("gap-6 items-start w-full justify-between"):
            # Channel thumbnail
            if channel_json.get("thumbnail_url"):
                ui.image(channel_json.get("thumbnail_url", "")).classes(
                    "w-32 h-32 rounded-full flex-shrink-0 object-cover"
                )

            # Channel info section
            with ui.column().classes("flex-1 gap-2"):
                # Channel name
                ui.label(channel_json.get("title", "")).classes(
                    "text-h6 font-bold text-gray-900 dark:text-white"
                )

                # Channel URL
                custom_url = channel_json.get("custom_url")
                if isinstance(custom_url, str) and custom_url:
                    with ui.row().classes("items-center gap-2"):
                        ui.label("URL:").classes(
                            "font-semibold text-sm text-gray-700 dark:text-gray-300"
                        )
                        ui.label(custom_url).classes(
                            "text-sm text-blue-600 dark:text-blue-400 break-all"
                        )

                # Country
                country = channel_json.get("country")
                if isinstance(country, str) and country:
                    with ui.row().classes("items-center gap-2"):
                        ui.label("Country:").classes(
                            "font-semibold text-sm text-gray-700 dark:text-gray-300"
                        )
                        ui.label(country).classes(
                            "text-sm text-gray-600 dark:text-gray-400"
                        )

                # Description
                description = channel_json.get("description", "").strip()
                if description:
                    with ui.column().classes("w-full mt-2"):
                        ui.label("About").classes(
                            "text-sm font-semibold text-gray-700 dark:text-gray-300"
                        )
                        ui.label(description).classes(
                            "text-sm text-gray-600 dark:text-gray-400 text-wrap"
                        )

            # Navigation button on the right
            with ui.column().classes("flex-shrink-0"):
                ui.button(
                    "Visit Channel",
                    icon="open_in_new",
                    on_click=lambda: ui.run_javascript(
                        f'window.open("https://www.youtube.com/channel/{channel_id}", "_blank")'
                    ),
                ).props("color=red")


def _render_channel_info_card(channel_json: dict) -> None:
    """Render channel information metadata card."""
    with ui.card().classes("w-full dark:bg-slate-800 mb-4"):
        ui.label("Channel Information").classes("text-h6 mb-3 font-bold")
        with ui.row().classes("w-full gap-4 items-center"):
            if channel_json.get("privacy_status"):
                with ui.column().classes("gap-1"):
                    ui.label("Status").classes(
                        "text-sm font-semibold text-gray-700 dark:text-gray-300"
                    )
                    ui.label(channel_json.get("privacy_status", "")).classes(
                        "text-sm text-gray-600 dark:text-gray-400"
                    )

            if channel_json.get("published_at"):
                with ui.column().classes("gap-1"):
                    ui.label("Published").classes(
                        "text-sm font-semibold text-gray-700 dark:text-gray-300"
                    )
                    ui.label(channel_json.get("published_at", "")).classes(
                        "text-sm text-gray-600 dark:text-gray-400"
                    )

            if channel_json.get("last_updated_at"):
                with ui.column().classes("gap-1"):
                    ui.label("Last Updated").classes(
                        "text-sm font-semibold text-gray-700 dark:text-gray-300"
                    )
                    ui.label(channel_json.get("last_updated_at", "")).classes(
                        "text-sm text-gray-600 dark:text-gray-400"
                    )

            if channel_json.get("made_for_kids") is not None:
                with ui.column().classes("gap-1"):
                    ui.label("Made for Kids").classes(
                        "text-sm font-semibold text-gray-700 dark:text-gray-300"
                    )
                    ui.label(str(channel_json.get("made_for_kids", False))).classes(
                        "text-sm text-gray-600 dark:text-gray-400"
                    )


async def youtube_channel_page(channel_id: str, tab: str | None = None) -> None:
    """Render the detailed channel page."""
    platform = PlatformDBData(
        platform_type=PlatformEnum.YouTubeChannel,
        data=PlatformYouTubeChannelDBData(channel_id=channel_id),
    )
    try:
        channel = await run.io_bound(
            YouTubeChannelDB(ref_id=platform.ref_id).query_channel
        )
    except Exception:
        channel = None

    if not channel:
        with ui.card().classes("w-full page-transition"):
            _render_channel_page_header()
            render_breadcrumbs(
                [
                    ("Home", "/"),
                    ("YouTube Videos", "/youtube"),
                    ("Channel", f"/youtube/{channel_id}"),
                ],
                right_text="Channel not found",
            )
            ui.separator()
            with ui.card().classes("w-full bg-red-50 dark:bg-red-900/20"):
                ui.label(f"Channel not found for id: {channel_id}").classes(
                    "text-negative text-subtitle1"
                )
        return

    channel_json = channel.to_json()
    channel_title = channel_json.get("title", "Channel")
    breadcrumb_title = (
        channel_title[:30] + "..." if len(channel_title) > 30 else channel_title
    )

    with ui.card().classes("w-full page-transition"):
        _render_channel_detail_header()
        render_breadcrumbs(
            [
                ("Home", "/"),
                ("YouTube Videos", "/youtube"),
                (breadcrumb_title, f"/youtube/{channel_id}"),
            ],
            right_text=f"Subscribers: {channel_json.get('subscriber_count', 'N/A')}",
        )
        ui.separator()
        _render_channel_identity_with_button(channel_json, channel_id)
        ui.separator()
        _render_channel_info_card(channel_json)
        ui.separator()
        _render_channel_statistics(channel_json)
        _render_channel_description(channel_json)
