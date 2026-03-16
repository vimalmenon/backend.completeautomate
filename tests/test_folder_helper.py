"""Unit tests for FolderHelper"""

import pickle

import pytest

from backend.helper.folder_helper.folder_helper import FolderHelper


@pytest.mark.unit
class TestFolderHelper:
    """Test cases for FolderHelper class"""

    def test_create_pickle_file_creates_parent_and_writes_data(self, tmp_path) -> None:
        """Creates missing folders and writes pickle data to file"""
        helper = FolderHelper()
        output_path = tmp_path / "nested" / "token.pickle"
        payload = {"token": "abc123", "expires": 3600}

        raw_bytes = helper.create_pickle_file(str(output_path), payload)

        assert output_path.exists()
        assert output_path.is_file()
        assert isinstance(raw_bytes, bytes)
        assert pickle.loads(raw_bytes) == payload
        with output_path.open("rb") as pickle_file:
            loaded = pickle.load(pickle_file)
        assert loaded == payload

    def test_create_pickle_file_raises_for_existing_directory(self, tmp_path) -> None:
        """Raises when target path points to an existing directory"""
        helper = FolderHelper()
        directory_path = tmp_path / "already_a_directory"
        directory_path.mkdir(parents=True, exist_ok=True)

        with pytest.raises(IsADirectoryError):
            helper.create_pickle_file(str(directory_path), {"value": 1})
