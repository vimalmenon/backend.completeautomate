from typing import TypedDict

from nicegui import ui


class MenuItem(TypedDict):
    name: str
    icon: str
    links_to: str


class MenuSection(TypedDict):
    category: str
    icon: str
    items: list[MenuItem]


def main_page():
    menu_items: list[MenuSection] = [
        {
            "category": "Tasks",
            "icon": "task",
            "items": [
                {
                    "name": "List Tasks",
                    "icon": "list_alt",
                    "links_to": "/tasks",
                },
            ],
        },
        {
            "category": "YouTube",
            "icon": "video_library",
            "items": [
                {
                    "name": "List Videos",
                    "icon": "ondemand_video",
                    "links_to": "/youtube",
                },
                {
                    "name": "List Channel",
                    "icon": "live_tv",
                    "links_to": "/youtube",
                },
            ],
        },
        {
            "category": "Prompt",
            "icon": "article",
            "items": [
                {
                    "name": "List Prompts",
                    "icon": "description",
                    "links_to": "/prompt",
                },
            ],
        },
    ]

    with ui.card().classes("w-full"):
        ui.label("CompleteAutomate Dashboard").classes("text-h4 mb-4")
        ui.separator()

        ui.label("Navigate to:").classes("text-h6 mt-4")

        with ui.column().classes("w-full gap-3 mt-2"):
            for section in menu_items:
                with ui.card().classes(
                    "w-full border border-gray-200 dark:border-slate-700"
                ):
                    with ui.row().classes("items-center gap-2 mb-2"):
                        ui.icon(section["icon"], size="md")
                        ui.label(section["category"]).classes(
                            "text-subtitle1 font-semibold"
                        )

                    with ui.row().classes("w-full gap-2 flex-wrap"):
                        for item in section["items"]:
                            with ui.button(
                                item["name"],
                                icon=item["icon"],
                                on_click=lambda target=item[
                                    "links_to"
                                ]: ui.run_javascript(
                                    f'window.location.href = "{target}"'
                                ),
                            ).props("flat"):
                                ui.tooltip(item["links_to"])
