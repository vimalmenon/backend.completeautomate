import pickle
import shutil
from pathlib import Path
from typing import Any


class FolderHelper:

    def create_missing_folders(self, path: str) -> None:
        normalized_path = Path(path)

        if normalized_path.suffix:
            if normalized_path.exists() and normalized_path.is_dir():
                raise IsADirectoryError(
                    f"Expected a file path but found an existing directory: {normalized_path}"
                )
            target_dir = normalized_path.parent
        else:
            target_dir = normalized_path

        target_dir.mkdir(parents=True, exist_ok=True)

    def check_if_file_exists(self, path: str) -> bool:
        normalized_path = Path(path)
        return normalized_path.is_file()

    def delete_folder(self, path: str) -> None:
        normalized_path = Path(path)

        if not normalized_path.exists():
            return

        if not normalized_path.is_dir():
            raise NotADirectoryError(
                f"Path exists but is not a directory: {normalized_path}"
            )

        shutil.rmtree(normalized_path)

    def create_pickle_file(self, path: str, data: Any) -> bytes:
        normalized_path = Path(path)

        if normalized_path.exists() and normalized_path.is_dir():
            raise IsADirectoryError(
                f"Expected a file path but found an existing directory: {normalized_path}"
            )

        self.create_missing_folders(path)
        serialized_data = pickle.dumps(data)
        with normalized_path.open("wb") as pickle_file:
            pickle_file.write(serialized_data)
        return serialized_data

    def create_pickle_data(self, data: Any) -> bytes:
        return pickle.dumps(data)

    def unpack_pickle_data(self, path: str):
        return pickle.loads(path)
