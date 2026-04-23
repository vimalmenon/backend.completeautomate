from backend.manager.job_manager import JobManager


class JobSchedulerManager:
    def __init__(self):
        self.job_manger = JobManager()

    def execute(self): ...
