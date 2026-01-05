# CompleteAutomate Backend - Project Guidance

## Overview

This is the backend service for CompleteAutomate - a Python-based automation platform providing core services, tool execution, and system utilities.

---

## Project Structure

```
backend.completeautomate/
├── backend/
│   ├── __init__.py
│   ├── services/                # Core service modules
│   │   ├── tool/               # Tool execution services
│   │   │   ├── command_tool.py # Execute shell commands
│   │   │   └── __init__.py
│   │   └── utility/            # Utility functions
│   │       ├── system_prompt_utility.py  # System prompt management
│   │       └── __init__.py
│   └── __init__.py
├── main.py                      # Application entry point
├── pyproject.toml              # Project metadata and dependencies
├── README.md                   # Project documentation
└── notes.txt                   # Development notes
```

---

## Setup & Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Environment Setup

```bash
cd backend.completeautomate

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -e .
# or
pip install -r requirements.txt
```

### Deactivating Virtual Environment

```bash
deactivate
```

---

## Key Components & Services

### CommandTool Service
Executes shell commands in specified directories with output capture and error handling.

**Location:** `backend/services/tool/command_tool.py`

**Features:**
- Execute commands with custom working directory
- Optional shell execution mode
- 5-minute timeout protection
- Returns exit code, stdout, stderr, and success flag
- Comprehensive error handling

**Usage:**

```python
from backend.services.tool.command_tool import CommandTool

tool = CommandTool()

# Execute a simple command
result = tool.execute_command("npm install")

# Execute in a specific directory
result = tool.execute_command(
    command="npm install",
    cwd="/path/to/project"
)

# Execute using shell (for complex commands)
result = tool.execute_command(
    command="echo $PATH && ls -la",
    shell=True
)

# Check results
if result["success"]:
    print("Command output:", result["stdout"])
else:
    print("Command error:", result["stderr"])
    print("Exit code:", result["returncode"])
```

**Return Format:**
```python
{
    "returncode": int,      # Exit code (0 = success)
    "stdout": str,          # Standard output
    "stderr": str,          # Error output
    "success": bool         # Whether command succeeded
}
```

**Parameters:**
- `command` (str): Command to execute
- `cwd` (str, optional): Working directory for execution
- `shell` (bool, optional): Use shell execution (default: False)

### SystemPromptUtility
Manages dynamic system prompts using Jinja2 template engine.

**Location:** `backend/services/utility/system_prompt_utility.py`

**Features:**
- Template-based prompt generation
- Variable substitution
- Filter support (uppercase, join, etc.)
- Easy customization

**Usage:**

```python
from jinja2 import Template

# Create a template
template = Template("""
You are a {{ role }} assistant.
Task: {{ task }}
Available tools: {{ tools | join(', ') }}
""")

# Render with variables
output = template.render(
    role="Python expert",
    task="help with code",
    tools=["execute_command", "analyze_code", "suggest_improvements"]
)

print(output)
```

**Common Jinja2 Features:**

```jinja2
{# Variables #}
Hello {{ name }}!

{# Filters #}
{{ message | upper }}
{{ items | length }}
{{ items | join(', ') }}

{# Conditionals #}
{% if user %}
  Welcome {{ user }}!
{% endif %}

{# Loops #}
{% for item in items %}
  - {{ item }}
{% endfor %}

{# Comments #}
{# This is a comment #}
```

---

## Development Guidelines

### Best Practices

- **Create a new branch** for each feature: `git checkout -b feature/your-feature`
- **Follow PEP 8** conventions for Python code
- **Write docstrings** for all functions and classes
- **Type hints** for function parameters and returns
- **Test locally** before pushing changes
- **Write descriptive commit messages** explaining what and why
- **Handle exceptions** properly with meaningful error messages

### Code Style

```python
# Good example
def execute_command(command: str, cwd: Optional[str] = None) -> dict:
    """
    Execute a shell command.
    
    Args:
        command: The command to execute
        cwd: Working directory (optional)
    
    Returns:
        Dictionary with result details
    """
    try:
        # Implementation
        pass
    except Exception as e:
        # Handle error
        pass
```

### Type Hints

Use type hints for all function signatures:

```python
from typing import Optional, List, Dict

def process_items(items: List[str], filter_val: Optional[str] = None) -> Dict[str, int]:
    """Process items and return counts."""
    pass
```

---

## Common Workflows

### Creating a New Service

1. Create a new directory under `backend/services/`
2. Create service file with class definition
3. Add `__init__.py` for exports
4. Import and use in main application

```python
# backend/services/my_service/my_service.py
from typing import Optional

class MyService:
    """Service description."""
    
    def process(self, data: str) -> dict:
        """Process data and return result."""
        try:
            result = self._do_something(data)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _do_something(self, data: str) -> str:
        """Helper method."""
        return data.upper()
```

```python
# backend/services/my_service/__init__.py
from .my_service import MyService

__all__ = ["MyService"]
```

### Adding Dependencies

1. Edit `pyproject.toml` or `requirements.txt`
2. Install in virtual environment
3. Commit changes

```bash
# Install a package
pip install package_name

# Generate requirements file
pip freeze > requirements.txt
```

### Testing Your Code

```python
# Simple test
if __name__ == "__main__":
    from backend.services.tool.command_tool import CommandTool
    
    tool = CommandTool()
    result = tool.execute_command("echo 'Hello World'")
    print(result)
```

---

## Useful Commands

### Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows

# Deactivate
deactivate

# Remove
rm -rf venv
```

### Package Management
```bash
# Install in development mode
pip install -e .

# Install dependencies
pip install -r requirements.txt

# Install specific package
pip install package_name

# Update package
pip install --upgrade package_name

# List installed packages
pip list

# Generate requirements file
pip freeze > requirements.txt
```

### Running Code
```bash
# Run main application
python main.py

# Run a specific module
python -m backend.services.tool.command_tool

# Interactive Python shell
python
```

### Git Operations
```bash
# Create and switch to branch
git checkout -b feature/your-feature

# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Add feature description"

# Push to remote
git push origin feature/your-feature
```

---

## Development Tips

### Environment Variables

Create a `.env` file for local configuration:

```
DEBUG=True
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///local.db
```

Load in your code:
```python
import os
from dotenv import load_dotenv

load_dotenv()
debug_mode = os.getenv("DEBUG", "False") == "True"
```

### Debugging

Use Python's built-in debugger:

```python
import pdb

def my_function():
    x = 10
    pdb.set_trace()  # Execution will pause here
    return x
```

Or use print statements:
```python
print(f"Debug: variable={variable}, type={type(variable)}")
```

### Performance

- Use efficient algorithms
- Cache repeated computations
- Use generators for large datasets
- Profile code with `cProfile` module

```python
import cProfile

cProfile.run('my_function()')
```

### Logging

Add logging instead of print statements:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Processing started")
logger.error("An error occurred", exc_info=True)
```

---

## Project Dependencies

Common packages used:

- **subprocess**: Running shell commands (built-in)
- **Jinja2**: Template engine for dynamic prompts
- **python-dotenv**: Environment variable management

Install all dependencies:
```bash
pip install -e .
```

---

## Resources & Links

- [Python Documentation](https://docs.python.org/3/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Type Hints Documentation](https://docs.python.org/3/library/typing.html)
- [subprocess Module](https://docs.python.org/3/library/subprocess.html)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

---

## Troubleshooting

### Virtual Environment Issues

**Problem:** Python not found after activating venv
```bash
# Deactivate and reactivate
deactivate
source venv/bin/activate

# Or remove and recreate
rm -rf venv
python -m venv venv
source venv/bin/activate
```

### Module Import Errors

**Problem:** `ModuleNotFoundError: No module named 'backend'`

```bash
# Make sure you're installing in development mode
pip install -e .

# Check that __init__.py files exist in all directories
ls backend/__init__.py
ls backend/services/__init__.py
```

### Dependency Conflicts

**Problem:** Package conflicts or version issues

```bash
# Clear cache and reinstall
pip cache purge
pip install --force-reinstall -e .

# Or create fresh environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Command Timeout

**Problem:** Commands taking too long

The `CommandTool` has a 5-minute timeout by default. For longer operations:
- Break command into smaller chunks
- Increase timeout in code (modify `command_tool.py`)
- Run in background process

---

## Contributing

### Important Rules

⚠️ **NEVER commit directly to the main branch**
- All work must be done on feature branches
- Main branch should only be updated through pull requests
- Use feature branches: `feature/your-feature` or `fix/bug-fix`

### Workflow

1. Ensure you're on main and up to date: `git checkout main && git pull origin main`
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes following PEP 8
4. Add docstrings and type hints
5. Test thoroughly
6. Commit with clear messages: `git commit -m "Add feature description"`
7. Push: `git push origin feature/your-feature`
8. Create a pull request with description of changes
9. Request review from team members
10. Ensure all checks pass before merging
11. Delete feature branch after merge: `git branch -d feature/your-feature`

### Branch Naming Conventions

- `feature/feature-name` - For new features
- `fix/bug-name` - For bug fixes
- `docs/update-docs` - For documentation updates
- `refactor/refactor-name` - For refactoring code

**Example:**
```bash
# Good branch names
git checkout -b feature/add-command-executor
git checkout -b fix/timeout-issue
git checkout -b docs/update-readme

# Bad branch names
git checkout -b my-changes
git checkout -b test
git checkout -b new-feature
```

---

## License & Contact

For questions or support, reach out to the project maintainers.

Last Updated: January 2026
