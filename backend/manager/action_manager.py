from backend.enum import ActionEnum


class ActionManager:
    def __init__(self, action: str):
        self.action = ActionEnum(action)

    def execute(self) -> None:
        pass
