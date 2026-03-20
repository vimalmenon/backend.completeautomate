import base64
from datetime import datetime

from nicegui import run, ui

from backend.data import (
    JobData,
    PlatformDBData,
    PlatformYouTubeVideoDBData,
    YouTubeVideoDBData,
)
from backend.enum import (
    JobsStatusEnum,
    JobStatusEnum,
    JobTypeEnum,
    PlatformEnum,
    YouTubeVideoTaskEnum,
)
from backend.integration.storage.s3_storage import S3Storage
from backend.manager import JobManager, YouTubeVideoManager
from backend.ui.common.component_common import (
    render_common_header,
    render_separator,
)

FLOW_STEPS: list[tuple[YouTubeVideoTaskEnum, str]] = [
    (YouTubeVideoTaskEnum.YouTubeVideoStart, "Start"),
    (YouTubeVideoTaskEnum.YouTubeVideoFixTranscript, "Fix Transcript"),
    (YouTubeVideoTaskEnum.YouTubeVideoMetadataSelection, "Metadata Selection"),
    (YouTubeVideoTaskEnum.YouTubeVideoThumbnailSelection, "Thumbnail Selection"),
    (YouTubeVideoTaskEnum.YouTubeVideoComplete, "Complete"),
]

FLOW_STEP_JOB_TYPES: dict[str, str] = {
    "Start": "YouTubeVideo",
    "Fix Transcript": "YouTubeVideoSummarizer",
    "Metadata Selection": "YouTubeVideoMetadataUpdater",
    "Thumbnail Selection": "YouTubeVideoThumbnailPromptSuggester",
    "Complete": "YouTubeThumbnailUpdater",
}

JOB_STATUS_TO_TASK_STATUS: dict[JobsStatusEnum, TaskStatusEnum] = {
    JobsStatusEnum.NEW: TaskStatusEnum.NEW,
    JobsStatusEnum.IN_PROGRESS: TaskStatusEnum.IN_PROGRESS,
    JobsStatusEnum.COMPLETE: TaskStatusEnum.COMPLETED,
    JobsStatusEnum.PENDING: TaskStatusEnum.PENDING,
    JobsStatusEnum.REVIEW: TaskStatusEnum.REVIEW,
    JobsStatusEnum.FAILED: TaskStatusEnum.FAILED,
    JobsStatusEnum.ARCHIVED: TaskStatusEnum.CLEAN_UP,
}

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


def _resolve_flow_root_job_id(task: TaskData) -> str:
    if task.trail:
        return str(task.trail[0])
    return str(task.id)


def _job_type_value(task: TaskData) -> str:
    return task.job_type.value


def _filter_tasks_by_flow_job_id(
    tasks: list[TaskData], flow_job_id: str | None = None
) -> list[TaskData]:
    if not tasks:
        return []

    sorted_tasks = sorted(tasks, key=lambda task: task.created_at)
    flow_job_types = set(FLOW_STEP_JOB_TYPES.values())
    flow_candidates = [
        task for task in sorted_tasks if _job_type_value(task) in flow_job_types
    ]

    if not flow_candidates:
        return sorted_tasks

    selected_root_job_id: str
    if flow_job_id:
        selected_root_job_id = flow_job_id
        matched_task = next(
            (task for task in reversed(sorted_tasks) if str(task.id) == flow_job_id),
            None,
        )
        if matched_task:
            selected_root_job_id = _resolve_flow_root_job_id(matched_task)
    else:
        selected_root_job_id = _resolve_flow_root_job_id(flow_candidates[-1])

    filtered_tasks = [
        task
        for task in sorted_tasks
        if _resolve_flow_root_job_id(task) == selected_root_job_id
    ]

    if flow_job_id and not filtered_tasks:
        return _filter_tasks_by_flow_job_id(tasks=tasks, flow_job_id=None)

    return filtered_tasks


def _get_video_job(ref_id: str, flow_job_id: str | None = None) -> JobData | None:
    jobs = [
        job
        for job in JobManager().get_job_by_type(type=JobTypeEnum.YouTubeVideo)
        if job.task_data.get("ref_id") == ref_id
    ]
    if not jobs:
        return None

    if flow_job_id:
        matched_job = next((job for job in jobs if str(job.id) == flow_job_id), None)
        if matched_job:
            return matched_job

    return sorted(jobs, key=lambda job: job.created_at)[-1]


def _build_task_by_job(tasks: list[TaskData]) -> dict[str, TaskData]:
    task_by_job: dict[str, TaskData] = {}
    for task in tasks:
        task_by_job[_job_type_value(task)] = task
    return task_by_job


def _get_flow_status_by_step_label(
    video_job: JobData | None,
) -> dict[str, TaskStatusEnum]:
    if not video_job:
        return {}

    if video_job.status == JobsStatusEnum.COMPLETE:
        return {step_label: TaskStatusEnum.COMPLETED for _, step_label in FLOW_STEPS}

    current_task_value = video_job.task_data.get("task")
    if not current_task_value:
        return {}

    current_flow_step = YouTubeVideoTaskEnum(current_task_value)
    current_step_label = next(
        (
            step_label
            for flow_step, step_label in FLOW_STEPS
            if flow_step == current_flow_step
        ),
        None,
    )
    if not current_step_label:
        return {}

    current_step_index = next(
        index
        for index, (_, step_label) in enumerate(FLOW_STEPS)
        if step_label == current_step_label
    )
    current_status = JOB_STATUS_TO_TASK_STATUS.get(
        video_job.status, TaskStatusEnum.PENDING
    )

    flow_statuses: dict[str, TaskStatusEnum] = {}
    for index, (_, step_label) in enumerate(FLOW_STEPS):
        if index < current_step_index:
            flow_statuses[step_label] = TaskStatusEnum.COMPLETED
            continue
        if index > current_step_index:
            flow_statuses[step_label] = TaskStatusEnum.PENDING
            continue
        flow_statuses[step_label] = current_status
    return flow_statuses


def _get_visible_flow_steps(
    task_by_job: dict[str, TaskData],
    flow_status_by_step_label: dict[str, TaskStatusEnum],
) -> list[tuple[YouTubeVideoTaskEnum, str, str]]:
    visible_flow_steps: list[tuple[YouTubeVideoTaskEnum, str, str]] = []
    for flow_step, step_label in FLOW_STEPS:
        job_type_key = FLOW_STEP_JOB_TYPES[step_label]
        visible_flow_steps.append((flow_step, job_type_key, step_label))
    return visible_flow_steps


def _attach_task_card_handlers(
    *,
    flow_step: YouTubeVideoTaskEnum,
    job_type: str,
    current_task: TaskData | None,
    current_status: TaskStatusEnum | None,
    step_label: str,
    video_job: JobData | None,
    task_card,
) -> None:
    editable_job_types = {
        "YouTubeVideoSummarizer",
        "YouTubeVideoMetadataSuggester",
        "YouTubeVideoMetadataUpdater",
        "YouTubeVideoThumbnailPromptSuggester",
    }
    if job_type not in editable_job_types:
        return

    if current_task:
        task_card.on(
            "dblclick",
            lambda _, task=current_task: _show_task_status_dialog(task),
        )
        return

    if video_job and current_status is not None:
        task_card.on(
            "dblclick",
            lambda _, job=video_job, step=flow_step, label=step_label: _show_flow_job_status_dialog(
                video_job=job,
                flow_step=step,
                step_label=label,
            ),
        )
        return

    task_card.on(
        "dblclick",
        lambda _, current_step=step_label: ui.notify(
            f"{current_step} task is not available yet",
            type="warning",
        ),
    )


def _show_task_status_dialog(task: TaskData) -> None:
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Edit Task Status").classes("text-h6 mb-2")
        ui.label(f"Task ID: {task.id}").classes("text-caption text-gray-600 mb-2")

        status_options = [status.value for status in TaskStatusEnum]
        status_input = (
            ui.select(
                options=status_options,
                value=task.status.value,
                label="Status",
            )
            .props("outlined dense")
            .classes("w-full")
        )

        def on_save() -> None:
            old_status = task.status
            old_completed_at = task.completed_at
            try:
                task.status = TaskStatusEnum(str(status_input.value))
                task.completed_at = (
                    datetime.now() if task.status == TaskStatusEnum.COMPLETED else None
                )
                JobManager().update_task(task)
                ui.notify("Task status updated", type="positive")
                dialog.close()
                ui.run_javascript(
                    "window.location.href = window.location.pathname + window.location.search"
                )
            except Exception:
                task.status = old_status
                task.completed_at = old_completed_at
                ui.notify("Failed to update task status", type="negative")

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Save", icon="save", on_click=on_save).props("color=primary")

    dialog.open()


def _show_flow_job_status_dialog(
    video_job: JobData,
    flow_step: YouTubeVideoTaskEnum,
    step_label: str,
) -> None:
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label(f"Edit {step_label} Status").classes("text-h6 mb-2")
        ui.label(f"Job ID: {video_job.id}").classes("text-caption text-gray-600 mb-2")

        status_options = [status.value for status in JobsStatusEnum]
        status_input = (
            ui.select(
                options=status_options,
                value=video_job.status.value,
                label="Job Status",
            )
            .props("outlined dense")
            .classes("w-full")
        )

        def on_save() -> None:
            old_status = video_job.status
            old_task_data = dict(video_job.task_data)
            try:
                new_status = JobsStatusEnum(str(status_input.value))
                updated_task_data = {**video_job.task_data, "task": flow_step.value}
                JobManager().update_job_data(
                    job_id=video_job.id,
                    status=new_status,
                    failed_count=video_job.failed_count,
                    task_data=updated_task_data,
                )
                video_job.status = new_status
                video_job.task_data = updated_task_data
                ui.notify(f"{step_label} status updated", type="positive")
                dialog.close()
                ui.run_javascript(
                    "window.location.href = window.location.pathname + window.location.search"
                )
            except Exception:
                video_job.status = old_status
                video_job.task_data = old_task_data
                ui.notify(f"Failed to update {step_label} status", type="negative")

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Save", icon="save", on_click=on_save).props("color=primary")

    dialog.open()


def render_task_progress(
    tasks: list[TaskData],
    video_job: JobData | None,
    flow_job_id: str | None = None,
) -> None:
    flow_tasks = _filter_tasks_by_flow_job_id(tasks=tasks, flow_job_id=flow_job_id)
    task_by_job = _build_task_by_job(flow_tasks)
    flow_status_by_step_label = _get_flow_status_by_step_label(video_job)
    visible_flow_steps = _get_visible_flow_steps(task_by_job, flow_status_by_step_label)

    with ui.card().classes(
        "w-full p-4 shadow-sm border border-gray-200 dark:border-slate-700"
    ):
        ui.label("Task Flow").classes("text-sm font-bold mb-2")
        with ui.row().classes("w-full items-stretch gap-1 flex-wrap"):
            for index, (flow_step, job_type, step_label) in enumerate(
                visible_flow_steps
            ):
                current_task = task_by_job.get(job_type)
                status = (
                    current_task.status
                    if current_task
                    else flow_status_by_step_label.get(step_label)
                )
                style = (
                    STATUS_STYLE[status]
                    if status and status in STATUS_STYLE
                    else STATUS_STYLE[TaskStatusEnum.PENDING]
                )

                with ui.card().classes(
                    "min-w-[110px] flex-1 shadow-none border border-gray-200 dark:border-slate-700"
                ) as task_card:
                    with ui.column().classes("px-2 py-1 gap-0"):
                        ui.label(step_label).classes("text-xs font-semibold")
                        with ui.row().classes("items-center gap-1"):
                            ui.icon(style["icon"]).classes(
                                f"text-{style['color']}-600 text-sm"
                            )
                            ui.badge(style["label"], color=style["color"]).classes(
                                "text-[10px] px-1 py-0"
                            ).props("outline")

                _attach_task_card_handlers(
                    flow_step=flow_step,
                    job_type=job_type,
                    current_task=current_task,
                    current_status=status,
                    step_label=step_label,
                    video_job=video_job,
                    task_card=task_card,
                )

                if index < len(visible_flow_steps) - 1:
                    with ui.column().classes("justify-center hidden lg:flex"):
                        ui.icon("chevron_right").classes("text-gray-400 text-xs")


def _should_show_metadata_suggestions(video_job: JobData | None) -> bool:
    if not video_job:
        return False
    return (
        video_job.status == JobsStatusEnum.REVIEW
        and video_job.task_data.get("task")
        == YouTubeVideoTaskEnum.YouTubeVideoMetadataSelection.value
    )


def _should_show_thumbnail_prompt_suggestions(tasks: list[TaskData]) -> bool:
    latest_thumbnail_prompt_task: TaskData | None = None
    for task in sorted(tasks, key=lambda t: t.created_at):
        if _job_type_value(task) == "YouTubeVideoThumbnailPromptSuggester":
            latest_thumbnail_prompt_task = task

    return bool(
        latest_thumbnail_prompt_task
        and latest_thumbnail_prompt_task.status == TaskStatusEnum.REVIEW
    )


def _should_show_thumbnail_suggestions(video_job: JobData | None) -> bool:
    if not video_job:
        return False
    return (
        video_job.status == JobsStatusEnum.REVIEW
        and video_job.task_data.get("task")
        == YouTubeVideoTaskEnum.YouTubeVideoThumbnailSelection.value
    )


def _build_thumbnail_image_source(s3_data) -> str | None:
    try:
        image_bytes = S3Storage().get_bytes(s3_data)
        if not image_bytes:
            return None
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        return f"data:{s3_data.content_type.value};base64,{encoded_image}"
    except Exception:
        return None


def _select_thumbnail_option(ref_id: str, option_index: int) -> None:
    try:
        video_manager = YouTubeVideoManager(ref_id=ref_id)
        video = video_manager.get_video()
        if not video:
            ui.notify("Video not found", type="negative")
            return

        if option_index < 0 or option_index >= len(video.thumbnails_suggestions):
            ui.notify("Thumbnail option not found", type="warning")
            return

        for index, suggestion in enumerate(video.thumbnails_suggestions):
            suggestion.status = (
                JobStatusEnum.PROMOTE if index == option_index else JobStatusEnum.REVIEW
            )

        video_manager.update_thumbnails_suggestions(video.thumbnails_suggestions)
        ui.notify("Thumbnail selected", type="positive")
        ui.run_javascript(
            "window.location.href = window.location.pathname + window.location.search"
        )
    except Exception:
        ui.notify("Failed to select thumbnail", type="negative")


def _render_thumbnail_suggestions(video: YouTubeVideoDBData) -> None:
    suggestions = video.thumbnails_suggestions
    if not suggestions:
        return

    with ui.card().classes(
        "w-full p-4 shadow-sm border border-emerald-200 dark:border-emerald-700 "
        "bg-emerald-50 dark:bg-emerald-900/20"
    ):
        ui.label("Thumbnail Suggestions").classes("text-h6 font-bold mb-2")
        ui.label("Select one thumbnail to promote").classes(
            "text-sm text-emerald-700 mb-2"
        )

        with ui.row().classes("w-full gap-3 flex-wrap"):
            for index, detail in enumerate(suggestions):
                is_selected = detail.status == JobStatusEnum.PROMOTE
                image_source = _build_thumbnail_image_source(detail.s3_data)

                with ui.card().classes(
                    "w-[260px] max-w-full p-3 bg-white dark:bg-slate-800 "
                    "shadow-none border border-emerald-100 dark:border-emerald-800"
                ):
                    ui.label(f"Option {index + 1}").classes(
                        "text-sm font-semibold text-emerald-700"
                    )

                    if image_source:
                        ui.image(image_source).classes(
                            "w-full h-[146px] object-cover rounded-md mt-2"
                        )
                    else:
                        with ui.row().classes(
                            "w-full h-[146px] mt-2 rounded-md border border-dashed border-gray-300 "
                            "items-center justify-center"
                        ):
                            ui.label("Image preview unavailable").classes(
                                "text-xs text-gray-500"
                            )

                    with ui.row().classes("w-full items-center justify-between mt-3"):
                        badge_color = "green" if is_selected else "grey"
                        badge_label = "Selected" if is_selected else detail.status.value
                        ui.badge(badge_label, color=badge_color).props("outline")
                        ui.button(
                            "Select",
                            icon="check",
                            on_click=lambda current_ref=video.ref_id, current_index=index: _select_thumbnail_option(
                                ref_id=current_ref,
                                option_index=current_index,
                            ),
                        ).props(
                            "color=primary"
                            if not is_selected
                            else "color=primary outline"
                        )


def _update_thumbnail_prompt_option_status(
    ref_id: str,
    option_index: int,
    status_value: str,
) -> None:
    try:
        video_manager = YouTubeVideoManager(ref_id=ref_id)
        video = video_manager.get_video()
        if not video:
            ui.notify("Video not found", type="negative")
            return

        if option_index < 0 or option_index >= len(video.thumbnail_prompt_suggestions):
            ui.notify("Thumbnail prompt option not found", type="warning")
            return

        video.thumbnail_prompt_suggestions[option_index].status = JobStatusEnum(
            status_value
        )
        video_manager.update_thumbnail_prompt_suggestions(
            video.thumbnail_prompt_suggestions
        )
        ui.notify("Option status updated", type="positive")
        ui.run_javascript(
            "window.location.href = window.location.pathname + window.location.search"
        )
    except Exception:
        ui.notify("Failed to update option status", type="negative")


def _render_thumbnail_prompt_suggestions(video: YouTubeVideoDBData) -> None:
    suggestions = video.thumbnail_prompt_suggestions
    if not suggestions:
        return

    status_styles: dict[JobStatusEnum, tuple[str, str]] = {
        JobStatusEnum.NEW: ("fiber_new", "grey"),
        JobStatusEnum.IN_PROGRESS: ("schedule", "blue"),
        JobStatusEnum.REVIEW: ("rate_review", "orange"),
        JobStatusEnum.APPROVED: ("verified", "teal"),
        JobStatusEnum.PROMOTE: ("north_east", "green"),
        JobStatusEnum.FAILED: ("error", "red"),
        JobStatusEnum.CLEAN_UP: ("cleaning_services", "brown"),
    }

    with ui.card().classes(
        "w-full p-4 shadow-sm border border-indigo-200 dark:border-indigo-700 "
        "bg-indigo-50 dark:bg-indigo-900/20"
    ):
        ui.label("Thumbnail Prompt Suggestions").classes("text-h6 font-bold mb-2")

        for index, detail in enumerate(suggestions, start=1):
            icon_name, color = status_styles.get(detail.status, ("info", "grey"))
            with ui.card().classes(
                "w-full bg-white dark:bg-slate-800 mt-2 shadow-none border border-indigo-100 dark:border-indigo-800"
            ):
                with ui.row().classes("w-full justify-between items-center gap-2 mb-2"):
                    ui.label(f"Option {index}: {detail.name}").classes(
                        "text-sm font-semibold text-indigo-700"
                    )
                    with ui.row().classes("items-center gap-2 flex-wrap justify-end"):
                        status_input = (
                            ui.select(
                                options=[status.value for status in JobStatusEnum],
                                value=detail.status.value,
                                label="Status",
                            )
                            .props("outlined dense")
                            .classes("min-w-40")
                        )
                        ui.button(
                            "Update Status",
                            icon="save",
                            on_click=lambda current_ref=video.ref_id, current_index=index - 1, current_status=status_input: _update_thumbnail_prompt_option_status(
                                ref_id=current_ref,
                                option_index=current_index,
                                status_value=str(current_status.value),
                            ),
                        ).props("color=primary")
                        ui.icon(icon_name).classes(f"text-{color}-600 text-sm")
                        ui.badge(detail.status.value, color=color).props("outline")

                with ui.column().classes("w-full gap-2"):
                    with ui.row().classes("w-full gap-4 items-start"):
                        ui.label("Description:").classes("w-1/5 font-bold text-sm")
                        ui.label(detail.description or "-").classes(
                            "w-4/5 text-wrap text-sm whitespace-pre-wrap"
                        )

                    with ui.row().classes("w-full gap-4 items-start"):
                        ui.label("Prompt:").classes("w-1/5 font-bold text-sm")
                        ui.label(detail.prompt or "-").classes(
                            "w-4/5 text-wrap text-sm whitespace-pre-wrap font-mono"
                        )

                    with ui.row().classes("w-full gap-4 items-start"):
                        ui.label("Negative Prompt:").classes("w-1/5 font-bold text-sm")
                        ui.label(detail.negative_prompt or "-").classes(
                            "w-4/5 text-wrap text-sm whitespace-pre-wrap font-mono"
                        )


def _update_metadata_option_status(
    ref_id: str,
    option_index: int,
    status_value: str,
) -> None:
    try:
        video_manager = YouTubeVideoManager(ref_id=ref_id)
        video = video_manager.get_video()
        if not video:
            ui.notify("Video not found", type="negative")
            return

        if option_index < 0 or option_index >= len(video.metadata_suggestions):
            ui.notify("Metadata option not found", type="warning")
            return

        video.metadata_suggestions[option_index].status = JobStatusEnum(status_value)
        video_manager.update_metadata_suggestions(video.metadata_suggestions)
        ui.notify("Option status updated", type="positive")
        ui.run_javascript(
            "window.location.href = window.location.pathname + window.location.search"
        )
    except Exception:
        ui.notify("Failed to update option status", type="negative")


def _render_metadata_suggestions(video: YouTubeVideoDBData) -> None:
    suggestions = video.metadata_suggestions
    if not suggestions:
        return

    status_styles: dict[JobStatusEnum, tuple[str, str]] = {
        JobStatusEnum.NEW: ("fiber_new", "grey"),
        JobStatusEnum.IN_PROGRESS: ("schedule", "blue"),
        JobStatusEnum.REVIEW: ("rate_review", "orange"),
        JobStatusEnum.APPROVED: ("verified", "teal"),
        JobStatusEnum.PROMOTE: ("north_east", "green"),
        JobStatusEnum.FAILED: ("error", "red"),
        JobStatusEnum.CLEAN_UP: ("cleaning_services", "brown"),
    }

    with ui.card().classes(
        "w-full p-4 shadow-sm border border-amber-200 dark:border-amber-700 "
        "bg-amber-50 dark:bg-amber-900/20"
    ):
        ui.label("Metadata Suggestions").classes("text-h6 font-bold mb-2")
        if video.comment:
            with ui.row().classes("w-full gap-4 items-start mb-3"):
                ui.label("Comment:").classes("font-bold text-amber-700 text-sm")
                ui.label(video.comment).classes("text-wrap text-sm")

        for index, detail in enumerate(suggestions, start=1):
            icon_name, color = status_styles.get(detail.status, ("info", "grey"))
            with ui.card().classes(
                "w-full bg-white dark:bg-slate-800 mt-2 shadow-none border border-amber-100 dark:border-amber-800"
            ):
                with ui.row().classes("w-full justify-between items-center gap-2 mb-2"):
                    ui.label(f"Option {index}").classes(
                        "text-sm font-semibold text-amber-700"
                    )
                    with ui.row().classes("items-center gap-2 flex-wrap justify-end"):
                        status_input = (
                            ui.select(
                                options=[status.value for status in JobStatusEnum],
                                value=detail.status.value,
                                label="Status",
                            )
                            .props("outlined dense")
                            .classes("min-w-40")
                        )
                        ui.button(
                            "Update Status",
                            icon="save",
                            on_click=lambda current_ref=video.ref_id, current_index=index - 1, current_status=status_input: _update_metadata_option_status(
                                ref_id=current_ref,
                                option_index=current_index,
                                status_value=str(current_status.value),
                            ),
                        ).props("color=primary")
                        ui.icon(icon_name).classes(f"text-{color}-600 text-sm")
                        ui.badge(detail.status.value, color=color).props("outline")

                with ui.column().classes("w-full gap-2"):
                    with ui.row().classes("w-full gap-4 items-start"):
                        ui.label("Title:").classes("w-1/5 font-bold text-sm")
                        ui.label(detail.title).classes("w-4/5 text-wrap text-sm")

                    with ui.row().classes("w-full gap-4 items-start"):
                        ui.label("Description:").classes("w-1/5 font-bold text-sm")
                        ui.label(detail.description or "-").classes(
                            "w-4/5 text-wrap text-sm whitespace-pre-wrap"
                        )

                    with ui.row().classes("w-full gap-4 items-start"):
                        ui.label("Tags:").classes("w-1/5 font-bold text-sm")
                        ui.label(
                            ", ".join(detail.tags) if detail.tags else "-"
                        ).classes("w-4/5 text-wrap text-sm")


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

        video, tasks, video_job = await run.io_bound(
            lambda: (
                YouTubeVideoManager(ref_id=platform.ref_id).get_video(),
                JobManager().get_job_by_ref_id(ref_id=platform.ref_id),
                _get_video_job(ref_id=platform.ref_id, flow_job_id=section),
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
                            ).update_transcript(new_text)
                        )
                        save_btn.props("loading=false disabled=false")
                        transcript_dialog.close()
                        ui.notify("Transcript saved", type="positive", position="top")

                    save_btn = ui.button(
                        "Save Changes", icon="save", on_click=save_transcript
                    ).props("color=primary")

    flow_tasks = _filter_tasks_by_flow_job_id(tasks=tasks, flow_job_id=section)
    show_metadata_suggestions = _should_show_metadata_suggestions(video_job)
    show_thumbnail_suggestions = _should_show_thumbnail_suggestions(video_job)
    show_thumbnail_prompt_suggestions = _should_show_thumbnail_prompt_suggestions(
        flow_tasks
    )

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
        render_task_progress(tasks=tasks, video_job=video_job, flow_job_id=section)
        _render_video_details(video)
        _render_transcript_section(video, platform.ref_id, video_id, transcript_dialog)
        if show_metadata_suggestions:
            _render_metadata_suggestions(video)
        if show_thumbnail_suggestions:
            _render_thumbnail_suggestions(video)
        if show_thumbnail_prompt_suggestions:
            _render_thumbnail_prompt_suggestions(video)
