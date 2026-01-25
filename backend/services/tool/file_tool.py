import os
import logging
from typing import Optional, Dict, Any, TypedDict

logger = logging.getLogger(__name__)


class FileInput(TypedDict, total=False):
    """Input schema for FileTool."""

    file_path: str  # Required: The file path to write to
    content: str  # Required: The content to write
    mode: str  # Optional: 'w' (overwrite), 'a' (append), default: 'w'
    create_dirs: bool  # Optional: Create parent directories if they don't exist


class FileOutput(TypedDict):
    """Output schema for FileTool."""

    success: bool  # Whether the operation was successful
    file_path: str  # The file path that was written to
    bytes_written: int  # Number of bytes written
    message: str  # Success or error message


class FileTool:
    """
    Tool for reading, writing, and managing files.

    This tool allows creating, updating, and reading files with comprehensive
    error handling and validation.
    """

    # Tool Metadata
    TOOL_NAME = "file_executor"
    TOOL_VERSION = "1.0.0"
    TOOL_DESCRIPTION = (
        "Read, write, and manage files. Can create new files, append content, "
        "and read existing files with proper error handling."
    )
    TOOL_CATEGORY = "file_management"

    # Tool Schema for Writing
    WRITE_INPUT_SCHEMA = {
        "type": "object",
        "title": "FileWriteInput",
        "description": "Input parameters for file write operation",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to write (e.g., '/path/to/file.tsx', './src/components/Button.tsx')",
                "examples": [
                    "/Users/vimalmenon/code/project/src/file.tsx",
                    "./src/components/Header.tsx",
                ],
            },
            "content": {
                "type": "string",
                "description": "The content to write to the file",
                "examples": [
                    "import React from 'react';",
                    "export const MyComponent = () => { return <div>Hello</div>; };",
                ],
            },
            "mode": {
                "type": "string",
                "description": "Write mode: 'w' to overwrite (default), 'a' to append",
                "enum": ["w", "a"],
                "examples": ["w", "a"],
            },
            "create_dirs": {
                "type": "boolean",
                "description": "Create parent directories if they don't exist (default: true)",
                "examples": [True, False],
            },
        },
        "required": ["file_path", "content"],
    }

    # Tool Schema for Reading
    READ_INPUT_SCHEMA = {
        "type": "object",
        "title": "FileReadInput",
        "description": "Input parameters for file read operation",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to read",
                "examples": ["/path/to/file.tsx", "./src/components/Button.tsx"],
            },
        },
        "required": ["file_path"],
    }

    OUTPUT_SCHEMA = {
        "type": "object",
        "title": "FileToolOutput",
        "description": "Result of file operation",
        "properties": {
            "success": {
                "type": "boolean",
                "description": "Whether the operation was successful",
            },
            "file_path": {
                "type": "string",
                "description": "The file path that was operated on",
            },
            "bytes_written": {
                "type": "integer",
                "description": "Number of bytes written (for write operations)",
            },
            "message": {
                "type": "string",
                "description": "Success or error message",
            },
        },
        "required": ["success", "file_path", "message"],
    }

    # Configuration
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS = {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".html",
        ".css",
        ".scss",
        ".json",
        ".md",
        ".txt",
        ".yml",
        ".yaml",
        ".xml",
    }

    def __init__(self, allowed_dirs: Optional[list] = None):
        """
        Initialize FileTool.

        Args:
            allowed_dirs: List of allowed directories for file operations (optional)
        """
        self.allowed_dirs = allowed_dirs or []
        logger.info(f"FileTool initialized with allowed dirs: {allowed_dirs}")

    def get_write_tool_definition(self) -> Dict[str, Any]:
        """
        Get complete tool definition for file writing.

        Returns:
            Dictionary with full tool definition for writing files
        """
        return {
            "name": "file_writer",
            "version": self.TOOL_VERSION,
            "description": "Write or append content to a file. Use 'mode' parameter: 'w' to overwrite, 'a' to append.",
            "category": self.TOOL_CATEGORY,
            "operation": "write",
            "inputSchema": self.WRITE_INPUT_SCHEMA,
            "outputSchema": self.OUTPUT_SCHEMA,
            "examples": [
                {
                    "name": "Create a React component",
                    "input": {
                        "file_path": "./src/components/Button.tsx",
                        "content": "import React from 'react';\n\nexport const Button = () => {\n  return <button>Click me</button>;\n};",
                        "mode": "w",
                        "create_dirs": True,
                    },
                    "output": {
                        "success": True,
                        "file_path": "./src/components/Button.tsx",
                        "bytes_written": 87,
                        "message": "File written successfully",
                    },
                },
                {
                    "name": "Append to a file",
                    "input": {
                        "file_path": "./notes.md",
                        "content": "\n## New Section\nAdditional content",
                        "mode": "a",
                    },
                    "output": {
                        "success": True,
                        "file_path": "./notes.md",
                        "bytes_written": 32,
                        "message": "Content appended successfully",
                    },
                },
            ],
        }

    def get_read_tool_definition(self) -> Dict[str, Any]:
        """
        Get complete tool definition for file reading.

        Returns:
            Dictionary with full tool definition for reading files
        """
        return {
            "name": "file_reader",
            "version": self.TOOL_VERSION,
            "description": "Read the entire content of a file. Provide the absolute file path.",
            "category": self.TOOL_CATEGORY,
            "operation": "read",
            "inputSchema": self.READ_INPUT_SCHEMA,
            "outputSchema": self.OUTPUT_SCHEMA,
            "examples": [
                {
                    "name": "Read a TypeScript file",
                    "input": {"file_path": "./src/components/Button.tsx"},
                    "output": {
                        "success": True,
                        "file_path": "./src/components/Button.tsx",
                        "message": "File read successfully\n\nimport React from 'react';\n...",
                    },
                },
            ],
        }

    def get_delete_tool_definition(self) -> Dict[str, Any]:
        """
        Get complete tool definition for file deletion.

        Returns:
            Dictionary with full tool definition for deleting files
        """
        return {
            "name": "file_deleter",
            "version": self.TOOL_VERSION,
            "description": "Delete a file permanently. Provide the absolute file path.",
            "category": self.TOOL_CATEGORY,
            "operation": "delete",
            "inputSchema": self.READ_INPUT_SCHEMA,  # Same as read - only needs file_path
            "outputSchema": self.OUTPUT_SCHEMA,
            "examples": [
                {
                    "name": "Delete a file",
                    "input": {"file_path": "./src/temp.tsx"},
                    "output": {
                        "success": True,
                        "file_path": "./src/temp.tsx",
                        "message": "File deleted successfully",
                    },
                },
            ],
        }

    def _is_path_allowed(self, file_path: str) -> bool:
        """
        Check if the file path is in an allowed directory.

        Args:
            file_path: The file path to check

        Returns:
            True if allowed, False otherwise
        """
        if not self.allowed_dirs:
            return True

        abs_path = os.path.abspath(file_path)
        return any(abs_path.startswith(allowed) for allowed in self.allowed_dirs)

    def _validate_file_path(self, file_path: str) -> tuple[bool, Optional[str]]:
        """
        Validate the file path for security and integrity.

        Args:
            file_path: The file path to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_path or not isinstance(file_path, str):
            return False, "File path must be a non-empty string"

        # Check for path traversal attacks
        if ".." in file_path:
            return False, "Path traversal is not allowed"

        # Check allowed directories
        if not self._is_path_allowed(file_path):
            return (
                False,
                f"File path is not in allowed directories: {self.allowed_dirs}",
            )

        # Check file extension
        _, ext = os.path.splitext(file_path)
        if ext and ext not in self.ALLOWED_EXTENSIONS:
            return (
                False,
                f"File extension '{ext}' is not allowed. Allowed: {self.ALLOWED_EXTENSIONS}",
            )

        return True, None

    def write_file(
        self, file_path: str, content: str, mode: str = "w", create_dirs: bool = True
    ) -> FileOutput:
        """
        Write content to a file.

        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            mode: 'w' for overwrite (default), 'a' for append
            create_dirs: Create parent directories if they don't exist (default: True)

        Returns:
            Dictionary containing operation result

        Examples:
            >>> tool = FileTool()
            >>> result = tool.write_file('./src/app.tsx', 'export const App = () => {...}')
            >>> print(result['success'])
            True

            >>> result = tool.write_file('./notes.md', '\nNew note', mode='a')
            >>> print(result['message'])
            Content appended successfully
        """
        # Validate inputs
        if not file_path or not isinstance(file_path, str):
            return FileOutput(
                success=False,
                file_path=file_path or "unknown",
                bytes_written=0,
                message="Invalid file path: must be a non-empty string",
            )

        if not content or not isinstance(content, str):
            return FileOutput(
                success=False,
                file_path=file_path,
                bytes_written=0,
                message="Invalid content: must be a non-empty string",
            )

        if mode not in ["w", "a"]:
            return FileOutput(
                success=False,
                file_path=file_path,
                bytes_written=0,
                message=f"Invalid mode: '{mode}'. Must be 'w' (write) or 'a' (append)",
            )

        # Validate file path
        is_valid, error_msg = self._validate_file_path(file_path)
        if not is_valid:
            return FileOutput(
                success=False,
                file_path=file_path,
                bytes_written=0,
                message=f"Path validation failed: {error_msg}",
            )

        # Check content size
        content_size = len(content.encode("utf-8"))
        if content_size > self.MAX_FILE_SIZE:
            return FileOutput(
                success=False,
                file_path=file_path,
                bytes_written=0,
                message=f"Content too large: {content_size} bytes exceeds limit of {self.MAX_FILE_SIZE}",
            )

        try:
            # Expand user path
            expanded_path = os.path.expanduser(file_path)

            # Create parent directories if needed
            if create_dirs:
                parent_dir = os.path.dirname(expanded_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)
                    logger.info(f"Created directories: {parent_dir}")

            # Write or append to file
            with open(expanded_path, mode, encoding="utf-8") as f:
                bytes_written = f.write(content)

            logger.info(
                f"File '{expanded_path}' written successfully ({bytes_written} bytes, mode='{mode}')"
            )

            action = "appended to" if mode == "a" else "written to"
            return FileOutput(
                success=True,
                file_path=expanded_path,
                bytes_written=bytes_written,
                message=f"Content {action} file '{expanded_path}' successfully ({bytes_written} bytes)",
            )

        except PermissionError as e:
            error_msg = f"Permission denied when writing to '{file_path}': {str(e)}"
            logger.error(error_msg)
            return FileOutput(
                success=False,
                file_path=file_path,
                bytes_written=0,
                message=error_msg,
            )
        except FileNotFoundError as e:
            error_msg = f"Parent directory not found for '{file_path}': {str(e)}"
            logger.error(error_msg)
            return FileOutput(
                success=False,
                file_path=file_path,
                bytes_written=0,
                message=error_msg,
            )
        except Exception as e:
            error_msg = f"Unexpected error writing to file '{file_path}': {str(e)}"
            logger.error(error_msg)
            return FileOutput(
                success=False,
                file_path=file_path,
                bytes_written=0,
                message=error_msg,
            )

    def read_file(self, file_path: str) -> FileOutput:
        """
        Read content from a file.

        Args:
            file_path: Path to the file to read

        Returns:
            Dictionary containing file content and operation result

        Examples:
            >>> tool = FileTool()
            >>> result = tool.read_file('./src/app.tsx')
            >>> print(result['success'])
            True
            >>> print(result['message'])  # Contains the file content
        """
        # Validate inputs
        if not file_path or not isinstance(file_path, str):
            return FileOutput(
                success=False,
                file_path=file_path or "unknown",
                bytes_written=0,
                message="Invalid file path: must be a non-empty string",
            )

        # Validate file path
        is_valid, error_msg = self._validate_file_path(file_path)
        if not is_valid:
            return FileOutput(
                success=False,
                file_path=file_path,
                bytes_written=0,
                message=f"Path validation failed: {error_msg}",
            )

        try:
            # Expand user path
            expanded_path = os.path.expanduser(file_path)

            # Check if file exists
            if not os.path.exists(expanded_path):
                return FileOutput(
                    success=False,
                    file_path=file_path,
                    bytes_written=0,
                    message=f"File not found: '{expanded_path}'",
                )

            # Check if it's a file (not a directory)
            if not os.path.isfile(expanded_path):
                return FileOutput(
                    success=False,
                    file_path=file_path,
                    bytes_written=0,
                    message=f"Path is not a file: '{expanded_path}'",
                )

            # Read file
            with open(expanded_path, "r", encoding="utf-8") as f:
                content = f.read()

            bytes_read = len(content.encode("utf-8"))
            logger.info(
                f"File '{expanded_path}' read successfully ({bytes_read} bytes)"
            )

            return FileOutput(
                success=True,
                file_path=expanded_path,
                bytes_written=bytes_read,
                message=content,
            )

        except PermissionError as e:
            error_msg = f"Permission denied when reading '{file_path}': {str(e)}"
            logger.error(error_msg)
            return FileOutput(
                success=False,
                file_path=file_path,
                bytes_written=0,
                message=error_msg,
            )
        except Exception as e:
            error_msg = f"Error reading file '{file_path}': {str(e)}"
            logger.error(error_msg)
            return FileOutput(
                success=False,
                file_path=file_path,
                bytes_written=0,
                message=error_msg,
            )

    def delete_file(self, file_path: str) -> FileOutput:
        """
        Delete a file.

        Args:
            file_path: Path to the file to delete

        Returns:
            Dictionary containing operation result
        """
        # Validate inputs
        if not file_path or not isinstance(file_path, str):
            return FileOutput(
                success=False,
                file_path=file_path or "unknown",
                bytes_written=0,
                message="Invalid file path: must be a non-empty string",
            )

        # Validate file path
        is_valid, error_msg = self._validate_file_path(file_path)
        if not is_valid:
            return FileOutput(
                success=False,
                file_path=file_path,
                bytes_written=0,
                message=f"Path validation failed: {error_msg}",
            )

        try:
            # Expand user path
            expanded_path = os.path.expanduser(file_path)

            # Check if file exists
            if not os.path.exists(expanded_path):
                return FileOutput(
                    success=False,
                    file_path=file_path,
                    bytes_written=0,
                    message=f"File not found: '{expanded_path}'",
                )

            # Delete file
            os.remove(expanded_path)
            logger.info(f"File '{expanded_path}' deleted successfully")

            return FileOutput(
                success=True,
                file_path=expanded_path,
                bytes_written=0,
                message=f"File '{expanded_path}' deleted successfully",
            )

        except PermissionError as e:
            error_msg = f"Permission denied when deleting '{file_path}': {str(e)}"
            logger.error(error_msg)
            return FileOutput(
                success=False,
                file_path=file_path,
                bytes_written=0,
                message=error_msg,
            )
        except Exception as e:
            error_msg = f"Error deleting file '{file_path}': {str(e)}"
            logger.error(error_msg)
            return FileOutput(
                success=False,
                file_path=file_path,
                bytes_written=0,
                message=error_msg,
            )
