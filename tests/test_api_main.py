from unittest.mock import patch

from backend.api.main import initialize_api_data


def test_initialize_api_data_uploads_data_when_offline() -> None:
    call_order: list[str] = []

    with (
        patch("backend.api.main.env.OFFLINE", True),
        patch("backend.api.main.DataManager") as mock_data_manager_cls,
    ):
        mock_data_manager = mock_data_manager_cls.return_value
        mock_data_manager.upload.side_effect = lambda: call_order.append("upload")

        initialize_api_data()

    assert call_order == ["upload"]


def test_initialize_api_data_skips_upload_when_online() -> None:
    mock_data_manager = None

    with (
        patch("backend.api.main.env.OFFLINE", False),
        patch("backend.api.main.DataManager") as mock_data_manager_cls,
    ):
        mock_data_manager = mock_data_manager_cls.return_value

        initialize_api_data()

    assert mock_data_manager is not None
    mock_data_manager.upload.assert_not_called()
