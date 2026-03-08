from nicegui import run, ui

from backend.manager import TaskManager


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


async def tasks_page():
    with ui.card().classes("w-full page-transition"):
        with ui.row().classes("items-center justify-between w-full mb-4"):
            ui.label("Task Management").classes("text-h4")
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

        render_breadcrumbs(
            [("Home", "/"), ("Tasks", "/tasks")], "Manage scheduled tasks"
        )
        ui.separator()

        # Show loading spinner while fetching tasks
        with ui.row().classes("w-full items-center my-4") as loading_row:
            ui.spinner(size="lg", color="primary")
            ui.label("Loading tasks...")

            # Fetch tasks from database (non-blocking)
            tasks = await run.io_bound(TaskManager().get_tasks)

        # Remove loading indicator
        loading_row.delete()

        if not tasks:
            with ui.card().classes("w-full bg-gray-100 dark:bg-slate-800"):
                ui.icon("inbox", size="xl").classes("text-gray-400")
                ui.label("No tasks found").classes("text-h6 text-gray-500")
        else:
            ui.label(f"Found {len(tasks)} task(s)").classes("text-subtitle1 mb-4")

            # Create custom table
            with ui.column().classes(
                "w-full gap-0 border border-gray-300 dark:border-slate-600 rounded"
            ):
                # Table header
                with ui.row().classes(
                    "w-full bg-gray-100 dark:bg-slate-800 border-b border-gray-300 dark:border-slate-600 p-3 font-bold flex-nowrap items-center"
                ):
                    ui.label("Task ID").classes("w-1/5")
                    ui.label("Job Type").classes("w-1/5")
                    ui.label("Status").classes("w-1/8")
                    ui.label("Created By").classes("w-1/8")
                    ui.label("Created At").classes("w-1/8")
                    ui.label("Actions").classes("w-1/6 text-right shrink-0")

            # Table rows
            for task in tasks:
                task_json = task.to_json()
                task_id = task_json.get("id", "")
                task_type = task_json.get("job_type", "")
                status = task_json.get("status", "")
                created_by = task_json.get("created_by", "")
                created_at = task_json.get("created_at", "")[:19]
                row_status_class = "green"

                # Row container
                with ui.column().classes(
                    "w-full gap-0 border-b border-gray-200 dark:border-slate-700"
                ):
                    # Row header
                    with ui.row().classes(
                        f"w-full p-3 items-center flex-nowrap {row_status_class}"
                    ):
                        ui.label(task_id).classes("w-1/5 text-sm")
                        ui.label(task_type[:20]).classes("w-1/5 text-sm")
                        ui.label(status).classes("w-1/8 text-sm")
                        ui.label(created_by).classes("w-1/8 text-sm")
                        ui.label(created_at).classes("w-1/8 text-sm font-medium")

                        # Action cell
                        with ui.row().classes(
                            "w-1/6 justify-end items-center gap-1 shrink-0"
                        ):
                            ui.button(
                                icon="play_arrow",
                                # on_click=lambda current_task_id=task_id: show_run_task_confirmation(
                                #     current_task_id
                                # ),
                            ).props(
                                'flat dense onclick="event.stopPropagation()" onmousedown="event.stopPropagation()"'
                            )
                            ui.button(
                                icon="open_in_new",
                                # on_click=lambda current_task_id=task_id: ui.run_javascript(
                                #     f'window.location.href = "/task/{current_task_id}"'
                                # ),
                            ).props(
                                'flat dense onclick="event.stopPropagation()" onmousedown="event.stopPropagation()"'
                            )
