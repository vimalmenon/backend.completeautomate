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

### SystemPromptHelper
Manages dynamic system prompts using Jinja2 template engine.

**Location:** `backend/services/helper/system_prompt/system_prompt_helper.py`

**Features:**
- Template-based prompt generation
- Role-based system prompts
- Variable substitution
- Team-aware prompts
- Message formatting

**Usage:**

```python
from backend.services.helper.system_prompt.system_prompt_helper import SystemPromptHelper
from backend.config.enum import TeamEnum

helper = SystemPromptHelper(
    role=TeamEnum.PLANNER,
    teams=[TeamEnum.BACKEND, TeamEnum.FRONTEND]
)

# Get system prompt
system_prompt = helper.get_system_prompt()

# Get system message
system_message = helper.get_system_message(
    content="You are responsible for planning tasks"
)
```

### AI Services

Multiple AI provider integrations for model inference.

**Location:** `backend/services/ai/`

**Supported Providers:**
- OpenAI (`open_ai.py`)
- DeepSeek (`deepseek_ai.py`)
- Groq (`groq_ai.py`)
- Anthropic (`anthropic_ai.py`)
- Perplexity (`perplexity_ai.py`)
- OpenRouter (`open_router_ai.py`)

**Usage:**

```python
from backend.services.ai.open_ai import OpenAI
from backend.services.ai.deepseek_ai import DeepseekAI
from langchain.messages import HumanMessage

# Initialize AI service
ai_service = DeepseekAI()
model = ai_service.get_model()

# Invoke model with messages
response = model.invoke([
    HumanMessage(content="Generate a plan for building a website")
])

print(response.content)
```

### Agent Services

Specialized agents for different roles and tasks.

**Location:** `backend/services/agent/`

**Available Agents:**
- **PlannerAgent** (`planner_agent.py`) - Plans and organizes tasks
- **BackendAgent** (`backend_agent.py`) - Backend development tasks
- **FrontendAgent** (`frontend_agent.py`) - Frontend development tasks
- **GraphicDesignerAgent** (`graphic_designer_agent.py`) - Design tasks
- **ResearcherAgent** (`researcher_agent.py`) - Research and information gathering
- **SocialMediaAgent** (`social_media_agent.py`) - Social media content
- **ManagerAgent** (`manager_agent.py`) - Project management

**Base Agent Class:**
All agents extend `BaseAgent` with common functionality like system prompts, model management, and tool handling.

**Usage:**

```python
from backend.services.agent.planner_agent import PlannerAgent

agent = PlannerAgent()
result = agent.start_task(
    task="Break down the website project into tasks",
    max_retries=3
)
```

### AWS Services

Cloud integration with AWS services.

**Location:** `backend/services/aws/`

**Services:**
- **DynamoDB** (`dynamo_database.py`) - Database operations
- **MessageDB** (`message_db.py`) - Message storage and retrieval
- **TaskDB** (`task_db.py`) - Task management with PlannedTaskOutput
- **S3Storage** (`s3_storage.py`) - File storage
- **SecretManager** (`secret.py`) - Secret management
- **SessionManager** (`session.py`) - Session handling

**Usage:**

```python
from backend.services.aws.task_db import TaskDB, Task, StatusLevel, PriorityLevel
from backend.services.aws.message_db import MessageDB
from uuid import UUID

# Task Database
task_db = TaskDB()

# Get all tasks
tasks = task_db.get_tasks()

# Get specific task
task = task_db.get_task_by_id(UUID("task-id"))

# Save tasks
task_db.save_tasks(tasks)

# Message Database
msg_db = MessageDB()
messages = msg_db.query_messages()
```

### FileTool Service

File system operations and management.

**Location:** `backend/services/tool/file_tool.py`

**Features:**
- Read files
- Write files
- Delete files
- Directory operations
- File validation

**Usage:**

```python
from backend.services.tool.file_tool import FileTool

file_tool = FileTool()

# Read file
content = file_tool.read_file("path/to/file.txt")

# Write file
file_tool.write_file("path/to/file.txt", "content")

# Delete file
file_tool.delete_file("path/to/file.txt")
```

### InternetTool Service

Web browsing and internet operations.

**Location:** `backend/services/tool/internet_tool.py`

**Features:**
- Web searches
- Page fetching
- Content retrieval

**Usage:**

```python
from backend.services.tool.internet_tool import InternetTool

internet_tool = InternetTool()

# Search the web
results = internet_tool.search("query")

# Fetch page content
content = internet_tool.fetch_page("url")
```

### Task Services

Task management and execution.

**Location:** `backend/services/task/`

**Task Types:**
- **PendingTask** (`pending_task.py`) - Manage pending tasks
- **StartNewTask** (`start_new_task.py`) - Start new task execution
- **NewIdeaTask** (`new_idea_task.py`) - Create and process new ideas
- **HumanInputTask** (`human_input_task.py`) - Request human input/confirmation

**Usage:**

```python
from backend.services.task.new_idea_task import NewIdeaTask
from backend.config.enum import TeamEnum

# Create and process new idea
idea_task = NewIdeaTask(team=TeamEnum.PLANNER)
result = idea_task.input(
    task="Describe what you want to build"
)
```

### Text-to-Speech Service

Audio generation from text.

**Location:** `backend/services/text_to_speech/resemble_service.py`

**Features:**
- Text to speech conversion
- Multiple voice options
- Audio file generation

**Usage:**

```python
from backend.services.text_to_speech.resemble_service import ResembleService

tts = ResembleService()
audio_url = tts.generate_speech("Hello, this is a test message")
```

### Configuration & Enums

**Location:** `backend/config/`

**Components:**
- **Env** (`env.py`) - Environment variables using Pydantic
- **Enums** (`enum.py`) - Team roles, status levels, priority levels

**Usage:**

```python
from backend.config.env import env
from backend.config.enum import TeamEnum

# Access environment variables (as SecretStr)
api_key = env.OPENAI_API_KEY.get_secret_value()

# Use enums
team = TeamEnum.PLANNER
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
