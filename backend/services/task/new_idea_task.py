from backend.services.agent.manager_agent import ManagerAgent


class NewIdeaTask:

    def input(self, idea: str):
        manager = ManagerAgent()
        print(idea)
