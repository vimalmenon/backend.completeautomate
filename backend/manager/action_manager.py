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
            DataManager().download_data_and_upload_to_s3()
        elif self.action == ActionEnum.restore_db:
            DataManager().restore_db_from_s3()
        elif self.action == ActionEnum.download_to_local:
            DataManager().download()
        elif self.action == ActionEnum.restore_from_local:
            DataManager().upload()
