import importlib
from logging import getLogger
from pathlib import Path
from typing import Any

from backend.exception import AppException

logger = getLogger(__name__)

CREATE_SELECTORS = [
    "button:has-text('Create')",
    "ytcp-button[id='create-icon'] button",
    "button:has-text('Create post')",
]

EDITOR_SELECTORS = [
    "ytcp-social-suggestions-textbox [contenteditable='true']",
    "div[contenteditable='true']",
]

PUBLISH_SELECTORS = [
    "button:has-text('Post')",
    "button:has-text('Publish')",
    "ytcp-button[id='publish-button'] button",
]


def _validate_post_inputs(channel_id: str, text: str) -> None:
    if not channel_id or not channel_id.strip():
        raise AppException("Channel ID is required")
    if not text or not text.strip():
        raise AppException("Post text is required")


def _load_playwright_sync_api() -> tuple[Any, type[Exception]]:
    try:
        playwright_sync_api = importlib.import_module("playwright.sync_api")
        return playwright_sync_api.sync_playwright, playwright_sync_api.TimeoutError
    except Exception as e:
        raise AppException(
            "Playwright is required for Community post automation. "
            "Install with: poetry add playwright; playwright install chromium"
        ) from e


def _click_first_matching(page: Any, selectors: list[str], timeout_ms: int) -> bool:
    for selector in selectors:
        try:
            page.locator(selector).first.click(timeout=timeout_ms)
            return True
        except Exception:
            continue
    return False


def _find_first_editor(page: Any, selectors: list[str], timeout_ms: int) -> Any | None:
    for selector in selectors:
        try:
            candidate = page.locator(selector).first
            candidate.click(timeout=timeout_ms)
            return candidate
        except Exception:
            continue
    return None


def _open_studio_posts_page(page: Any, channel_id: str, timeout_ms: int) -> None:
    page.goto(
        f"https://studio.youtube.com/channel/{channel_id}/posts",
        wait_until="domcontentloaded",
        timeout=timeout_ms,
    )

    if "accounts.google.com" in page.url:
        raise AppException(
            "Google sign-in is required in the browser profile before posting."
        )


def _compose_and_publish_post(page: Any, text: str) -> None:
    clicked_create = _click_first_matching(page, CREATE_SELECTORS, timeout_ms=4_000)
    if not clicked_create:
        raise AppException("Could not find the Create button in YouTube Studio")

    editor = _find_first_editor(page, EDITOR_SELECTORS, timeout_ms=5_000)
    if editor is None:
        raise AppException("Could not find the Community post editor in Studio")

    page.keyboard.type(text)

    published = _click_first_matching(page, PUBLISH_SELECTORS, timeout_ms=5_000)
    if not published:
        raise AppException("Could not find the Post/Publish button in Studio")


def create_community_post_via_studio(
    channel_id: str,
    text: str,
    *,
    headless: bool = False,
    timeout_ms: int = 60_000,
    user_data_dir: str = "backend/output/chrome-profile",
) -> bool:
    """
    Create a YouTube Community post via YouTube Studio browser automation.

    Notes:
    - This does not use YouTube Data API v3.
    - A signed-in Google session is required in the persistent browser profile.
    """
    _validate_post_inputs(channel_id, text)

    sync_playwright, playwright_timeout_error = _load_playwright_sync_api()

    Path(user_data_dir).mkdir(parents=True, exist_ok=True)

    try:
        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=headless,
            )
            page = context.pages[0] if context.pages else context.new_page()

            _open_studio_posts_page(page, channel_id, timeout_ms)
            _compose_and_publish_post(page, text)

            context.close()
            logger.info("Community post published through YouTube Studio automation")
            return True

    except playwright_timeout_error as e:
        logger.error(f"Timeout while creating Community post: {e}")
        raise AppException(
            "Timed out while creating Community post in YouTube Studio"
        ) from e
    except AppException:
        raise
    except Exception as e:
        logger.error(f"An error occurred while creating Community post: {e}")
        raise AppException(
            f"An error occurred while creating Community post: {str(e)}"
        ) from e
