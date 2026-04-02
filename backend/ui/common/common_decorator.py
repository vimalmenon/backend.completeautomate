from nicegui import ui


def ui_dialog_box(on_save, render_item):

    with ui.dialog() as dialog, ui.card().classes("w-96"):

        render_item()

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Save", icon="save", on_click=on_save).props("color=primary")

    dialog.open()


def ui_render_common_container(render_item):
    render_item()
