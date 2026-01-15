import pytest
import tempfile
import os
import json
from pathlib import Path
from backend.services.tool.file_tool import FileTool


class TestFileToolWrite:
    """Test cases for FileTool write operations."""

    @pytest.fixture
    def file_tool(self):
        """Create a FileTool instance for testing."""
        return FileTool()

    def test_write_file_basic(self, file_tool):
        """Test basic file writing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.tsx")
            content = "export const App = () => { return <div>Hello</div>; };"

            result = file_tool.write_file(file_path, content)

            assert result["success"] is True
            assert result["bytes_written"] > 0
            assert os.path.exists(file_path)
            with open(file_path) as f:
                assert f.read() == content

    def test_write_file_create_directories(self, file_tool):
        """Test file writing with directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "src", "components", "Button.tsx")
            content = "import React from 'react';\n\nexport const Button = () => {};"

            result = file_tool.write_file(file_path, content, create_dirs=True)

            assert result["success"] is True
            assert os.path.exists(file_path)
            with open(file_path) as f:
                assert f.read() == content

    def test_write_file_append_mode(self, file_tool):
        """Test file writing in append mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "notes.md")

            # Write initial content
            result1 = file_tool.write_file(file_path, "# Title\n")
            assert result1["success"] is True

            # Append content
            result2 = file_tool.write_file(file_path, "## Section 1\n", mode="a")
            assert result2["success"] is True

            with open(file_path) as f:
                content = f.read()
                assert "# Title" in content
                assert "## Section 1" in content

    def test_write_file_overwrite_mode(self, file_tool):
        """Test file writing in overwrite mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")

            # Write initial content
            file_tool.write_file(file_path, "Original content")

            # Overwrite with new content
            result = file_tool.write_file(file_path, "New content", mode="w")
            assert result["success"] is True

            with open(file_path) as f:
                assert f.read() == "New content"

    def test_write_file_invalid_path(self, file_tool):
        """Test file writing with invalid path."""
        result = file_tool.write_file("", "content")
        assert result["success"] is False
        assert "Invalid file path" in result["message"]

    def test_write_file_invalid_content(self, file_tool):
        """Test file writing with invalid content."""
        result = file_tool.write_file("test.txt", "")
        assert result["success"] is False
        assert "Invalid content" in result["message"]

    def test_write_file_invalid_mode(self, file_tool):
        """Test file writing with invalid mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            result = file_tool.write_file(file_path, "content", mode="x")

            assert result["success"] is False
            assert "Invalid mode" in result["message"]

    def test_write_file_unsupported_extension(self, file_tool):
        """Test file writing with unsupported file extension."""
        result = file_tool.write_file("test.exe", "content")
        assert result["success"] is False
        assert "not allowed" in result["message"]

    def test_write_file_with_unicode(self, file_tool):
        """Test file writing with Unicode content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "unicode.md")
            content = "# Hello 你好 مرحبا\n\nEmojis: 🚀 🎉 ✨"

            result = file_tool.write_file(file_path, content)

            assert result["success"] is True
            with open(file_path, encoding="utf-8") as f:
                assert f.read() == content

    def test_write_file_multiline_content(self, file_tool):
        """Test file writing with multiline content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "component.tsx")
            content = """import React from 'react';

export const MyComponent: React.FC = () => {
  return (
    <div className="container">
      <h1>Hello World</h1>
      <p>This is a multiline component</p>
    </div>
  );
};"""

            result = file_tool.write_file(file_path, content)

            assert result["success"] is True
            with open(file_path) as f:
                assert f.read() == content


class TestFileToolRead:
    """Test cases for FileTool read operations."""

    @pytest.fixture
    def file_tool(self):
        """Create a FileTool instance for testing."""
        return FileTool()

    def test_read_file_basic(self, file_tool):
        """Test basic file reading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.tsx")
            content = "export const App = () => {};"
            with open(file_path, "w") as f:
                f.write(content)

            result = file_tool.read_file(file_path)

            assert result["success"] is True
            assert content in result["message"]

    def test_read_file_not_found(self, file_tool):
        """Test reading non-existent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "nonexistent.txt")
            result = file_tool.read_file(file_path)

            assert result["success"] is False
            assert "not found" in result["message"]

    def test_read_file_invalid_path(self, file_tool):
        """Test reading with invalid path."""
        result = file_tool.read_file("")
        assert result["success"] is False

    def test_read_file_with_unicode(self, file_tool):
        """Test reading file with Unicode content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "unicode.md")
            content = "# 你好世界\n🚀 Rocket"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            result = file_tool.read_file(file_path)

            assert result["success"] is True
            assert "你好世界" in result["message"]
            assert "🚀" in result["message"]


class TestFileToolDelete:
    """Test cases for FileTool delete operations."""

    @pytest.fixture
    def file_tool(self):
        """Create a FileTool instance for testing."""
        return FileTool()

    def test_delete_file_basic(self, file_tool):
        """Test basic file deletion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            with open(file_path, "w") as f:
                f.write("content")

            result = file_tool.delete_file(file_path)

            assert result["success"] is True
            assert not os.path.exists(file_path)

    def test_delete_file_not_found(self, file_tool):
        """Test deleting non-existent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "nonexistent.txt")
            result = file_tool.delete_file(file_path)

            assert result["success"] is False
            assert "not found" in result["message"]

    def test_delete_file_invalid_path(self, file_tool):
        """Test deletion with invalid path."""
        result = file_tool.delete_file("")
        assert result["success"] is False


class TestFileToolWithAllowedDirs:
    """Test cases for FileTool with allowed directories restriction."""

    def test_write_file_allowed_directory(self):
        """Test file writing in allowed directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_tool = FileTool(allowed_dirs=[tmpdir])
            file_path = os.path.join(tmpdir, "test.txt")

            result = file_tool.write_file(file_path, "content")

            assert result["success"] is True

    def test_write_file_restricted_directory(self):
        """Test file writing in restricted directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_tool = FileTool(allowed_dirs=["/some/allowed/path"])
            file_path = os.path.join(tmpdir, "test.txt")

            result = file_tool.write_file(file_path, "content")

            assert result["success"] is False
            assert "not in allowed directories" in result["message"]


class TestFileToolEdgeCases:
    """Test cases for FileTool edge cases."""

    @pytest.fixture
    def file_tool(self):
        """Create a FileTool instance for testing."""
        return FileTool()

    def test_write_file_with_special_characters(self, file_tool):
        """Test file writing with special characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "special.tsx")
            content = "const str = `Template ${variable} string`;\nconst obj = { key: 'value' };"

            result = file_tool.write_file(file_path, content)

            assert result["success"] is True
            with open(file_path) as f:
                assert f.read() == content

    def test_write_file_large_content(self, file_tool):
        """Test file writing with large content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "large.txt")
            # Create content of ~1MB
            content = "x" * (1024 * 1024)

            result = file_tool.write_file(file_path, content)

            assert result["success"] is True
            assert os.path.getsize(file_path) >= 1024 * 1024

    def test_write_file_empty_directory_path(self, file_tool):
        """Test file writing with nested empty directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "a", "b", "c", "d", "file.txt")

            result = file_tool.write_file(file_path, "content", create_dirs=True)

            assert result["success"] is True
            assert os.path.exists(file_path)

    def test_write_file_json_content(self, file_tool):
        """Test file writing with JSON content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "config.json")
            content = json.dumps(
                {"name": "project", "version": "1.0.0", "features": ["A", "B"]},
                indent=2,
            )

            result = file_tool.write_file(file_path, content)

            assert result["success"] is True
            with open(file_path) as f:
                loaded = json.load(f)
                assert loaded["name"] == "project"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
