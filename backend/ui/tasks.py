from datetime import datetime
from typing import Any
from uuid import uuid4

from nicegui import ui

from backend.data.task import TaskData
from backend.database.task.task_db import TaskDB
from backend.enum.image import ImageTypeEnum
from backend.enum.job import JobEnum
from backend.enum.status import TaskStatusEnum
from backend.enum.team import TeamEnum
from backend.exception.app_exception import AppException
from backend.task_scheduler_services import TaskSchedulerServices

DETAIL_EXCLUDED_KEYS = {
    "id",
    "job_type",
    "created_by",
    "created_at",
    "completed_at",
    "status",
}

TASK_STATUS_PRIORITY = {
    TaskStatusEnum.NEW.value: 0,
    TaskStatusEnum.REVIEW.value: 1,
    TaskStatusEnum.FAILED.value: 2,
    TaskStatusEnum.IN_PROGRESS.value: 3,
    TaskStatusEnum.COMPLETED.value: 4,
}

stat_cards = [
    {"label": "All Tasks", "value": "", "icon": "hourglass_empty", "color": "violet"},
    {
        "label": "IN PROGRESS",
        "value": TaskStatusEnum.IN_PROGRESS.value,
        "icon": "schedule",
        "color": "blue",
    },
    {
        "label": "COMPLETED",
        "value": TaskStatusEnum.COMPLETED.value,
        "icon": "check_circle",
        "color": "green",
    },
    {
        "label": "IN REVIEW",
        "value": TaskStatusEnum.REVIEW.value,
        "icon": "hourglass_empty",
        "color": "gray",
    },
    {
        "label": "FAILED",
        "value": TaskStatusEnum.FAILED.value,
        "icon": "error",
        "color": "red",
    },
]

# Job Type Payload Field Definitions
JOB_PAYLOAD_FIELDS = {
    JobEnum.YouTubeChannel.value: [
        {"name": "ref_id", "label": "Reference ID", "type": "text", "required": True},
        {
            "name": "poll_frequency_in_days",
            "label": "Poll Frequency (Days)",
            "type": "number",
            "required": False,
            "default": 7,
        },
    ],
    JobEnum.YouTubeVideo.value: [
        {"name": "ref_id", "label": "Reference ID", "type": "text", "required": True},
        {
            "name": "poll_frequency_in_days",
            "label": "Poll Frequency (Days)",
            "type": "number",
            "required": False,
            "default": 7,
        },
    ],
    JobEnum.YouTubeThumbnailUpdater.value: [
        {"name": "ref_id", "label": "Reference ID", "type": "text", "required": True},
        {
            "name": "poll_frequency_in_days",
            "label": "Poll Frequency (Days)",
            "type": "number",
            "required": False,
            "default": 7,
        },
    ],
    JobEnum.YouTubeVideoSummarizer.value: [
        {"name": "ref_id", "label": "Reference ID", "type": "text", "required": True},
        {
            "name": "is_agent",
            "label": "Is Agent",
            "type": "checkbox",
            "required": False,
            "default": True,
        },
    ],
    JobEnum.YouTubeVideoMetadataSuggester.value: [
        {"name": "ref_id", "label": "Reference ID", "type": "text", "required": True},
    ],
    JobEnum.YouTubeVideoMetadataUpdater.value: [
        {"name": "ref_id", "label": "Reference ID", "type": "text", "required": True},
    ],
    JobEnum.YouTubeVideoThumbnailPromptSuggester.value: [
        {"name": "ref_id", "label": "Reference ID", "type": "text", "required": True},
        {
            "name": "is_agent",
            "label": "Is Agent",
            "type": "checkbox",
            "required": False,
            "default": True,
        },
    ],
    JobEnum.ImagePrompt.value: [
        {
            "name": "description",
            "label": "Description",
            "type": "text",
            "required": True,
        },
        {"name": "ref_id", "label": "Reference ID", "type": "text", "required": True},
        {
            "name": "image_type",
            "label": "Image Type",
            "type": "select",
            "required": True,
            "options": [it.value for it in ImageTypeEnum],
            "default": ImageTypeEnum.YouTube.value,
        },
    ],
    JobEnum.ImageGenerator.value: [
        {"name": "prompt", "label": "Prompt", "type": "textarea", "required": True},
        {
            "name": "name",
            "label": "Image Name",
            "type": "text",
            "required": True,
        },
        {
            "name": "image_type",
            "label": "Image Type",
            "type": "select",
            "required": True,
            "options": [it.value for it in ImageTypeEnum],
            "default": ImageTypeEnum.YouTube.value,
        },
        {"name": "ref_id", "label": "Reference ID", "type": "text", "required": True},
    ],
    JobEnum.PromptSuggester.value: [
        {
            "name": "description",
            "label": "Description",
            "type": "text",
            "required": True,
        },
    ],
    JobEnum.TwitterPost.value: [
        {
            "name": "content",
            "label": "Tweet Content",
            "type": "textarea",
            "required": True,
        },
    ],
    JobEnum.OWNER.value: [],
    JobEnum.TrendingIdeaSuggester.value: [],
}


def get_status_color(status_value: str) -> str:
    if status_value == TaskStatusEnum.IN_PROGRESS.value:
        return "primary"
    if status_value == TaskStatusEnum.FAILED.value:
        return "negative"
    if status_value == TaskStatusEnum.COMPLETED.value:
        return "positive"
    return "grey"


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


def sort_tasks_by_priority(tasks: list[TaskData]) -> list[TaskData]:
    return sorted(
        tasks,
        key=lambda task: (
            TASK_STATUS_PRIORITY.get(task.status.value, 99),
            task.created_at,
        ),
        reverse=False,
    )


def make_tasks_navigation_handler(status: str):
    def _handler() -> None:
        target = f"/tasks?status={status}" if status else "/tasks"
        ui.run_javascript(f'window.location.href = "{target}"')

    return _handler


def update_task_status(event, current_task):
    old_status = current_task.status
    try:
        current_task.status = TaskStatusEnum(event.value)
        TaskDB().update_task(current_task)
        event.sender.props(f'color="{get_status_color(event.value)}"')
        event.sender.update()
        ui.notify(f"Updated task status to {event.value}", type="positive")
    except (ValueError, AppException):
        current_task.status = old_status
        event.sender.value = old_status.value
        event.sender.props(f'color="{get_status_color(old_status.value)}"')
        event.sender.update()
        ui.notify("Failed to update task status", type="negative")


def build_payload_from_fields(
    job_type: str, field_values: dict[str, Any]
) -> dict[str, Any]:
    """Build payload dictionary from form field values."""
    payload: dict[str, Any] = {}
    fields = JOB_PAYLOAD_FIELDS.get(job_type, [])

    for field in fields:
        field_name: str = str(field.get("name", ""))
        field_type: str = str(field.get("type", ""))
        if field_name in field_values:
            value = field_values[field_name]
            # Handle type conversions
            if field_type == "number" and value:
                payload[field_name] = int(value) if value else field.get("default")
            elif field_type == "checkbox":
                payload[field_name] = bool(value)
            elif value is not None and value != "":
                payload[field_name] = value

    return payload


def render_payload_fields(job_type_select: Any, fields_container: Any) -> None:
    """Dynamically render payload input fields based on selected job type."""
    fields_container.clear()
    job_type: Any = job_type_select.value
    fields: list[dict[str, Any]] = JOB_PAYLOAD_FIELDS.get(job_type, [])

    # Initialize field inputs dictionary if not present
    if not hasattr(fields_container, "_field_inputs"):
        fields_container._field_inputs = {}
    else:
        fields_container._field_inputs.clear()

    with fields_container:
        if not fields:
            ui.label("No additional fields required for this job type").classes(
                "text-gray-500 italic"
            )
            return

        for field in fields:
            field_name: str = str(field.get("name", ""))
            field_type: str = str(field.get("type", ""))
            label: str = str(field.get("label", ""))

            input_field: Any = None

            if field_type == "text":
                input_field = (
                    ui.input(label=label).props("outlined dense").classes("w-full")
                )

            elif field_type == "number":
                input_field = (
                    ui.number(
                        label=label,
                        value=field.get("default", 0),
                        min=1,
                    )
                    .props("outlined dense")
                    .classes("w-full")
                )

            elif field_type == "textarea":
                input_field = (
                    ui.textarea(label=label)
                    .props("outlined autogrow")
                    .classes("w-full")
                )

            elif field_type == "checkbox":
                input_field = ui.checkbox(
                    label,
                    value=field.get("default", False),
                )

            elif field_type == "select":
                input_field = (
                    ui.select(
                        options=field.get("options", []),
                        value=field.get("default"),
                        label=label,
                    )
                    .props("outlined dense")
                    .classes("w-full")
                )

            if input_field is not None:
                fields_container._field_inputs[field_name] = input_field


def render_task_detail_rows(task_json: dict, detail_section) -> None:
    with detail_section:
        for key, value in task_json.items():
            if key == "payload" and value is not None:
                with ui.row().classes("w-full gap-4 items-start"):
                    ui.label("**payload:**").classes(
                        "w-1/5 font-bold text-blue-600 text-sm"
                    )
                    ui.json_editor({"content": {"json": value}}).classes("w-4/5")
                continue

            if (
                key not in DETAIL_EXCLUDED_KEYS
                and value is not None
                and not isinstance(value, list)
            ):
                display_val = (
                    str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                )
                with ui.row().classes("w-full gap-4 items-start"):
                    ui.label(f"**{key}:**").classes(
                        "w-1/5 font-bold text-blue-600 text-sm"
                    )
                    ui.label(display_val).classes("w-4/5 text-wrap text-sm")


def add_task(
    selected_job_type: str,
    selected_created_by: str,
    selected_status: str,
    fields_container,
) -> None:
    try:
        # Build payload from dynamic fields
        field_values = {}
        if (
            hasattr(fields_container, "_field_inputs")
            and fields_container._field_inputs
        ):
            for field_name, field_input in fields_container._field_inputs.items():
                try:
                    field_values[field_name] = field_input.value
                except AttributeError:
                    # Skip fields that don't have a value attribute
                    pass

        payload = build_payload_from_fields(selected_job_type, field_values)

        # Validate required fields
        fields = JOB_PAYLOAD_FIELDS.get(selected_job_type, [])
        for field in fields:
            if field.get("required") and field["name"] not in payload:
                ui.notify(
                    f"Required field '{field['label']}' is missing",
                    type="negative",
                )
                return

        status = TaskStatusEnum(selected_status)
        task = TaskData(
            id=uuid4(),
            job_type=JobEnum(selected_job_type),
            payload=payload,
            created_by=JobEnum(selected_created_by),
            created_at=datetime.now(),
            status=status,
            completed_at=datetime.now() if status == TaskStatusEnum.COMPLETED else None,
            trail=[],
        )
        TaskDB().add_task(task)
        ui.notify("Task created", type="positive")
        ui.run_javascript(
            "window.location.href = window.location.pathname + window.location.search"
        )
    except Exception as e:
        import traceback

        error_msg = traceback.format_exc()
        print(f"Error creating task: {error_msg}")
        ui.notify(f"Failed to create task: {str(e)}", type="negative")


def run_task_now(task_id: str) -> None:
    try:
        ui.notify(f"Running task: {task_id}", type="info")
        TaskSchedulerServices().start(task_id=task_id)
        ui.notify("Task run completed", type="positive")
        ui.run_javascript(
            "window.location.href = window.location.pathname + window.location.search"
        )
    except Exception:
        ui.notify("Failed to run task", type="negative")


def show_run_task_confirmation(task_id: str) -> None:
    """Show confirmation dialog before running a task."""
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Confirm Task Execution").classes("text-h6 mb-4")
        ui.label("Are you sure you want to run this task?").classes("mb-4")

        def on_confirm() -> None:
            dialog.close()
            run_task_now(task_id)

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


def render_add_task_form() -> None:
    job_options = [job.value for job in JobEnum]
    team_options = [team.role for team in TeamEnum]
    status_options = [status.value for status in TaskStatusEnum]

    with ui.expansion("Add New Task", icon="add_circle").classes("w-full my-3"):
        with ui.card().classes("w-full dark:bg-slate-800"):
            with ui.row().classes("w-full gap-3 items-end"):
                job_type_input = (
                    ui.select(
                        options=job_options,
                        value=JobEnum.OWNER.value,
                        label="Job Type",
                    )
                    .props("outlined dense")
                    .classes("w-1/4")
                )
                created_by_input = (
                    ui.select(
                        options=team_options,
                        value=TeamEnum.OWNER.role,
                        label="Created By",
                    )
                    .props("outlined dense")
                    .classes("w-1/4")
                )
                status_input = (
                    ui.select(
                        options=status_options,
                        value=TaskStatusEnum.NEW.value,
                        label="Status",
                    )
                    .props("outlined dense")
                    .classes("w-1/4")
                )

            # Container for dynamic payload fields with field storage
            fields_container: Any = ui.column().classes("w-full mt-3")
            fields_container._field_inputs = {}

            # Initial rendering of payload fields
            render_payload_fields(job_type_input, fields_container)

            # Update fields when job type changes
            def on_job_type_change() -> None:
                render_payload_fields(job_type_input, fields_container)

            job_type_input.on_value_change(on_job_type_change)
            with ui.row().classes("w-full justify-end mt-3"):
                ui.button(
                    "Create Task",
                    icon="add",
                    on_click=lambda: add_task(
                        str(job_type_input.value),
                        str(created_by_input.value),
                        str(status_input.value),
                        fields_container,
                    ),
                ).props("color=primary")


def tasks_page(status: str = ""):
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

        ui.separator()

        with ui.row().classes("w-full gap-4 my-4 flex-wrap"):
            for stat in stat_cards:
                with (
                    ui.card()
                    .classes(
                        f"flex-1 min-w-[180px] shadow-sm hover:shadow-md transition-shadow border-t-4 border-{stat['color']}-500"
                    )
                    .on("click", make_tasks_navigation_handler(stat["value"]))
                ):
                    with ui.avatar(color=stat["color"], text_color="white", size="sm"):
                        ui.icon(stat["icon"], size="sm")
                    with ui.column().classes("gap-0"):
                        ui.label(stat["label"]).classes("text-subtitle2 text-gray-600")

            if status:
                ui.label(f"Active filter: {status}").classes(
                    "text-caption text-gray-600"
                )

        render_add_task_form()

        # Show loading spinner while fetching data
        with ui.row().classes("w-full items-center my-4") as loading_row:
            ui.spinner(size="lg", color="primary")
            ui.label("Loading tasks...")

        # Fetch tasks
        tasks = TaskDB().get_tasks()
        if status:
            tasks = [
                task
                for task in tasks
                if str(getattr(task.status, "value", task.status)) == status
            ]
        tasks = sort_tasks_by_priority(tasks)

        # Remove loading spinner and row
        loading_row.delete()

        if tasks:
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
                    ui.label("Job Type").classes("w-1/8")
                    ui.label("Status").classes("w-1/8")
                    ui.label("Created By").classes("w-1/8")
                    ui.label("Created At").classes("w-1/8")
                    ui.label("Completed At").classes("w-1/8")
                    ui.label("Actions").classes("w-1/6 text-center shrink-0")

                # Table rows
                for task in tasks:
                    task_json = task.to_json()
                    task_id = task_json.get("id", "")
                    task_type = task_json.get("job_type", "")
                    status = task_json.get("status", "")
                    created_by = task_json.get("created_by", "")
                    created_at = task_json.get("created_at", "")[:19]
                    completed_at = (task_json.get("completed_at") or "")[:19]
                    row_status_class = get_status_row_class(status)

                    # Row container
                    with ui.column().classes(
                        "w-full gap-0 border-b border-gray-200 dark:border-slate-700"
                    ):
                        # Row header
                        with ui.row().classes(
                            f"w-full p-3 items-center flex-nowrap {row_status_class}"
                        ):
                            ui.label(task_id).classes("w-1/5 text-sm")
                            ui.label(task_type[:20]).classes("w-1/8 text-sm")
                            ui.label(status).classes("w-1/8 text-sm")
                            ui.label(created_by).classes("w-1/8 text-sm")
                            ui.label(created_at).classes("w-1/8 text-sm font-medium")
                            ui.label(completed_at).classes("w-1/8 text-sm font-medium")

                            # Action cell
                            with ui.row().classes(
                                "w-1/6 justify-center items-center gap-1 shrink-0"
                            ):
                                ui.button(
                                    icon="play_arrow",
                                    on_click=lambda current_task_id=task_id: show_run_task_confirmation(
                                        current_task_id
                                    ),
                                ).props(
                                    'flat dense onclick="event.stopPropagation()" onmousedown="event.stopPropagation()"'
                                )
                                ui.button(
                                    icon="open_in_new",
                                    on_click=lambda current_task_id=task_id: ui.run_javascript(
                                        f'window.location.href = "/task/{current_task_id}"'
                                    ),
                                ).props(
                                    'flat dense onclick="event.stopPropagation()" onmousedown="event.stopPropagation()"'
                                )
        else:
            with ui.card().classes("w-full bg-gray-100 dark:bg-slate-800"):
                ui.icon("inbox", size="xl").classes("text-gray-400")
                ui.label("No tasks found").classes("text-h6 text-gray-500")

        ui.separator().classes("my-4")


def task_detail_page(task_id: str) -> None:
    task = TaskDB().get_task_by_id(task_id)

    with ui.card().classes("w-full page-transition"):
        with ui.row().classes("items-center justify-between w-full mb-4"):
            ui.label("Task Details").classes("text-h4")
            with ui.row().classes("gap-2"):
                ui.button(
                    "Run Task",
                    icon="play_arrow",
                    on_click=lambda current_task_id=task_id: show_run_task_confirmation(
                        current_task_id
                    ),
                ).props("flat")
                ui.button(
                    "Back to Tasks",
                    icon="arrow_back",
                    on_click=lambda: ui.run_javascript(
                        'window.location.href = "/tasks"'
                    ),
                ).props("flat")
                ui.button(
                    icon="home",
                    on_click=lambda: ui.run_javascript('window.location.href = "/"'),
                ).props("flat")

        ui.separator()

        if not task:
            with ui.card().classes("w-full bg-red-50 dark:bg-red-900/20"):
                ui.label(f"Task not found for id: {task_id}").classes(
                    "text-negative text-subtitle1"
                )
            return

        status_options = [status.value for status in TaskStatusEnum]
        with ui.row().classes("w-full items-end gap-3 mb-4"):
            ui.label(f"Task ID: {task.id}").classes("text-subtitle1 font-medium")
            (
                ui.select(
                    label="Status",
                    options=status_options,
                    value=task.status.value,
                    on_change=lambda e, current_task=task: update_task_status(
                        e, current_task
                    ),
                )
                .props(
                    f'dense outlined options-dense color="{get_status_color(task.status.value)}"'
                )
                .classes("w-56")
            )

        task_json = task.to_json()
        detail_section = ui.column().classes(
            "w-full bg-blue-50 dark:bg-slate-800 p-4 gap-3"
        )
        render_task_detail_rows(task_json, detail_section)
