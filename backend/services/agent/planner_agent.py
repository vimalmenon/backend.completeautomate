from backend.services.helper.system_prompt.system_prompt_helper import (
    SystemPromptHelper,
)
from backend.config.enum import TeamEnum
from langchain.agents import create_agent
from backend.services.ai.deepseek_ai import DeepseekAI
from langchain.messages import SystemMessage, HumanMessage
from backend.services.agent.base_agent import BaseAgent
from typing import Dict, Any, List
import logging
from langchain.tools import tool, ToolRuntime
from backend.services.aws.message_db import MessageDB
from backend.services.aws.task_db import TaskDB, PlannedTaskOutputResponse

logger = logging.getLogger(__name__)


@tool
def list_all_tasks(runtime: ToolRuntime) -> List[Dict[str, Any]]:
    """
    Get all tasks from the TaskDB.

    Returns:
        List of tasks in JSON format

    """
    tasks = TaskDB().get_tasks() or []
    return [task.to_json() for task in tasks]


class PlannerAgent(BaseAgent):
    name: str = "Parker"
    role: TeamEnum = TeamEnum.PLANNER
    teams: List[TeamEnum] = []

    def __init__(self):
        self.system_prompt_helper = SystemPromptHelper(role=self.role, teams=self.teams)
        self.system_prompt = self.system_prompt_helper.get_system_prompt()
        self.model = DeepseekAI().get_model()

    def start_task(self, task: str):
        agent = create_agent(
            name=self.name,
            model=self.model,
            tools=[list_all_tasks],
            system_prompt=self.system_prompt,
            response_format=PlannedTaskOutputResponse,
        )
        system_message = self.system_prompt_helper.get_system_message(
            content="You are a planner agent. Your role is to plan and organize tasks and get all the planned tasks before starting the planning process."
        )
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=task),
        ]

        try:
            result = agent.invoke(
                {
                    "messages": messages,
                }
            )
            MessageDB(self.role).save_message_from_agent_result(result)
            if structured_response := result.get("structured_response"):
                TaskDB().save_tasks(structured_response)
            # Reset retry count on successful invocation
        except Exception as e:
            pass

        logger.info("Agent task completed successfully")
        return result

    def resume_task(self, ref_id: str):
        pass
