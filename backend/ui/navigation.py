"""Navigation utilities with loading states"""

from nicegui import ui


def navigate_with_loading(url: str, label: str = "Loading..."):
    """
    Navigate to a URL with a loading indicator

    Args:
        url: Target URL to navigate to
        label: Loading message to display
    """

    async def navigate():
        # Show loading overlay
        ui.notify(f"Navigating to {url}...", type="info", position="top")
        ui.run_javascript(f'window.location.href = "{url}"')

    return navigate


def create_nav_link(text: str, url: str, classes: str = "text-white"):
    """
    Create a navigation link with loading feedback

    Args:
        text: Link text
        url: Target URL
        classes: CSS classes for the link
    """
    button = ui.button(text, on_click=navigate_with_loading(url, f"Loading {text}..."))
    button.classes(classes)
    return button
