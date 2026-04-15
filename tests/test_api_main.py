from unittest.mock import patch

from backend.api.main import initialize_api_data


def test_initialize_api_data_restores_downloaded_data_when_offline() -> None:
    call_order: list[str] = []

    with (
        patch("backend.api.main.env.OFFLINE", True),
        patch("backend.api.main.DataManager") as mock_data_manager_cls,
    ):
        mock_data_manager = mock_data_manager_cls.return_value
        mock_data_manager.start_up_script.side_effect = lambda: call_order.append(
            "startup"
        )
        mock_data_manager.download.side_effect = lambda: call_order.append("download")

        initialize_api_data()

    assert call_order == ["startup", "download"]


def test_initialize_api_data_skips_restore_when_online() -> None:
    call_order: list[str] = []

    with (
        patch("backend.api.main.env.OFFLINE", False),
        patch("backend.api.main.DataManager") as mock_data_manager_cls,
    ):
        mock_data_manager = mock_data_manager_cls.return_value
        mock_data_manager.start_up_script.side_effect = lambda: call_order.append(
            "startup"
        )
        mock_data_manager.download.side_effect = lambda: call_order.append("download")

        initialize_api_data()

    assert call_order == ["startup"]