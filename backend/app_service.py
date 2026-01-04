from backend.services.task.pending_task import PendingTask
from backend.services.task.start_new_task import StartNewTask
from backend.services.task.scrum_master_task import ScrumMasterAgent
from backend.services.task.new_idea_task import NewIdeaTask


class AppService:

    def start(self) -> None:
        # Start new Ideas
        NewIdeaTask().input(
            idea="I want to list down the tasks to be performed by team as task name as what they have to do and team."
        )
        # Get Human Confirmation
        # HumanInputTask().input()
        # Get pending tasks
        # PendingTask().check()
        # Prepare next tasks
        # ScrumMasterAgent().check()
        # Start next tasks
        # StartNewTask().check()

        # print(
        #     CompanyDetailUtility(
        #         "AI Automation Service Provider",
        #         responsibility="driving innovation and excellence in automation solutions",
        #     ).company_values
        # )
