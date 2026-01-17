from backend.services.helper.system_prompt.system_prompt_helper import (
    SystemPromptHelper,
)
from backend.config.enum import TeamEnum
from langchain.agents import create_agent
from backend.services.ai.deepseek_ai import DeepseekAI
from backend.services.tool.file_tool import FileTool
from langchain.messages import SystemMessage, HumanMessage, ToolMessage
from backend.services.agent.base_agent import BaseAgent
from typing import Dict, Any, List, Optional
import json
import logging
from langchain.tools import tool

logger = logging.getLogger(__name__)


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
        return [
            self.file_tool.get_write_tool_definition(),
            self.file_tool.get_read_tool_definition(),
        ]

    def _handle_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Handle tool calls from the agent.

        Args:
            tool_name: Name of the tool to call
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result as string
        """
        if not isinstance(tool_input, dict):
            return json.dumps({"error": f"Invalid input format for {tool_name}"})

        if tool_name == "file_writer":
            result = self.file_tool.write_file(
                file_path=tool_input.get("file_path"),
                content=tool_input.get("content"),
                mode=tool_input.get("mode", "w"),
            )
            return json.dumps(result)
        elif tool_name == "file_reader":
            result = self.file_tool.read_file(
                file_path=tool_input.get("file_path"),
            )
            return json.dumps(result)
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

    def write_file(
        self, file_path: str, content: str, mode: str = "w"
    ) -> Dict[str, Any]:
        """
        Write content to a file using the FileTool.

        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            mode: Write mode ('w' for overwrite, 'a' for append)

        Returns:
            Result dictionary with success status and message
        """
        result = self.file_tool.write_file(
            file_path=file_path, content=content, mode=mode
        )
        return result

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read content from a file using the FileTool.

        Args:
            file_path: Path to the file to read

        Returns:
            Result dictionary with file content or error message
        """
        result = self.file_tool.read_file(file_path=file_path)
        return result

    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        Delete a file using the FileTool.

        Args:
            file_path: Path to the file to delete

        Returns:
            Result dictionary with success status and message
        """
        result = self.file_tool.delete_file(file_path=file_path)
        return result

    def start_task(self, task: str):
        agent = create_agent(
            name=self.name,
            model=self.model,
            tools=self.tools,
            system_prompt=self.system_prompt,
        )
        system_message = self.system_prompt_helper.get_system_message(
            content="You are a planner agent. Your role is to plan and organize tasks, and manage project documentation."
        )
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=task),
        ]

        # Run agent in a loop to handle tool calls
        while True:
            result = agent.invoke(
                {
                    "messages": messages,
                    "user_preferences": {"style": "technical", "verbosity": "detailed"},
                }
            )

            # Update messages with agent response
            if "messages" in result:
                messages = result["messages"]
                last_message = messages[-1]
                last_message.pretty_print()
                logger.info(f"Agent response: {last_message}")

                # Check if the last message contains tool use
                if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                    for tool_call in last_message.tool_calls:
                        tool_name = tool_call.get("name") or tool_call.get("tool")
                        tool_input = tool_call.get("args") or tool_call.get("input")

                        logger.info(
                            f"Calling tool: {tool_name} with input: {tool_input}"
                        )

                        # Execute the tool
                        tool_result = self._handle_tool_call(tool_name, tool_input)
                        breakpoint()
                        # Add tool message to messages
                        messages.append(
                            ToolMessage(
                                content=tool_result,
                                tool_call_id=tool_call.get("id"),
                                name=tool_name,
                            )
                        )
                        logger.info(f"Tool result: {tool_result}")
                else:
                    # No more tool calls, exit loop
                    logger.info("Agent completed task, no more tool calls")
                    break
            else:
                break
        return result

    def resume_task(self, task_id: str):
        pass
