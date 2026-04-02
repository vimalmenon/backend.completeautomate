from nicegui import ui


def render_notify(msg: str):
    ui.notify(msg, type="positive", position="top")


def render_separator():
    ui.separator()


def render_breadcrumbs(items: list[tuple[str, str]], right_text: str = ""):
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


def render_common_header(page_title: str):
    with ui.row().classes("items-center justify-between w-full mb-4"):
        ui.label(page_title).classes("text-h4")
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


def render_not_found_message(message: str, icon: str | None = None):
    with ui.card().classes("w-full bg-gray-100 dark:bg-slate-800"):
        if icon:
            ui.icon("inbox", size="xl").classes("text-gray-400")
        ui.label(message).classes("text-h6 text-gray-500")


def render_textarea(label, value):
    return (
        ui.textarea(label=label, value=value)
        .props("outlined autogrow")
        .classes("w-full mt-3")
    )


def render_select_option(label, value, options):
    return (
        ui.select(
            options=options,
            value=value,
            label=label,
        )
        .props("outlined dense")
        .classes("w-full")
    )
