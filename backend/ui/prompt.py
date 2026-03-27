from datetime import datetime

from nicegui import run, ui

from backend.data.prompt import PromptDBData
from backend.database import PromptDB
from backend.enum.ai import AIModelEnum
from backend.enum.prompt import PromptTaskEnum
from backend.enum.team import TeamEnum
from backend.exception.app_exception import AppException


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


def save_prompt_changes(
    prompt_data, prompt_value: str, system_message_value: str
) -> None:
    try:
        prompt_data.prompt = prompt_value
        prompt_data.system_message = system_message_value
        prompt_data.last_updated = datetime.now()
        PromptDB().save_prompt(prompt_data)
        ui.notify("Prompt updated", type="positive")
        ui.run_javascript(
            "window.location.href = window.location.pathname + window.location.search"
        )
    except AppException:
        ui.notify("Failed to update prompt", type="negative")


def open_edit_prompt_dialog(prompt_data) -> None:
    with (
        ui.dialog() as dialog,
        ui.card().classes("w-[900px] max-w-full dark:bg-slate-800"),
    ):
        ui.label("Edit Prompt").classes("text-h6")

        prompt_input = (
            ui.textarea(label="Prompt", value=prompt_data.prompt)
            .props("outlined autogrow")
            .classes("w-full")
        )
        system_message_input = (
            ui.textarea(label="System Message", value=prompt_data.system_message)
            .props("outlined autogrow")
            .classes("w-full")
        )

        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button(
                "Save",
                icon="save",
                on_click=lambda: save_prompt_changes(
                    prompt_data,
                    str(prompt_input.value),
                    str(system_message_input.value),
                ),
            ).props("color=primary")

    dialog.open()


def add_prompt(
    selected_task: str,
    selected_role: str,
    selected_ai: str,
    prompt_value: str,
    system_message_value: str,
) -> None:
    if not prompt_value.strip() or not system_message_value.strip():
        ui.notify("Prompt and system message are required", type="negative")
        return

    try:
        # Create a PromptVersionDBData for the initial version
        from uuid import uuid4

        from backend.data.prompt import PromptVersionDBData

        version_id = uuid4()
        version = PromptVersionDBData(
            prompt=prompt_value.strip(),
            system_message=system_message_value.strip(),
            version=version_id,
            ai=AIModelEnum(selected_ai),
        )
        prompt_data = PromptDBData(
            task=PromptTaskEnum(selected_task),
            role=TeamEnum.from_value(selected_role),
            description="",
            versions=[version],
            version=version_id,
            last_updated=datetime.now(),
        )
        PromptDB().save_prompt(prompt_data)
        ui.notify("Prompt created", type="positive")
        ui.run_javascript(
            "window.location.href = window.location.pathname + window.location.search"
        )
    except (ValueError, AppException):
        ui.notify("Failed to create prompt", type="negative")


def render_add_prompt_form() -> None:
    task_options = [task.value for task in PromptTaskEnum]
    role_options = [team.role for team in TeamEnum]
    ai_options = [ai.value for ai in AIModelEnum]

    with ui.expansion("Add New Prompt", icon="add_circle").classes("w-full my-3"):
        with ui.card().classes("w-full dark:bg-slate-800"):
            with ui.row().classes("w-full gap-3 items-end"):
                task_input = (
                    ui.select(
                        options=task_options,
                        value=task_options[0] if task_options else None,
                        label="Task",
                    )
                    .props("outlined dense")
                    .classes("w-1/3")
                )
                role_input = (
                    ui.select(
                        options=role_options,
                        value=TeamEnum.SOCIAL_MEDIA_MANAGER.role,
                        label="Role",
                    )
                    .props("outlined dense")
                    .classes("w-1/3")
                )
                ai_input = (
                    ui.select(
                        options=ai_options,
                        value=AIModelEnum.Grok.value,
                        label="AI",
                    )
                    .props("outlined dense")
                    .classes("w-1/3")
                )

            prompt_input = (
                ui.textarea(label="Prompt", value="")
                .props("outlined autogrow")
                .classes("w-full mt-3")
            )
            system_message_input = (
                ui.textarea(label="System Message", value="")
                .props("outlined autogrow")
                .classes("w-full mt-3")
            )

            with ui.row().classes("w-full justify-end mt-3"):
                ui.button(
                    "Create Prompt",
                    icon="add",
                    on_click=lambda: add_prompt(
                        str(task_input.value),
                        str(role_input.value),
                        str(ai_input.value),
                        str(prompt_input.value),
                        str(system_message_input.value),
                    ),
                ).props("color=primary")


async def prompt_page():
    with ui.card().classes("w-full page-transition"):
        with ui.row().classes("items-center justify-between w-full mb-4"):
            ui.label("Prompt Management").classes("text-h4")
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
            [("Home", "/"), ("Prompts", "/prompt")], right_text="AI prompt templates"
        )
        ui.separator()

        render_add_prompt_form()

        with ui.row().classes("w-full items-center my-4") as loading_row:
            ui.spinner(size="lg", color="primary")
            ui.label("Loading prompts...")

        try:
            prompts = await run.io_bound(PromptDB().get_all_prompts)
        except AppException:
            prompts = []
            ui.notify("Failed to load prompts", type="negative")

        loading_row.delete()

        if prompts:
            ui.label(f"Found {len(prompts)} prompt(s)").classes("text-subtitle1 mb-4")

            with ui.column().classes(
                "w-full gap-0 border border-gray-300 dark:border-slate-600 rounded"
            ):
                with ui.row().classes(
                    "w-full bg-gray-100 dark:bg-slate-800 border-b border-gray-300 dark:border-slate-600 p-3 font-bold flex-nowrap items-center"
                ):
                    ui.label("Task").classes("w-1/4")
                    ui.label("Role").classes("w-1/6")
                    ui.label("AI").classes("w-1/6")
                    ui.label("Updated").classes("w-1/3")
                    ui.label("Action").classes("w-1/6 text-center")

                for prompt in prompts:
                    task = prompt.task.value
                    role = prompt.role
                    ai = prompt.ai
                    last_updated = prompt.last_updated

                    with ui.row().classes(
                        "w-full p-3 hover:bg-blue-50 dark:hover:bg-blue-900/40 items-center flex-nowrap border-b border-gray-200 dark:border-slate-700 cursor-pointer gap-3"
                    ):
                        ui.label(task).classes("w-1/4 text-sm font-medium")
                        ui.label(role).classes("w-1/6 text-sm")
                        ui.label(ai).classes("w-1/6 text-sm")
                        ui.label(str(last_updated)).classes("w-1/3 text-sm")
                        with ui.row().classes(
                            "w-1/6 justify-center items-center gap-2"
                        ):
                            ui.button(
                                icon="open_in_new",
                                on_click=lambda task_val=task: ui.run_javascript(
                                    f'window.location.href = "/prompt/{task_val}"'
                                ),
                            ).props("flat dense color=primary").tooltip("View Details")
        else:
            with ui.card().classes("w-full bg-gray-100 dark:bg-slate-800"):
                ui.icon("article", size="xl").classes("text-gray-400")
                ui.label("No prompts found").classes("text-h6 text-gray-500")

        ui.separator().classes("my-4")


async def prompt_detail_page(task_id: str) -> None:
    try:
        prompt = await run.io_bound(
            PromptDB().get_prompt_by_task, PromptTaskEnum(task_id)
        )
    except (ValueError, AppException):
        prompt = None

    with ui.card().classes("w-full page-transition"):
        with ui.row().classes("items-center justify-between w-full mb-4"):
            ui.label("Prompt Details").classes("text-h4")
            with ui.row().classes("gap-2"):
                ui.button(
                    "Back to Prompts",
                    icon="arrow_back",
                    on_click=lambda: ui.run_javascript(
                        'window.location.href = "/prompt"'
                    ),
                ).props("flat")
                ui.button(
                    icon="home",
                    on_click=lambda: ui.run_javascript('window.location.href = "/"'),
                ).props("flat")

        prompt_status = "Template found" if prompt else "Not found"
        render_breadcrumbs(
            [("Home", "/"), ("Prompts", "/prompt"), (task_id, f"/prompt/{task_id}")],
            right_text=f"Status: {prompt_status}",
        )
        ui.separator()

        if not prompt:
            with ui.card().classes("w-full bg-red-50 dark:bg-red-900/20"):
                ui.label(f"Prompt not found for task: {task_id}").classes(
                    "text-negative text-subtitle1"
                )
            return

        prompt_json = prompt.to_json()

        with ui.card().classes("w-full dark:bg-slate-800"):
            ui.label("Metadata").classes("text-h6 mb-3")

            with ui.row().classes("w-full gap-4 items-start"):
                ui.label("Task:").classes("w-1/4 font-bold")
                ui.label(prompt_json.get("task", "")).classes("w-3/4 text-wrap")

            with ui.row().classes("w-full gap-4 items-start"):
                ui.label("Role:").classes("w-1/4 font-bold")
                ui.label(prompt_json.get("role", "")).classes("w-3/4 text-wrap")

            with ui.row().classes("w-full gap-4 items-start"):
                ui.label("AI:").classes("w-1/4 font-bold")
                ui.label(prompt.ai).classes("w-3/4 text-wrap")

            with ui.row().classes("w-full gap-4 items-start"):
                ui.label("Description:").classes("w-1/4 font-bold")
                ui.label(prompt.description).classes("w-3/4 text-wrap")

            with ui.row().classes("w-full gap-4 items-start"):
                ui.label("Version:").classes("w-1/4 font-bold")
                ui.label(prompt_json.get("version", "")).classes("w-3/4 text-wrap")

            with ui.row().classes("w-full gap-4 items-start"):
                ui.label("Last Updated:").classes("w-1/4 font-bold")
                ui.label(prompt_json.get("last_updated", "")).classes("w-3/4 text-wrap")

        with ui.card().classes("w-full dark:bg-slate-800"):
            ui.label("Prompt").classes("text-h6 mb-3")
            ui.label(prompt.prompt).classes("w-full text-wrap text-sm")

        with ui.card().classes("w-full dark:bg-slate-800"):
            ui.label("System Message").classes("text-h6 mb-3")
            ui.label(prompt.system_message).classes("w-full text-wrap text-sm")

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button(
                "Edit",
                icon="edit",
                on_click=lambda: open_edit_prompt_dialog(prompt),
            ).props("color=primary")
            ui.button(
                "Back to Prompts",
                icon="arrow_back",
                on_click=lambda: ui.run_javascript('window.location.href = "/prompt"'),
            ).props("flat")
