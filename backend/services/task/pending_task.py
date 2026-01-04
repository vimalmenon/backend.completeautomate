from backend.config.enum import TeamEnum


class PendingTask:
    tasks = [TeamEnum.SCRUM_MASTER, TeamEnum.RESEARCHER]

    def check(self):
        # Get all pending tasks
        # Make agent work on tasks
        for task in self.tasks:
            print(task)
