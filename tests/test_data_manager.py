from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from backend.exception.app_exception import AppException
from backend.manager.data_manager import DataManager, env


def test_restore_from_s3_runs_download_then_upload() -> None:
    call_order: list[str] = []

    with (
        patch.object(
            DataManager,
            "download_to_local",
            side_effect=lambda: call_order.append("download_to_local"),
        ),
        patch.object(
            DataManager,
            "upload",
            side_effect=lambda: call_order.append("upload"),
        ),
    ):
        DataManager().restore_from_s3()

    assert call_order == ["download_to_local", "upload"]


def test_download_to_local_exports_db_snapshots_then_downloads_s3() -> None:
    fake_db = SimpleNamespace(
        s3_data="fake-s3-data",
        get_data=lambda: ["raw-db-record"],
        convert_json_to_cls=lambda data: [f"converted:{data[0]}"],
    )
    call_order: list[tuple[str, object, object] | tuple[str]] = []

    with (
        patch("backend.manager.data_manager.db_data", [fake_db]),
        patch.object(
            DataManager,
            "_DataManager__download_and_upload_pickle_file_to_s3",
            side_effect=lambda s3_data, data: call_order.append(
                ("export_pickle", s3_data, data)
            ),
        ),
        patch.object(
            DataManager,
            "_DataManager__download_for_s3",
            side_effect=lambda: call_order.append(("download_s3",)),
        ),
    ):
        DataManager().download_to_local()

    assert call_order == [
        ("export_pickle", "fake-s3-data", ["converted:raw-db-record"]),
        ("download_s3",),
    ]


def test_download_for_s3_ignores_missing_s3_objects_when_offline() -> None:
    mock_download = MagicMock(side_effect=AppException("missing"))

    with (
        patch.object(
            DataManager,
            "_DataManager__get_s3_values",
            return_value=[object()],
        ),
        patch(
            "backend.manager.data_manager.S3Storage.download_data",
            mock_download,
        ),
        patch.object(env, "OFFLINE", True),
    ):
        DataManager()._DataManager__download_for_s3()

    mock_download.assert_called_once()
