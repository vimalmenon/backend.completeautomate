from backend.services.utility.system_prompt.system_prompt_utility import (
    SystemPromptUtility,
)
from backend.config.enum import TeamEnum
from langgraph.prebuilt import create_react_agent
from backend.services.ai.deepseek_ai import DeepseekAI
from backend.services.tool.command_tool import CommandTool
from langchain.messages import SystemMessage, HumanMessage, ToolMessage
from backend.services.agent.base_agent import BaseAgent
from typing import Dict, Any, List


class FrontendAgent(BaseAgent):
    name = "Elizabeth"
    role = TeamEnum.FRONTEND_DEVELOPER
    responsibility = "Building and maintaining the user interface of applications"
    teams = []

    def __init__(self):
        self.system_prompt = SystemPromptUtility(
            role=self.role, teams=self.teams
        ).get_system_prompt()
        self.model = DeepseekAI().get_model()
        self.command_tool = CommandTool()
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> List[Dict[str, Any]]:
        """
        Initialize available tools for the agent.
        
        Returns:
            List of tool definitions
        """
        tools = [
            self.command_tool.get_tool_definition()
        ]
        return tools

    def execute_command(self, command: str, cwd: str = None, shell: bool = False) -> Dict[str, Any]:
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
            command=command,
            cwd=cwd,
            shell=shell
        )
        return result

    def start_task(self, task: str):
        agent = create_react_agent(
            name=self.name,
            model=self.model,
            tools=self.tools,
            # state_modifier=self.system_prompt
        )
        messages = [
            HumanMessage(content=(self.system_prompt + task)),
        ]
        # Pass messages as a dictionary with 'messages' key
        for step in agent.stream({"messages": messages}, stream_mode="values"):
            if "messages" in step:
                step["messages"][-1].pretty_print()

        # result = agent.invoke(
        #     {
        #         "messages": messages,
        #         "user_preferences": {"style": "technical", "verbosity": "detailed"},
        #     }
        # )
        breakpoint()
        # return result

    def resume_task(self, task_id: str):
        pass

