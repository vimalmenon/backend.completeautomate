from backend.enum import ActionEnum
from backend.manager.transform import transform_data


class ActionManager:
    def __init__(self, action: str):
        self.action = ActionEnum(action)

    def execute(self) -> None:
        if self.action == ActionEnum.transform:
            transform_data()
        else:
            pass
