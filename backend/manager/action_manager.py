from backend.enum import ActionEnum
from backend.manager.data_manager import DataManager
from backend.manager.transform import transform_data


class ActionManager:
    def __init__(self, action: str):
        try:
            self.action = ActionEnum(action)
        except ValueError:
            raise ValueError(
                f"Invalid action: {action}: Allowed values are {[e.value for e in ActionEnum]}"
            )

    def execute(self) -> None:
        if self.action == ActionEnum.transform:
            transform_data()
        elif self.action == ActionEnum.backup_db:
            DataManager().backup_db()
        elif self.action == ActionEnum.restore_db:
            DataManager()
        elif self.action == ActionEnum.download_to_local:
            DataManager().download()
        elif self.action == ActionEnum.restore_from_local:
            DataManager().upload()
