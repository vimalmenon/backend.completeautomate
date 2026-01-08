# CompleteAutomate Backend - Project Guidance

![CI](https://github.com/vimalmenon/backend.completeautomate/workflows/CI/badge.svg)

## Overview

This repository contains the backend for CompleteAutomate. It focuses on multi-agent automation workflows, job execution, AI provider integration, and AWS-backed persistence utilities.

---

## Current Project Structure

```text
backend.completeautomate/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── app.py
│   ├── config/
│   │   ├── env.py
│   │   └── logging_config.py
│   └── services/
│       ├── agent/
│       │   └── general_agent.py
│       ├── ai/
│       │   ├── deepseek_ai.py
│       │   ├── groq_ai.py
│       │   ├── open_ai.py
│       │   ├── open_router_ai.py
│       │   ├── perplexity_ai.py
│       │   └── qwen_ai.py
│       ├── aws/
│       │   ├── command_db.py
│       │   ├── dynamo_database.py
│       │   ├── s3_storage.py
│       │   ├── session.py
│       │   ├── image/
│       │   ├── task/
│       │   └── youtube/
│       ├── data/
│       ├── enum/
│       ├── exception/
│       ├── features/
│       │   ├── image_generation/
│       │   ├── text_to_speech/
│       │   └── youtube/
│       ├── jobs/
│       ├── team/
│       └── tool/
│           └── file_tool.py
├── tests/
├── logs/
├── output/
├── main.py
├── main.ipynb
├── pyproject.toml
├── tox.ini
└── Makefile
```

---

## Environment & Setup

### Requirements

- Python `>=3.13,<3.15`
- Poetry

### Install

```bash
poetry install
```

### Run Application

```bash
poetry run app
```

---

## Common Commands (Makefile)

Run all commands from repository root.

### Quick Commands

```bash
make install       # Install dependencies
make run           # Start app (poetry run app)
make check         # Run all quality checks (format, lint, type)
make fix           # Auto-fix issues (format-all)
make clean         # Cleanup caches/build artifacts
```

### Quality & Linting

```bash
make format-check  # Check formatting without changes
make format-all    # Format + autofix imports/lint (Black + Ruff + isort)
make lint          # Run Flake8 linter
make type-check    # Run Mypy type checker
make deadcode      # Find dead code using deadcode analyzer
```

### Testing

```bash
make test          # Pytest with coverage
make test-quick    # Pytest without coverage
```

---

## CI/CD

### GitHub Actions

**Workflow:** `.github/workflows/ci.yml`

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Automated Checks:**
- **Black** code formatting validation
- **Flake8** linting
- **Mypy** type checking
- **Python versions:** 3.13, 3.14

**Features:**
- Poetry dependency caching for faster runs
- Matrix strategy for multi-version testing
- Runs on Ubuntu latest

**Note:** Tests are not currently included in CI as test coverage is being developed.

---

## Key Runtime Components

### Architecture Overview

**Data Flow:**
1. Tasks are created with metadata and stored in DynamoDB
2. Jobs process tasks through stages: NEW → IN_PROGRESS → COMPLETED/FAILED
3. Results stored in DynamoDB and S3
4. Automatic cleanup of completed tasks

### Layer Descriptions

**Agent Layer** (`backend/services/agent/`)
- Multi-agent orchestration using LangChain and LangGraph
- General-purpose agent runtime for complex workflows
- Entry point: `general_agent.py`

**AI Provider Layer** (`backend/services/ai/`)
- Pluggable LLM integrations:
  - OpenAI (GPT models)
  - Anthropic (Claude)
  - Groq (fast inference)
  - DeepSeek
  - Perplexity
  - Qwen
  - xAI

**Features Layer** (`backend/services/features/`)
- Domain-specific implementations:
  - `youtube/` - YouTube API integration:
    - Get channel info (subscribers, view count, video count, branding)
    - Fetch channel community posts
    - List all videos (published, scheduled, unlisted)
    - Create community posts
    - Update video thumbnails
  - `image_generation/` - AI-powered image generation with prompt optimization
  - `text_to_speech/` - Resemble AI integration for TTS

**AWS Layer** (`backend/services/aws/`)
- **DynamoDB**: Task persistence, video metadata, channel info, image metadata
- **S3**: File storage with auto-download to `backend/output/`
  - `images/` - PNG, JPEG files
  - `json/` - JSON data files
  - `pickle/` - Serialized Python objects and credentials

**Jobs Layer** (`backend/services/jobs/`)
- Job handlers for automation:
  - Base job interface
  - Image generation jobs
  - YouTube-specific jobs (channel updates, video management)

**Team Layer** (`backend/services/team/`)
- Team-specific role implementations and templates:
  - Manager
  - Organization
  - Researcher
  - Social media manager

**Data Layer** (`backend/services/data/`)
- Serializable data models with:
  - `to_json()` - Serialize to dict
  - `to_cls()` - Deserialize from dict
  - `to_cls_from_response()` - Convert API responses
- Supported models:
  - `YouTubeChannel`, `YouTubeVideo`, `YouTubePostDBData`
  - `YouTubeChannelStats`, `YouTubeVideoStats`
  - `S3Data` (with PNG, JPEG, JSON, Pickle support)
  - `ImageData`, `TaskData`

---

## Key Features & Examples

### YouTube Automation

```python
from backend.services.features.youtube.youtube_api import YouTubeAPI
from backend.services.data.youtube import YouTubePostDBData

api = YouTubeAPI()

# Get detailed channel information
channel_info = api.get_channel_info(channel_id="UCxxxxx")
print(f"Channel: {channel_info['snippet']['title']}")
print(f"Description: {channel_info['snippet']['description']}")
print(f"Subscribers: {channel_info['statistics']['subscriberCount']}")
print(f"Total Views: {channel_info['statistics']['viewCount']}")
print(f"Video Count: {channel_info['statistics']['videoCount']}")

# Fetch channel community posts
posts: list[YouTubePostDBData] = api.get_channel_posts(
    channel_id="UCxxxxx",
    max_results=20
)

for post in posts:
    print(f"Posted: {post.published_at}")
    print(f"Text: {post.text_display}")
    print(f"Has attachments: {post.has_attachments}")
    print()

# List all videos (published, scheduled, and unlisted)
videos = api.list_all_videos(channel_id="UCxxxxx", max_results=50)
for video in videos:
    status = video['status']['privacyStatus']
    publish_date = video['snippet'].get('publishedAt', 'TBD')
    print(f"{video['snippet']['title']}")
    print(f"  Status: {status}")
    print(f"  Published: {publish_date}")
    print(f"  Views: {video['statistics'].get('viewCount', 0)}")
    print()

# Create a community post
success = api.create_text_post(
    channel_id="UCxxxxx",
    text="Check out our latest updates!"
)

# Update video thumbnail
success = api.update_thumbnail(
    video_id="xxxxx",
    thumbnail_path="/path/to/image.jpg"
)
```

### S3 Data Management

```python
from backend.services.data.s3 import S3Data
from backend.services.enum.s3 import S3ContentTypeEnum

# Auto-detect content type from filename
s3_data = S3Data(name="image.png")  # Auto-detects PNG

# Supports:
# - PNG, JPEG (images/)
# - JSON (json/)
# - Pickle (pickle/) - for serialized Python objects

print(s3_data.s3_key)          # 'images/image.png'
print(s3_data.downloaded_path)  # 'backend/output/images/image.png'
```

### Data Serialization

All data models support round-trip serialization:

```python
from backend.services.data.youtube import YouTubeChannel

# Serialize to JSON
channel_dict = channel.to_json()

# Deserialize from API response
channel = YouTubeChannel.to_cls_from_response(api_response)

# Convert back from dict
channel = YouTubeChannel.to_cls(channel_dict)
```

---

**Location:** `backend/services/tool/file_tool.py`

`FileTool` currently supports:

- `write_file(file_path, content, mode="w", create_dirs=True)`
- `read_file(file_path)`
- `delete_file(file_path)`

### Validation & Safety Behavior

- Rejects empty/invalid file paths
- Rejects path traversal (`..`)
- Supports optional allowed directory restrictions (`allowed_dirs`)
- Restricts writes to specific extensions (`.py`, `.js`, `.jsx`, `.ts`, `.tsx`, `.html`, `.css`, `.scss`, `.json`, `.md`, `.txt`, `.yml`, `.yaml`, `.xml`)
- Maximum write content size: 10 MB

### Output Contract

All operations return a dict-like `FileOutput` with:

- `success` (bool)
- `file_path` (str)
- `bytes_written` (int)
- `message` (str)

---

## Testing

- Primary tests are in `tests/`
- `tests/test_file_tool.py` covers write/read/delete behavior, allowed directory checks, and edge cases for `FileTool`

Run tests:

```bash
make test
```

---

## Development Guidelines

### Code Quality Standards

- **Type Safety**: Full type hints required (MyPy enforced in CI)
- **Formatting**: Black code style (checked in CI)
- **Linting**: Flake8 (checked in CI)
- **Imports**: isort for consistent import organization

### Before Opening a PR

1. Run `make check` to validate everything locally
2. Ensure all tests pass: `make test`
3. Fix type errors: `make type-check`
4. Auto-fix issues: `make fix`

### Pull Request Process

1. Create a feature branch from `develop`
2. Make your changes with clear commit messages
3. Run `make check` to validate
4. Push to your branch
5. All PRs automatically run:
   - Black formatting validation
   - Flake8 linting
   - Mypy type checking
   - Python 3.13 and 3.14 compatibility checks

### Best Practices

- Keep changes focused and minimal
- Use clear docstrings and type hints
- Maintain service layer boundaries (AI / AWS / jobs / team / features)
- Update data models when changing behavior
- Add serialization methods (`to_json()`, `to_cls()`) for new data models
- Prefer composition over inheritance
- Keep business logic out of data layers

### If Guide Drifts From Codebase

Treat **code and tests as source of truth**. Update this file accordingly.

---

## Recent Updates

- ✅ Added `get_channel_info()` - Fetch detailed channel statistics and metadata
- ✅ Added `list_all_videos()` - List all videos including scheduled and unlisted
- ✅ Added pickle file support to S3Data class
- ✅ Implemented `get_channel_posts()` to fetch YouTube community posts
- ✅ Set up CI/CD with GitHub Actions
- ✅ Configured code quality checks (Black, Flake8, Mypy)
- ✅ Added type hints throughout codebase

## Notes

- **Main entrypoint**: `main.py` (Poetry script: `poetry run app`)
- **Notebook experimentation**: `main.ipynb` for interactive development
- **Output directory**: `backend/output/` auto-created with subfolders for images, json, pickle
- **Task lifecycle**: NEW → IN_PROGRESS → COMPLETED/FAILED → CLEAN_UP (automatic)
- **Logging**: Comprehensive logging for S3, DynamoDB, and task operations
- **CI/CD**: All commits to `main`/`develop` run automated checks