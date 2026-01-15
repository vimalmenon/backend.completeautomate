import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from backend.services.agent.frontend_agent import FrontendAgent
from backend.services.tool.command_tool import CommandTool


class TestFrontendAgentHandleToolCall:
    """Test cases for FrontendAgent._handle_tool_call method."""

    @pytest.fixture
    def frontend_agent(self):
        """Create a FrontendAgent instance for testing."""
        with patch('backend.services.agent.frontend_agent.DeepseekAI'):
            with patch('backend.services.agent.frontend_agent.SystemPromptHelper'):
                agent = FrontendAgent()
                return agent

    def test_handle_tool_call_with_valid_command(self, frontend_agent):
        """Test tool call with a valid simple command."""
        tool_input = {
            "command": "echo 'Hello World'",
            "cwd": None,
            "shell": False
        }
        
        result = frontend_agent._handle_tool_call("command_executor", tool_input)
        result_dict = json.loads(result)
        
        assert result_dict["success"] is True
        assert "Hello World" in result_dict["stdout"]
        assert result_dict["returncode"] == 0

    def test_handle_tool_call_with_shell_operators(self, frontend_agent):
        """Test tool call with shell operators (&&, ||, |) - should auto-enable shell."""
        tool_input = {
            "command": "echo 'test' && echo 'success'",
            "cwd": None,
            "shell": False  # Not explicitly set to True
        }
        
        result = frontend_agent._handle_tool_call("command_executor", tool_input)
        result_dict = json.loads(result)
        
        assert result_dict["success"] is True
        assert "test" in result_dict["stdout"]
        assert "success" in result_dict["stdout"]

    def test_handle_tool_call_with_pipe_operator(self, frontend_agent):
        """Test tool call with pipe operator (|)."""
        tool_input = {
            "command": "echo 'hello world' | wc -w",
            "cwd": None,
            "shell": False
        }
        
        result = frontend_agent._handle_tool_call("command_executor", tool_input)
        result_dict = json.loads(result)
        
        assert result_dict["success"] is True
        assert "2" in result_dict["stdout"].strip()

    def test_handle_tool_call_with_cwd(self, frontend_agent):
        """Test tool call with custom working directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_input = {
                "command": "pwd",
                "cwd": tmpdir,
                "shell": False
            }
            
            result = frontend_agent._handle_tool_call("command_executor", tool_input)
            result_dict = json.loads(result)
            
            assert result_dict["success"] is True
            assert tmpdir in result_dict["stdout"]

    def test_handle_tool_call_with_failing_command(self, frontend_agent):
        """Test tool call with a command that fails."""
        tool_input = {
            "command": "ls /nonexistent/path",
            "cwd": None,
            "shell": False
        }
        
        result = frontend_agent._handle_tool_call("command_executor", tool_input)
        result_dict = json.loads(result)
        
        assert result_dict["success"] is False
        assert result_dict["returncode"] != 0

    def test_handle_tool_call_invalid_input_format(self, frontend_agent):
        """Test tool call with invalid input format (not a dict)."""
        result = frontend_agent._handle_tool_call("command_executor", "invalid_string")
        result_dict = json.loads(result)
        
        assert "error" in result_dict
        assert "Invalid input format" in result_dict["error"]

    def test_handle_tool_call_unknown_tool(self, frontend_agent):
        """Test tool call with unknown tool name."""
        tool_input = {"command": "echo test"}
        
        result = frontend_agent._handle_tool_call("unknown_tool", tool_input)
        result_dict = json.loads(result)
        
        assert "error" in result_dict
        assert "Unknown tool" in result_dict["error"]

    def test_handle_tool_call_with_redirection(self, frontend_agent):
        """Test tool call with output redirection (>) - requires shell."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.txt")
            tool_input = {
                "command": f"echo 'test output' > {output_file}",
                "cwd": None,
                "shell": False
            }
            
            result = frontend_agent._handle_tool_call("command_executor", tool_input)
            result_dict = json.loads(result)
            
            assert result_dict["success"] is True
            assert os.path.exists(output_file)
            with open(output_file) as f:
                assert "test output" in f.read()

    def test_handle_tool_call_with_environment_variable(self, frontend_agent):
        """Test tool call with environment variable expansion ($)."""
        tool_input = {
            "command": "echo $HOME",
            "cwd": None,
            "shell": False
        }
        
        result = frontend_agent._handle_tool_call("command_executor", tool_input)
        result_dict = json.loads(result)
        
        # With shell auto-detection, this should work
        assert result_dict["success"] is True
        assert result_dict["stdout"].strip() != ""

    def test_handle_tool_call_with_explicit_shell_true(self, frontend_agent):
        """Test tool call with explicitly set shell=True."""
        tool_input = {
            "command": "echo 'shell mode' && ls",
            "cwd": None,
            "shell": True
        }
        
        result = frontend_agent._handle_tool_call("command_executor", tool_input)
        result_dict = json.loads(result)
        
        assert result_dict["success"] is True

    def test_handle_tool_call_returns_json_string(self, frontend_agent):
        """Test that tool call result is always valid JSON string."""
        tool_input = {
            "command": "echo test",
            "cwd": None,
            "shell": False
        }
        
        result = frontend_agent._handle_tool_call("command_executor", tool_input)
        
        # Should be able to parse as JSON
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_handle_tool_call_complex_command_with_operators(self, frontend_agent):
        """Test complex command with multiple operators."""
        tool_input = {
            "command": "echo 'line1' && echo 'line2' || echo 'error'",
            "cwd": None,
            "shell": False
        }
        
        result = frontend_agent._handle_tool_call("command_executor", tool_input)
        result_dict = json.loads(result)
        
        assert result_dict["success"] is True
        assert "line1" in result_dict["stdout"]
        assert "line2" in result_dict["stdout"]

    def test_handle_tool_call_missing_command_key(self, frontend_agent):
        """Test tool call with missing required command key."""
        tool_input = {
            "cwd": None,
            "shell": False
        }
        
        result = frontend_agent._handle_tool_call("command_executor", tool_input)
        result_dict = json.loads(result)
        
        # Should handle gracefully - command_tool validates this
        assert "success" in result_dict

    def test_handle_tool_call_with_heredoc(self, frontend_agent):
        """Test tool call with heredoc syntax (cat > file << 'EOF'...EOF)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_file.tsx")
            # Heredoc syntax requires shell=True
            tool_input = {
                "command": f"cd {tmpdir} && cat > test_file.tsx << 'EOF'\nimport React from 'react';\n\nexport const TestComponent = () => {{\n  return <div>Test</div>;\n}};\nEOF",
                "cwd": None,
                "shell": False  # Should auto-detect
            }
            
            result = frontend_agent._handle_tool_call("command_executor", tool_input)
            result_dict = json.loads(result)
            
            assert result_dict["success"] is True
            assert os.path.exists(file_path)
            with open(file_path) as f:
                content = f.read()
                assert "import React" in content
                assert "TestComponent" in content

    def test_handle_tool_call_with_complex_multiline_heredoc(self, frontend_agent):
        """Test tool call with complex multi-line heredoc content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "Header.component.tsx")
            # Complex heredoc with nested quotes and special characters
            tool_input = {
                "command": f"cd {tmpdir} && cat > Header.component.tsx << 'EOF'\n'use client';\n\nimport React, {{ useEffect, useState }} from 'react';\nimport Link from 'next/link';\n\nexport const Header: React.FC = () => {{\n  const [isMenuOpen, setIsMenuOpen] = useState(false);\n  const [isSticky, setIsSticky] = useState(false);\n\n  useEffect(() => {{\n    const handleScroll = () => {{\n      setIsSticky(window.scrollY > 20);\n    }};\n    window.addEventListener('scroll', handleScroll);\n    return () => window.removeEventListener('scroll', handleScroll);\n  }}, []);\n\n  return (\n    <header className=\"fixed top-0 left-0 right-0 w-full z-50\">\n      <nav>\n        <div className=\"flex items-center\">\n          <Link href=\"/\">CompleteAutomate</Link>\n        </div>\n      </nav>\n    </header>\n  );\n}};\nEOF",
                "cwd": None,
                "shell": False
            }
            
            result = frontend_agent._handle_tool_call("command_executor", tool_input)
            result_dict = json.loads(result)
            
            assert result_dict["success"] is True
            assert os.path.exists(file_path)
            with open(file_path) as f:
                content = f.read()
                assert "'use client';" in content
                assert "export const Header" in content
                assert "useEffect" in content
                assert "handleScroll" in content
                assert "CompleteAutomate" in content

    def test_handle_tool_call_with_chained_commands_and_heredoc(self, frontend_agent):
        """Test tool call with chained cd && cat > file << EOF pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "src", "components")
            os.makedirs(subdir, exist_ok=True)
            file_path = os.path.join(subdir, "Button.tsx")
            
            tool_input = {
                "command": f"cd {subdir} && cat > Button.tsx << 'EOF'\nimport React from 'react';\n\ninterface ButtonProps {{\n  label: string;\n  onClick: () => void;\n}}\n\nexport const Button: React.FC<ButtonProps> = ({{ label, onClick }}) => {{\n  return (\n    <button onClick={{onClick}} className=\"px-4 py-2 bg-blue-600 text-white rounded\">\n      {{label}}\n    </button>\n  );\n}};\nEOF",
                "cwd": None,
                "shell": False
            }
            
            result = frontend_agent._handle_tool_call("command_executor", tool_input)
            result_dict = json.loads(result)
            
            assert result_dict["success"] is True
            assert os.path.exists(file_path)
            with open(file_path) as f:
                content = f.read()
                assert "ButtonProps" in content
                assert "onClick" in content
                assert "blue-600" in content


class TestCommandToolIntegration:
    """Integration tests for CommandTool with shell operator detection."""

    @pytest.fixture
    def command_tool(self):
        """Create a CommandTool instance for testing."""
        return CommandTool()

    def test_command_tool_basic_execution(self, command_tool):
        """Test basic command execution."""
        result = command_tool.execute_command("echo 'test'")
        
        assert result["success"] is True
        assert "test" in result["stdout"]

    def test_command_tool_with_custom_timeout(self):
        """Test CommandTool with custom timeout."""
        tool = CommandTool(timeout=10)
        result = tool.execute_command("sleep 1 && echo 'done'", shell=True)
        
        assert result["success"] is True

    def test_command_tool_validates_input(self, command_tool):
        """Test that CommandTool validates input."""
        # Test with None command
        is_valid, error_msg = command_tool.validate_input(
            {"command": None, "cwd": None, "shell": False}
        )
        
        assert is_valid is False
        assert error_msg is not None

    def test_command_tool_timeout(self):
        """Test command execution timeout."""
        # Create CommandTool with very short timeout
        tool_with_timeout = CommandTool(timeout=1)
        result = tool_with_timeout.execute_command("sleep 10", shell=False)
        # This should timeout
        assert result["success"] is False
        assert result["returncode"] == -1
        assert "timed out" in result["stderr"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
