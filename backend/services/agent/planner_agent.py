from backend.services.helper.system_prompt.system_prompt_helper import (
    SystemPromptHelper,
)
from backend.config.enum import TeamEnum
from langchain.agents import create_agent
from backend.services.ai.deepseek_ai import DeepseekAI
from backend.services.tool.file_tool import FileTool
from langchain.messages import SystemMessage, HumanMessage, ToolMessage
from backend.services.agent.base_agent import BaseAgent
from typing import Dict, Any, List
import logging
import time
from langchain.tools import tool
from backend.services.aws.message_db import MessageDB
from backend.services.aws.task_db import TaskDB, PlannedTaskOutputResponse

logger = logging.getLogger(__name__)


@tool
def list_all_tasks() -> List[Dict[str, Any]]:
    """
    Tool to list all tasks from the TaskDB.

    Returns:
        List of tasks as dictionaries
    """
    breakpoint()
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
        self.file_tool = FileTool()
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> List[Dict[str, Any]]:
        """
        Initialize available tools for the agent.

        Returns:
            List of tool definitions
        """
        return [list_all_tasks]

    def _handle_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Handle tool calls from the agent.

        Args:
            tool_name: Name of the tool to call
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result as string
        """
        breakpoint()

    def start_task(self, task: str, max_retries: int = 3):
        agent = create_agent(
            name=self.name,
            model=self.model,
            tools=self.tools,
            system_prompt=self.system_prompt,
            response_format=PlannedTaskOutputResponse,
        )
        system_message = self.system_prompt_helper.get_system_message(
            content="You are a planner agent. Your role is to plan and organize tasks, and manage project documentation."
        )
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=task),
        ]

        # Run agent in a loop to handle tool calls
        retry_count = 0
        while True:
            try:
                result = agent.invoke(
                    {
                        "messages": messages,
                    }
                )
                breakpoint()
                # MessageDB().save_message_from_agent_result(result)
                TaskDB().save_tasks(result["structured_response"])
                # result["structured_response"].tasks
                # Reset retry count on successful invocation
                retry_count = 0

            except Exception as e:
                retry_count += 1
                error_msg = f"Error invoking agent (attempt {retry_count}/{max_retries}): {str(e)}"
                logger.error(error_msg)

                if retry_count >= max_retries:
                    logger.error(f"Max retries ({max_retries}) reached. Aborting.")
                    return {
                        "error": error_msg,
                        "messages": messages,
                        "success": False,
                    }

                # Wait before retrying (exponential backoff)
                wait_time = 2**retry_count
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue

            # Update messages with agent response
            if "messages" in result:
                messages = result["messages"]
                last_message = messages[-1]
                last_message.pretty_print()
                logger.info(f"Agent response: {last_message}")

                # Check if the last message contains tool use
                if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                    for tool_call in last_message.tool_calls:
                        # Extract tool name and input from different formats
                        tool_name = None
                        tool_input = None

                        if isinstance(tool_call, dict):
                            tool_name = tool_call.get("name") or tool_call.get("tool")
                            tool_input = tool_call.get("args") or tool_call.get("input")
                        else:
                            tool_name = getattr(tool_call, "name", None) or getattr(
                                tool_call, "tool", None
                            )
                            tool_input = getattr(tool_call, "args", None) or getattr(
                                tool_call, "input", None
                            )

                        if not tool_name or not tool_input:
                            logger.warning(f"Invalid tool call format: {tool_call}")
                            continue

                        logger.info(
                            f"Calling tool: {tool_name} with input: {tool_input}"
                        )

                        # Execute the tool
                        tool_result = self._handle_tool_call(tool_name, tool_input)
                        logger.info(f"Tool result: {tool_result}")

                        # Add tool message to messages
                        tool_call_id = (
                            tool_call.get("id")
                            if isinstance(tool_call, dict)
                            else getattr(tool_call, "id", None)
                        )
                        messages.append(
                            ToolMessage(
                                content=tool_result,
                                tool_call_id=tool_call_id,
                                name=tool_name,
                            )
                        )
                else:
                    # No more tool calls, exit loop
                    logger.info("Agent completed task, no more tool calls")
                    break
            else:
                break

        logger.info("Agent task completed successfully")
        return result

    def resume_task(self, ref_id: str):
        pass
