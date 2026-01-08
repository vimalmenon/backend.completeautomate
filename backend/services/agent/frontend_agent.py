from backend.services.utility.system_prompt.system_prompt_utility import (
    SystemPromptUtility,
)
from backend.config.enum import TeamEnum
from langchain.agents import create_agent
from backend.services.ai.groq_ai import GroqAI
from backend.services.tool.command_tool import CommandTool
from langchain.messages import SystemMessage, HumanMessage, ToolMessage
from backend.services.agent.base_agent import BaseAgent
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)


class FrontendAgent(BaseAgent):
    name = "Elizabeth"
    role = TeamEnum.FRONTEND_DEVELOPER
    responsibility = "Building and maintaining the user interface of applications"
    teams = []

    def __init__(self):
        self.system_prompt = SystemPromptUtility(
            role=self.role, teams=self.teams
        ).get_system_prompt()
        self.model = GroqAI().get_model()
        self.command_tool = CommandTool()
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> List[Dict[str, Any]]:
        """
        Initialize available tools for the agent.

        Returns:
            List of tool definitions
        """
        tools = [self.command_tool.get_tool_definition()]
        return tools

    def _handle_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Handle tool calls from the agent.

        Args:
            tool_name: Name of the tool to call
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result as string
        """
        if tool_name == "command_executor":
            if not isinstance(tool_input, dict):
                return json.dumps({"error": "Invalid input format for command_executor"})
            result = self.command_tool.execute_command(
                command=tool_input.get("command"),
                cwd=tool_input.get("cwd"),
                shell=tool_input.get("shell", False)
            )
            return json.dumps(result)
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

    def execute_command(
        self, command: str, cwd: str = None, shell: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a shell command using the CommandTool.

        Args:
            command: The command to execute
            cwd: Working directory (optional)
            shell: Whether to use shell execution (default: False)

        Returns:
            Result dictionary with returncode, stdout, stderr, and success flag
        """
        result = self.command_tool.execute_command(
            command=command, cwd=cwd, shell=shell
        )
        return result

    def start_task(self, task: str):
        agent = create_agent(
            name=self.name,
            model=self.model,
            tools=self.tools,
            system_prompt=self.system_prompt,
        )
        messages = [
            SystemMessage(
                content="You are a frontend developer agent. Your role is to build and maintain the user interface of applications."
            ),
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

                        logger.info(f"Calling tool: {tool_name} with input: {tool_input}")

                        # Execute the tool
                        tool_result = self._handle_tool_call(tool_name, tool_input)

                        # Add tool message to messages
                        messages.append(
                            ToolMessage(
                                content=tool_result,
                                tool_call_id=tool_call.get("id"),
                                name=tool_name
                            )
                        )
                        logger.info(f"Tool result: {tool_result}")
                else:
                    # No more tool calls, exit loop
                    logger.info("Agent completed task, no more tool calls")
                    break
            else:
                break

        breakpoint()
        return result

    def resume_task(self, task_id: str):
        pass
