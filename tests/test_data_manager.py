from unittest.mock import patch

from backend.exception.app_exception import AppException
from backend.manager.data_manager import DataManager, env


def test_download_uploads_downloaded_data_to_db_when_offline() -> None:
    call_order: list[str] = []

    with (
        patch.object(
            DataManager,
            "_DataManager__download_for_s3",
            side_effect=lambda: call_order.append("download"),
        ),
        patch.object(
            DataManager,
            "_DataManager__upload_downloaded_db_data",
            side_effect=lambda: call_order.append("upload_db"),
        ),
        patch.object(env, "OFFLINE", True),
    ):
        DataManager().download()

    assert call_order == ["download", "upload_db"]


def test_download_skips_db_upload_when_online() -> None:
    call_order: list[str] = []

    with (
        patch.object(
            DataManager,
            "_DataManager__download_for_s3",
            side_effect=lambda: call_order.append("download"),
        ),
        patch.object(
            DataManager,
            "_DataManager__upload_downloaded_db_data",
            side_effect=lambda: call_order.append("upload_db"),
        ),
        patch.object(env, "OFFLINE", False),
    ):
        DataManager().download()

    assert call_order == ["download"]


def test_download_ignores_missing_s3_objects_when_offline() -> None:
    call_order: list[str] = []

    with (
        patch.object(
            DataManager,
            "_DataManager__get_s3_values",
            return_value=[object()],
        ),
        patch(
            "backend.manager.data_manager.S3Storage.download_data",
            side_effect=AppException("missing"),
        ),
        patch.object(
            DataManager,
            "_DataManager__upload_downloaded_db_data",
            side_effect=lambda: call_order.append("upload_db"),
        ),
        patch.object(env, "OFFLINE", True),
    ):
        DataManager().download()

    assert call_order == ["upload_db"]
