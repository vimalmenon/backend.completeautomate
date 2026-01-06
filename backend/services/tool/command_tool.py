import subprocess
from typing import Optional, Dict, Any, TypedDict


class CommandInput(TypedDict, total=False):
    """Input schema for CommandTool."""

    command: str  # Required: The command to execute
    cwd: Optional[str]  # Optional: Working directory
    shell: bool  # Optional: Use shell execution


class CommandOutput(TypedDict):
    """Output schema for CommandTool."""

    returncode: int  # Exit code
    stdout: str  # Standard output
    stderr: str  # Standard error
    success: bool  # Command success status


class CommandTool:
    """
    Tool for executing shell commands with output capture and error handling.

    This tool allows executing arbitrary shell commands in a specified working
    directory with comprehensive result information including exit codes,
    standard output, and error messages.
    """

    # Tool Metadata
    TOOL_NAME = "command_executor"
    TOOL_VERSION = "1.0.0"
    TOOL_DESCRIPTION = (
        "Execute shell commands and capture their output. "
        "Supports custom working directories and shell mode execution."
    )
    TOOL_CATEGORY = "execution"

    # Tool Schema
    INPUT_SCHEMA = {
        "type": "object",
        "title": "CommandToolInput",
        "description": "Input parameters for command execution",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute (e.g., 'ls -la', 'npm install')",
                "examples": ["npm install", "python script.py", "git status"],
            },
            "cwd": {
                "type": ["string", "null"],
                "description": "Working directory for command execution (optional)",
                "examples": ["/path/to/project", "/home/user/workspace", None],
            },
            "shell": {
                "type": "boolean",
                "description": "Whether to use shell execution for complex commands (default: False)",
                "examples": [True, False],
            },
        },
        "required": ["command"],
    }

    OUTPUT_SCHEMA = {
        "type": "object",
        "title": "CommandToolOutput",
        "description": "Result of command execution",
        "properties": {
            "returncode": {
                "type": "integer",
                "description": "Exit code (0 = success, non-zero = error)",
                "examples": [0, 1, -1],
            },
            "stdout": {
                "type": "string",
                "description": "Standard output from the command",
            },
            "stderr": {
                "type": "string",
                "description": "Standard error from the command",
            },
            "success": {
                "type": "boolean",
                "description": "Whether the command executed successfully",
            },
        },
        "required": ["returncode", "stdout", "stderr", "success"],
    }

    # Configuration
    DEFAULT_TIMEOUT = 300  # 5 minutes
    MAX_TIMEOUT = 1800  # 30 minutes

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize CommandTool.

        Args:
            timeout: Command execution timeout in seconds (default: 300)
        """
        if timeout > self.MAX_TIMEOUT:
            raise ValueError(f"Timeout cannot exceed {self.MAX_TIMEOUT} seconds")
        self.timeout = timeout

    @classmethod
    def get_tool_definition(cls) -> Dict[str, Any]:
        """
        Get complete tool definition for registration.

        Returns:
            Dictionary with full tool definition including metadata and schemas
        """
        return {
            "name": cls.TOOL_NAME,
            "version": cls.TOOL_VERSION,
            "description": cls.TOOL_DESCRIPTION,
            "category": cls.TOOL_CATEGORY,
            "inputSchema": cls.INPUT_SCHEMA,
            "outputSchema": cls.OUTPUT_SCHEMA,
            "examples": [
                {
                    "name": "List directory contents",
                    "input": {"command": "ls -la", "cwd": "/home/user"},
                    "output": {
                        "returncode": 0,
                        "stdout": "total 24\ndrwxr-xr-x  5 user  staff   160 Jan  6 10:30 .",
                        "stderr": "",
                        "success": True,
                    },
                },
                {
                    "name": "Install npm dependencies",
                    "input": {"command": "npm install", "cwd": "/project"},
                    "output": {
                        "returncode": 0,
                        "stdout": "added 150 packages",
                        "stderr": "",
                        "success": True,
                    },
                },
                {
                    "name": "Execute with shell",
                    "input": {"command": "echo $PATH && ls -la", "shell": True},
                    "output": {
                        "returncode": 0,
                        "stdout": "/usr/local/bin:/usr/bin\ntotal 24\n...",
                        "stderr": "",
                        "success": True,
                    },
                },
            ],
        }

    def execute_command(
        self, command: str, cwd: Optional[str] = None, shell: bool = False
    ) -> CommandOutput:
        """
        Execute a command and return the result.

        Args:
            command: The command to execute (string or list)
            cwd: The working directory to execute the command in (optional)
            shell: Whether to use shell execution (default: False)

        Returns:
            Dictionary containing:
                - returncode: Exit code of the command
                - stdout: Standard output
                - stderr: Standard error
                - success: Boolean indicating if command succeeded

        Examples:
            >>> tool = CommandTool()
            >>> result = tool.execute_command("npm install")
            >>> print(result["success"])

            >>> result = tool.execute_command("ls -la", cwd="/home/user")
            >>> print(result["stdout"])

            >>> result = tool.execute_command("echo $HOME", shell=True)
            >>> print(result["stdout"])
        """
        try:
            # Parse command into list if it's a string and shell is False
            if isinstance(command, str) and not shell:
                cmd_list = command.split()
            else:
                cmd_list = command

            # Execute the command
            result = subprocess.run(
                cmd_list,
                cwd=cwd,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            return CommandOutput(
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                success=result.returncode == 0,
            )

        except subprocess.TimeoutExpired:
            return CommandOutput(
                returncode=-1,
                stdout="",
                stderr=f"Command execution timed out after {self.timeout} seconds",
                success=False,
            )
        except Exception as e:
            return CommandOutput(
                returncode=-1,
                stdout="",
                stderr=f"Error executing command: {str(e)}",
                success=False,
            )

    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate input against schema.

        Args:
            input_data: Input dictionary to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(input_data, dict):
            return False, "Input must be a dictionary"

        if "command" not in input_data:
            return False, "Required parameter 'command' is missing"

        if not isinstance(input_data["command"], str):
            return False, "'command' must be a string"

        if "cwd" in input_data and input_data["cwd"] is not None:
            if not isinstance(input_data["cwd"], str):
                return False, "'cwd' must be a string or null"

        if "shell" in input_data:
            if not isinstance(input_data["shell"], bool):
                return False, "'shell' must be a boolean"

        return True, ""
