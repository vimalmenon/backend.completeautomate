from backend.services.agent.base_agent import BaseAgent

class FrontendAgent(BaseAgent):
    name = "Frontend Agent"
    role = "Frontend Developer"
    responsibility = "Building and maintaining the user interface of applications"
    teams = []

    def __init__(self):
        pass

    def start_task(self, task: str):
        pass

    def resume_task(self, task_id: str):
        pass
