import subprocess
from typing import Optional


class CommandTool:

    def execute_command(
        self, command: str, cwd: Optional[str] = None, shell: bool = False
    ) -> dict:
        """
        Execute a command and return the result.

        Args:
            command: The command to execute (string or list)
            cwd: The working directory to execute the command in
            shell: Whether to use shell execution

        Returns:
            Dictionary containing:
                - returncode: Exit code of the command
                - stdout: Standard output
                - stderr: Standard error
                - success: Boolean indicating if command succeeded
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
                timeout=300,  # 5 minute timeout
            )

            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }

        except subprocess.TimeoutExpired:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": "Command execution timed out",
                "success": False,
            }
        except Exception as e:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False,
            }
