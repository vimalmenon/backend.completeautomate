import json
from datetime import datetime

from nicegui import run, ui

from backend.data import JobData
from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.exception.app_exception import AppException
from backend.jobs_scheduler import JobScheduler
from backend.manager import JobManager
from backend.ui.common.component_common import (
    render_breadcrumbs,
    render_common_header,
    render_not_found_message,
)

TASK_STATUS_PRIORITY = {
    JobsStatusEnum.NEW.value: 0,
    JobsStatusEnum.REVIEW.value: 1,
    JobsStatusEnum.FAILED.value: 2,
    JobsStatusEnum.IN_PROGRESS.value: 3,
    JobsStatusEnum.COMPLETE.value: 4,
}

jobs_cards = [
    {"label": "All Jobs", "value": "", "icon": "hourglass_empty", "color": "violet"},
    {
        "label": "IN PROGRESS",
        "value": JobsStatusEnum.IN_PROGRESS.value,
        "icon": "schedule",
        "color": "blue",
    },
    {
        "label": "COMPLETED",
        "value": JobsStatusEnum.COMPLETE.value,
        "icon": "check_circle",
        "color": "green",
    },
    {
        "label": "IN REVIEW",
        "value": JobsStatusEnum.REVIEW.value,
        "icon": "hourglass_empty",
        "color": "gray",
    },
    {
        "label": "FAILED",
        "value": JobsStatusEnum.FAILED.value,
        "icon": "error",
        "color": "red",
    },
]


def sort_jobs_by_priority(jobs: list[JobData]) -> list[JobData]:
    return sorted(
        jobs,
        key=lambda job: (
            TASK_STATUS_PRIORITY.get(job.status.value, 99),
            job.created_at,
        ),
        reverse=False,
    )


def get_status_row_class(status_value: str) -> str:
    if status_value == JobsStatusEnum.IN_PROGRESS.value:
        return (
            "bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/50"
        )
    if status_value == JobsStatusEnum.FAILED.value:
        return "bg-red-50 dark:bg-red-900/30 hover:bg-red-100 dark:hover:bg-red-900/50"
    if status_value == JobsStatusEnum.COMPLETE.value:
        return "bg-green-50 dark:bg-green-900/30 hover:bg-green-100 dark:hover:bg-green-900/50"
    return "hover:bg-blue-50 dark:hover:bg-blue-900/40"


def make_jobs_navigation_handler(status: str):
    def _handler() -> None:
        target = f"/jobs?status={status}" if status else "/jobs"
        ui.run_javascript(f'window.location.href = "{target}"')

    return _handler


def get_status_count(jobs: list[JobData], status: str) -> int:
    if not status:
        return len(jobs)
    return sum(1 for job in jobs if job.status.value == status)


def run_job_now(job_id: str) -> None:
    try:
        ui.notify(f"Running job: {job_id}", type="info")
        JobScheduler().start(job_id=job_id)
        ui.notify("Job run completed", type="positive")
        ui.run_javascript(
            "window.location.href = window.location.pathname + window.location.search"
        )
    except Exception:
        ui.notify("Failed to run job", type="negative")


def show_run_job_confirmation(job_id: str) -> None:
    """Show confirmation dialog before running a job."""
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Confirm Job Execution").classes("text-h6 mb-4")
        ui.label("Are you sure you want to run this job?").classes("mb-4")

        def on_confirm() -> None:
            dialog.close()
            run_job_now(job_id)

        with ui.row().classes("w-full justify-end gap-2"):
            ui.button(
                "Cancel",
                on_click=dialog.close,
            ).props("flat")
            ui.button(
                "Confirm",
                on_click=on_confirm,
                color="primary",
            )

    dialog.open()


def show_edit_status_dialog(job: JobData) -> None:
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Edit Job Status").classes("text-h6 mb-2")
        ui.label(f"Job ID: {job.id}").classes("text-caption text-gray-600 mb-2")

        status_options = [status.value for status in JobsStatusEnum]
        status_input = (
            ui.select(
                options=status_options,
                value=job.status.value,
                label="Status",
            )
            .props("outlined dense")
            .classes("w-full")
        )

        def on_save() -> None:
            old_status = job.status
            try:
                job.status = JobsStatusEnum(str(status_input.value))
                JobManager().update_job_status(job.id, job.status)
                ui.notify("Job status updated", type="positive")
                dialog.close()
                ui.run_javascript(
                    "window.location.href = window.location.pathname + window.location.search"
                )
            except (ValueError, AppException):
                job.status = old_status
                ui.notify("Failed to update job status", type="negative")

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Save", icon="save", on_click=on_save).props("color=primary")

    dialog.open()


def add_job(
    selected_job_type: str,
    selected_status: str,
    payload_text: str,
) -> None:
    try:
        payload = json.loads(payload_text.strip() or "{}")
        if not isinstance(payload, dict):
            ui.notify("Payload must be a JSON object", type="negative")
            return

        status = JobsStatusEnum(selected_status)
        job = JobData(
            id=JobManager()
            .create_job(
                type=JobTypeEnum(selected_job_type),
                task_data=payload,
                description=selected_job_type,
                status=status,
            )
            .id,
            status=status,
            type=JobTypeEnum(selected_job_type),
            task_data=payload,
            description=selected_job_type,
            created_at=datetime.now(),
            completed_at=(
                datetime.now() if status == JobsStatusEnum.COMPLETE else None
            ),
        )
        JobManager().save_job(job)
        ui.notify("Job created", type="positive")
        ui.run_javascript(
            "window.location.href = window.location.pathname + window.location.search"
        )
    except json.JSONDecodeError:
        ui.notify("Invalid payload JSON", type="negative")
    except Exception as ex:
        ui.notify(f"Failed to create job: {ex}", type="negative")


def render_add_job_form() -> None:
    job_options = [job.value for job in JobTypeEnum]
    status_options = [status.value for status in JobsStatusEnum]

    with ui.dialog() as add_job_dialog, ui.card().classes("w-[720px] max-w-full"):
        ui.label("Add New Job").classes("text-h6 mb-2")

        with ui.row().classes("w-full gap-3 items-end flex-wrap"):
            job_type_input = (
                ui.select(
                    options=job_options,
                    value=job_options[0] if job_options else None,
                    label="Job Type",
                )
                .props("outlined dense")
                .classes("w-1/3 min-w-[200px]")
            )
            status_input = (
                ui.select(
                    options=status_options,
                    value=JobsStatusEnum.NEW.value,
                    label="Status",
                )
                .props("outlined dense")
                .classes("w-1/3 min-w-[200px]")
            )

        payload_input = (
            ui.textarea(label="Payload (JSON)", value="{}")
            .props("outlined autogrow")
            .classes("w-full mt-3")
        )

        with ui.row().classes("w-full justify-end mt-3 gap-2"):
            ui.button("Cancel", on_click=add_job_dialog.close).props("flat")
            ui.button(
                "Create Job",
                icon="add",
                on_click=lambda: add_job(
                    str(job_type_input.value),
                    str(status_input.value),
                    str(payload_input.value),
                ),
            ).props("color=primary")

    ui.button("Add Job", icon="add", on_click=add_job_dialog.open).props(
        "color=primary"
    ).classes("my-3")


async def jobs_page(status: str = ""):
    with ui.card().classes("w-full gap-0 page-transition"):
        render_common_header(page_title="Job Management")
        render_breadcrumbs([("Home", "/"), ("Jobs", "/jobs")], "Manage scheduled jobs")

        # Show loading spinner while fetching jobs
        with ui.row().classes("w-full items-center my-4") as loading_row:
            ui.spinner(size="lg", color="primary")
            ui.label("Loading jobs...")

            # Fetch jobs from database (non-blocking)
            all_jobs = await run.io_bound(JobManager().get_all_jobs)
            jobs = sort_jobs_by_priority(
                [
                    job
                    for job in all_jobs
                    if not status
                    or str(getattr(job.status, "value", job.status)) == status
                ]
            )

        # Remove loading indicator
        loading_row.delete()

        with ui.row().classes("w-full gap-4 mb-4 flex-wrap"):
            for stat in jobs_cards:
                with (
                    ui.card()
                    .classes(
                        f"flex-1 min-w-[180px] shadow-sm hover:shadow-md transition-shadow border-t-4 border-{stat['color']}-500 cursor-pointer"
                    )
                    .on("click", make_jobs_navigation_handler(stat["value"]))
                ):
                    with ui.avatar(color=stat["color"], text_color="white", size="sm"):
                        ui.icon(stat["icon"], size="sm")
                    with ui.column().classes("gap-0"):
                        ui.label(stat["label"]).classes("text-subtitle2 text-gray-600")
                        ui.label(
                            str(get_status_count(all_jobs, stat["value"]))
                        ).classes("text-h6 font-bold")

        if status:
            ui.label(f"Active filter: {status}").classes("text-caption text-gray-600")

        render_add_job_form()

        if not jobs:
            render_not_found_message(message="No jobs found", icon="inbox")

        else:
            ui.label(f"Found {len(jobs)} job(s)").classes("text-subtitle1 mb-4")

            # Create custom table
            with ui.column().classes(
                "w-full gap-0 border border-gray-300 dark:border-slate-600 rounded"
            ):
                # Table header
                with ui.row().classes(
                    "w-full gap-0 bg-gray-100 dark:bg-slate-800 border-b border-gray-300 dark:border-slate-600 p-3 font-bold flex-nowrap items-center"
                ):
                    ui.label("Job ID").classes("w-1/5")
                    ui.label("Job Type").classes("w-1/5")
                    ui.label("Status").classes("w-1/8")
                    ui.label("Created At").classes("w-1/8")
                    ui.label("Actions").classes("w-1/6 text-right shrink-0")

                # Table rows
                for job in jobs:
                    job_json = job.to_json()
                    job_id = job_json.get("id", "")
                    job_type = job_json.get("type", "")
                    job_status = job_json.get("status", "")
                    created_at = job_json.get("created_at", "")[:19]
                    row_status_class = get_status_row_class(job_status)

                    with ui.row().classes(
                        f"w-full gap-0 p-3 items-center flex-nowrap border-b border-gray-200 dark:border-slate-700 {row_status_class}"
                    ):
                        ui.label(job_id).classes("w-1/5 text-sm")
                        ui.label(job_type).classes("w-1/5 text-sm")
                        ui.label(job_status).classes("w-1/8 text-sm")
                        ui.label(created_at).classes("w-1/8 text-sm font-medium")

                        # Action cell
                        with ui.row().classes(
                            "w-1/6 justify-end items-center gap-1 shrink-0"
                        ):
                            ui.button(
                                icon="edit",
                                on_click=lambda current_job=job: show_edit_status_dialog(
                                    current_job
                                ),
                            ).props(
                                'flat dense onclick="event.stopPropagation()" onmousedown="event.stopPropagation()"'
                            )
                            if job_status in [
                                JobsStatusEnum.IN_PROGRESS.value,
                                JobsStatusEnum.FAILED.value,
                            ]:
                                ui.button(
                                    icon="play_arrow",
                                    on_click=lambda current_job_id=job_id: show_run_job_confirmation(
                                        current_job_id
                                    ),
                                ).props(
                                    'flat dense onclick="event.stopPropagation()" onmousedown="event.stopPropagation()"'
                                )

