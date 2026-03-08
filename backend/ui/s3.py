from nicegui import run, ui

from backend.config.env import env
from backend.exception.app_exception import AppException
from backend.integration.storage.s3_storage import S3Storage


def render_breadcrumbs(items: list[tuple[str, str]]) -> None:
    """Render breadcrumb navigation.
    
    Args:
        items: List of (label, url) tuples. Last item is current page (no link).
    """
    with ui.row().classes("items-center gap-2 mb-3 text-sm"):
        for index, (label, url) in enumerate(items):
            if index > 0:
                ui.label("/").classes("text-gray-400")
            
            if index == len(items) - 1:
                # Current page - no link
                ui.label(label).classes("text-gray-600 dark:text-gray-400 font-medium")
            else:
                # Clickable breadcrumb
                ui.link(label, url).classes(
                    "text-blue-600 dark:text-blue-400 hover:underline"
                )


async def s3_bucket_page() -> None:
    with ui.card().classes("w-full page-transition"):
        with ui.row().classes("items-center justify-between w-full mb-4"):
            ui.label("S3 Bucket Items").classes("text-h4")
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

        render_breadcrumbs([("Home", "/"), ("S3 Bucket", "/s3")])
        ui.separator()

        with ui.row().classes("w-full items-end gap-3 my-4 flex-wrap"):
            prefix_input = (
                ui.input(label="Prefix", placeholder="images/ or json/")
                .props("outlined clearable dense")
                .classes("min-w-[260px]")
            )
            max_keys_input = (
                ui.number(label="Max Keys", value=200, min=1, max=5000)
                .props("outlined dense")
                .classes("w-40")
            )
            table_container = ui.column().classes("w-full")

            async def load_items() -> None:
                table_container.clear()

                prefix = str(prefix_input.value or "").strip()
                max_keys_raw = max_keys_input.value
                try:
                    max_keys = int(max_keys_raw) if max_keys_raw else 200
                except (TypeError, ValueError):
                    ui.notify("Max Keys must be a valid number", type="negative")
                    return

                try:
                    items = await run.io_bound(
                        S3Storage().list_items, prefix=prefix, max_keys=max_keys
                    )
                except AppException:
                    with table_container:
                        ui.label(
                            f"Failed to load S3 items from bucket '{env.AWS_S3_BUCKET}'"
                        ).classes("text-negative")
                    ui.notify("Failed to load S3 items", type="negative")
                    return

                with table_container:
                    active_prefix = prefix if prefix else "/"
                    ui.label(
                        f"Bucket: {env.AWS_S3_BUCKET} | Prefix: {active_prefix} | Items: {len(items)}"
                    ).classes("text-subtitle1 mb-3")

                    if not items:
                        ui.label("No items found for the selected prefix.").classes(
                            "text-grey-7"
                        )
                        return

                    with ui.column().classes(
                        "w-full gap-0 border border-gray-300 dark:border-slate-600 rounded"
                    ):
                        with ui.row().classes(
                            "w-full bg-gray-100 dark:bg-slate-800 border-b border-gray-300 dark:border-slate-600 p-3 font-bold flex-nowrap items-center gap-3"
                        ):
                            ui.label("Name").classes("w-1/5")
                            ui.label("Type").classes("w-1/12")
                            ui.label("Key").classes("w-1/5")
                            ui.label("S3 Path").classes("w-1/3")
                            ui.label("Local Path").classes("w-1/4")

                        for item in items:
                            with ui.row().classes(
                                "w-full p-3 hover:bg-blue-50 dark:hover:bg-blue-900/40 items-start flex-nowrap border-b border-gray-200 dark:border-slate-700 gap-3"
                            ):
                                ui.label(item.name).classes("w-1/5 text-sm break-all")
                                ui.label(item.content_type.value).classes(
                                    "w-1/12 text-sm"
                                )
                                ui.label(item.key or "-").classes(
                                    "w-1/5 text-sm break-all"
                                )
                                ui.label(item.s3_key).classes(
                                    "w-1/3 text-sm font-mono break-all"
                                )
                                ui.label(item.downloaded_path).classes(
                                    "w-1/4 text-sm font-mono break-all"
                                )

            ui.button("Load Items", icon="search", on_click=load_items).props(
                "color=primary"
            )

            await load_items()
