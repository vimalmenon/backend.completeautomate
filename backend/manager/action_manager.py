from tabulate import tabulate

from backend.enum import ActionEnum
from backend.manager.data_manager import DataManager
from backend.manager.job_manager import JobManager
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
        elif self.action == ActionEnum.restore_from_s3:
            DataManager().restore_from_s3()
        elif self.action == ActionEnum.download_to_local:
            DataManager().download_to_local()
        elif self.action == ActionEnum.restore_from_local:
            DataManager().upload()
        elif self.action == ActionEnum.show_jobs:
            self.show_all_jobs()

    def show_all_jobs(self):
        jobs = JobManager().get_all_jobs()
        data = [[job.id, job.type, job.status, job.created_at] for job in jobs]
        headers = ["ID", "Type", "Status", "Created At"]
        print(tabulate(data, headers=headers, tablefmt="grid"))
