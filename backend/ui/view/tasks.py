from nicegui import run, ui

from backend.data import TaskData
from backend.enum import TaskStatusEnum
from backend.manager import TaskManager
from backend.ui.common.component_common import (
    render_breadcrumbs,
    render_common_header,
    render_separator,
)

TASK_STATUS_PRIORITY = {
    TaskStatusEnum.NEW.value: 0,
    TaskStatusEnum.REVIEW.value: 1,
    TaskStatusEnum.FAILED.value: 2,
    TaskStatusEnum.IN_PROGRESS.value: 3,
    TaskStatusEnum.COMPLETED.value: 4,
}


def sort_tasks_by_priority(tasks: list[TaskData]) -> list[TaskData]:
    return sorted(
        tasks,
        key=lambda task: (
            TASK_STATUS_PRIORITY.get(task.status.value, 99),
            task.created_at,
        ),
        reverse=False,
    )


def get_status_row_class(status_value: str) -> str:
    if status_value == TaskStatusEnum.IN_PROGRESS.value:
        return (
            "bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/50"
        )
    if status_value == TaskStatusEnum.FAILED.value:
        return "bg-red-50 dark:bg-red-900/30 hover:bg-red-100 dark:hover:bg-red-900/50"
    if status_value == TaskStatusEnum.COMPLETED.value:
        return "bg-green-50 dark:bg-green-900/30 hover:bg-green-100 dark:hover:bg-green-900/50"
    return "hover:bg-blue-50 dark:hover:bg-blue-900/40"


async def tasks_page(status: str = ""):
    print(status)
    with ui.card().classes("w-full gap-0 page-transition"):
        render_common_header(page_title="Task Management")
        render_breadcrumbs(
            [("Home", "/"), ("Tasks", "/tasks")], "Manage scheduled tasks"
        )
        render_separator()

        # Show loading spinner while fetching tasks
        with ui.row().classes("w-full items-center my-4") as loading_row:
            ui.spinner(size="lg", color="primary")
            ui.label("Loading tasks...")

            # Fetch tasks from database (non-blocking)
            tasks = await run.io_bound(TaskManager().get_tasks)
            tasks = sort_tasks_by_priority(
                [task for task in tasks if not status or task.status == status]
            )

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
                    "w-full gap-0 bg-gray-100 dark:bg-slate-800 border-b border-gray-300 dark:border-slate-600 p-3 font-bold flex-nowrap items-center"
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
                    row_status_class = get_status_row_class(status)

                    with ui.row().classes(
                        f"w-full gap-0 p-3 items-center flex-nowrap border-b border-gray-200 dark:border-slate-700 {row_status_class}"
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
