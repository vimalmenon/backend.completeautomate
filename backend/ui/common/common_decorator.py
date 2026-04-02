from functools import wraps

from nicegui import ui


def ui_dialog_box(on_save):
    def decorator(f):
        @wraps(f)
        def dialog(f):
            with ui.dialog() as dialog, ui.card().classes("w-96"):
                f()

                with ui.row().classes("w-full justify-end gap-2 mt-4"):
                    ui.button("Cancel", on_click=dialog.close).props("flat")
                    ui.button("Save", icon="save", on_click=on_save).props(
                        "color=primary"
                    )

            dialog.open()

        return dialog

    return decorator
