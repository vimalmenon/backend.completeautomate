from nicegui import ui


def main_page():
    menu_items = {
        "Tasks": [
            {
                "name": "List Tasks",
                "links_to": "/tasks?page=list_tasks",
            },
        ],
        "YouTube": [
            {
                "name": "List Videos",
                "links_to": "/youtube?page=youtube_videos",
            },
            {
                "name": "List Channel",
                "links_to": "/youtube?page=youtube_channel",
            },
        ],
        "Prompt": [
            {
                "name": "List Prompts",
                "links_to": "/prompt?page=list_prompts",
            },
        ],
    }

    with ui.card().classes("w-full"):
        ui.label("CompleteAutomate Dashboard").classes("text-h4 mb-4")
        ui.separator()

        ui.label("Navigate to:").classes("text-h6 mt-4")

        for category, items in menu_items.items():
            with ui.expansion(category, icon="folder").classes("w-full"):
                for item in items:
                    with ui.row().classes("items-center"):
                        ui.icon("arrow_forward", size="sm")
                        ui.link(item["name"], item["links_to"]).classes("ml-2")
