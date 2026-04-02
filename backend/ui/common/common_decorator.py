from nicegui import ui


def ui_dialog_box(on_save, render_item):

    with (
        ui.dialog() as dialog,
        ui.card().classes("width:min(960px, 92vw) height:min(760px, 88vh)"),
    ):
        with ui.card().style(
            "width:min(960px, 92vw); height:min(760px, 88vh);display:flex; flex-direction:column; "
            "padding:0; gap:0;"
        ):
            render_item()

            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                ui.button("Cancel", on_click=dialog.close).props("flat")
                ui.button("Save", icon="save", on_click=on_save).props("color=primary")

    return dialog


def ui_render_common_container(render_item):
    render_item()
