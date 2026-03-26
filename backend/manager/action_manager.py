from backend.enum import ActionEnum


class ActionManager:
    def __init__(self, action: ActionEnum):
        self.action = action

    def execute(self) -> None:
        pass
