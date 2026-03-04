# Complete Automate Backend

![CI](https://github.com/vimalmenon/backend.completeautomate/workflows/CI/badge.svg)
![Project Rating](https://img.shields.io/badge/Project%20Rating-7.5%2F10-yellow)

Python backend for multi-agent automation workflows, with task scheduling, YouTube automation, image generation, and a NiceGUI dashboard.

## Table of Contents

- [Highlights](#highlights)
- [Project Health](#project-health)
- [Roadmap](#roadmap)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
	- [1) Install dependencies](#1-install-dependencies)
	- [2) Configure environment](#2-configure-environment)
	- [3) Run the app](#3-run-the-app)
	- [4) Run the dashboard](#4-run-the-dashboard)
- [YouTube OAuth Notes](#youtube-oauth-notes)
- [Development Commands](#development-commands)
- [Testing](#testing)
- [Architecture Overview](#architecture-overview)
- [Project Layout](#project-layout)
- [Contributing](#contributing)

## Highlights

- Multi-agent orchestration for content and automation tasks
- Multiple LLM providers via LangChain integrations (OpenAI, Groq, DeepSeek, Perplexity, Anthropic, xAI, Qwen)
- YouTube automation (channel/video sync, transcript workflows, thumbnail updates)
- Image generation + prompt pipelines
- AWS-backed persistence (DynamoDB + S3)
- Web dashboard built with NiceGUI (`/`, `/tasks`, `/youtube`, `/prompt`)
- Tasks dashboard: add task form, inline status updates, status-colored rows, delete action, expandable payload JSON viewer
- Videos dashboard: newest-first by published date and 50-character description preview in table rows
- Prompt dashboard: expandable prompt table with task/role/model metadata
- Test suite with unit and integration markers

## Project Health

Current internal score: **7.5/10**

### What is working well

- Clear modular architecture (`ai`, `data`, `database`, `jobs`, `integration`, `ui`)
- Practical developer workflow (`Makefile`, pytest markers, lint/type checks)
- Functional NiceGUI dashboards with live task operations
- Good momentum with iterative UI improvements (status updates, row actions, sorting, JSON payload rendering)

### Improvement areas

- UI page logic has grown and can be further componentize
- Some runtime configuration is still tightly coupled to environment setup
- Need stronger end-to-end GUI flow validation for confidence in regressions

### Gradual Improvement Tracker

Use this checklist to track progress toward a **9/10** quality target.

- [ ] Extract shared reusable table utilities/components for `tasks.py`, `video.py`, and `prompt.py`
- [ ] Add explicit confirmation dialog before task deletion
- [ ] Add sorting controls in Tasks table (not just static ordering)
- [ ] Add field-level payload templates/validators for common `JobEnum` task types
- [ ] Add page-level error states for missing env/config with actionable guidance
- [ ] Add UI smoke tests for core flows (create/update/delete task, expand details, load prompt/video pages)
- [ ] Add CI job for GUI smoke test execution
- [ ] Reduce complex UI functions further and standardize helper naming across pages

### Milestone Guidance

- **8/10 target:** reusable table helpers + safer delete UX + better env error feedback
- **8.5/10 target:** payload templates/validation + task sorting controls
- **9/10 target:** GUI smoke tests integrated in CI and stable over multiple iterations

## Roadmap

<details>
<summary><b>TODO Items</b> (click to expand)</summary>


- [x] Fix tox issues
- [ ] Test if it's able to generate YouTube Title, Description and Tags with multiple options
- [ ] Test if it's able to generate good image prompts with multiple options
- [ ] Test all the prompts once done
- [ ] Need to check what this class does `PromptAnalyzerJob`
- [ ] Adding YouTubeChannel should add Video and Channel Detail (as they both use the same data)
- [ ] Add Playlist details to YouTube Video DB
- [ ] YouTube Idea Suggester
- [ ] Integrate with twitter
- [ ] Agent to review tasks
- [ ] Fix transcripts for grammar and naming errors
- [ ] Agent to analyze prompts
- [ ] Add AI review step for generated answers
- [ ] Add one-shot / few-shot prompt examples for image and other generation tasks
- [ ] Fix TODOs and dead code
- [ ] Remove `main.ipynb` (Rather use GUI to manage it)
- [ ] Mock data (use factory)
- [ ] Test Coverage
  - [ ] Mock data from Agents (Positive and Negative)
  - [ ] Test all the flows from Generator to Updater, Analyze
  - [ ] Test data for DB integration
  - [ ] Mock Integration with YouTube API
- [ ] GUI Enhancements
  - [ ] Add YouTube Channel
  - [ ] Add Platform to GUI
  - [ ] Ability to Work Offline
  - [ ] Mock AWS Dynamo DB Data
  - [ ] Mock AWS S3 data
  - [ ] Task Create or Edit
  - [ ] Analytics dashboard
  - [ ] YouTube stats graphs
  - [ ] Need to add UI for Youtube Channel
  - [ ] Need to add Graph for stats for YouTube
  - [ ] Show Graph next to Edit button to show Graph
  - [ ] Ability to perform all tasks from GUI

- Naming convention for generator
  - Updater (Update data to source)
  - Suggester (Suggest for Something)
  - Creator (Create Data on DB)
  - Analyzer (Analysis the data)
  - Generator (Generate Image / Video Sound)

### YouTube Workflow Pipeline

Task creation flows from top to bottom. Each stage is a separate scheduled job that fetches, processes, and creates the next task:

```
┌─ YouTubeChannelCreator (Initial Task)
│  ├─ Action: Fetch channel info from YouTube API
│  ├─ Store: YouTubeChannelDB
│  └─ Creates: YouTubeVideoGenerator
│
├─ YouTubeVideoGenerator (Created by ChannelCreator)
│  ├─ Action: Fetch all videos for channel
│  ├─ Store: YouTubeVideoDB
│  └─ Creates: YouTubeVideoAnalyzer
│
├─ YouTubeVideoAnalyzer (Created by VideoGenerator)
│  ├─ Action: Analyze video stats and content
│  └─ Creates: YouTubeMetadataSuggester
│
├─ YouTubeMetadataSuggester (Created by VideoAnalyzer)
│  ├─ Action: Use LLM to generate title/description/tags
│  ├─ Store: Prompt + suggestions in DB
│  └─ Creates: YouTubeMetadataUpdater (if enabled)
│
├─ YouTubeMetadataUpdater (Created by MetadataSuggester)
│  ├─ Action: Update YouTube video with suggested metadata
│  └─ Creates: ImagePromptSuggester (if thumbnail update enabled)
│
├─ ImagePromptSuggester (Created by MetadataUpdater)
│  ├─ Action: Generate image prompt from video content
│  └─ Creates: ImageGenerator
│
├─ ImageGenerator (Created by ImagePromptSuggester)
│  ├─ Action: Generate thumbnail image from prompt
│  └─ Creates: YouTubeThumbnailUpdater
│
└─ YouTubeThumbnailUpdater (Created by ImageGenerator)
   └─ Action: Upload generated thumbnail to YouTube (FINAL STEP)
```

**Key Points:**
- Start with `YouTubeChannelCreator` task via task dashboard
- Each job runs independently at scheduled intervals
- Each job can be retried or repositioned in the queue via dashboard
- Conditional task creation: some stages only create next task if specific conditions are met

**Ideas / Low Priority:**

- Add topic suggestions for next week
- Dockerfile + DockerHub CD
- Local text-to-speech
- Instagram/Twitter posting integration
- YouTube comments analysis
- Adopt GIT branching strategies
- Remove Teams as it looks of no use
- Upload Corrected Transcript
- Notify user on `REVIEW` via email or Telegram


</details>

## Requirements

- Python `>=3.13,<3.15`
- Poetry
- AWS account/resources (DynamoDB + S3)
- API keys for the providers you intend to use

## Quick Start

### 1) Install dependencies

```sh
git clone https://github.com/vimalmenon/backend.completeautomate.git
cd backend.completeautomate
poetry self add poetry-plugin-dotenv
poetry install
```

`poetry-plugin-dotenv` lets Poetry commands automatically read values from your `.env` file.

### 2) Configure environment

The app reads required variables from `backend/config/env.py`. Add them to a local `.env` (or export in your shell):

```env
VERSION=local
COMPANY_NAME=Your Company

AWS_CLIENT_ID=...
AWS_SECRET=...
AWS_REGION=us-east-1
AWS_SECRET_MANAGER=...
AWS_TABLE=...
AWS_S3_BUCKET=...
OFFLINE=false

GROQ_API_KEY=...
PPLX_API_KEY=...
OPEN_ROUTE_API_KEY=...
OPENAI_API_KEY=...
DEEPSEEK_API_KEY=...

YOUTUBE_API_KEY=...
YOUTUBE_CHANNEL_ID=...
```

Set `OFFLINE=true` to run AWS integrations against local Moto mocks (S3 + DynamoDB)
without requiring internet or real AWS credentials.

### 3) Run the app

```sh
poetry run app
```

### 4) Run the dashboard

```sh
poetry run python -m gui
```

Open: `http://localhost:8080`

Dashboard pages:

- Home: `http://localhost:8080/`
- Tasks: `http://localhost:8080/tasks`
- YouTube: `http://localhost:8080/youtube`
- Prompts: `http://localhost:8080/prompt`

## YouTube OAuth Notes

Some YouTube operations use OAuth and expect:

- `backend/output/json/client_secret.json`
- token cache written to `backend/output/pickle/token.pickle`

If no token exists, the app launches the OAuth flow on first authenticated YouTube request.

## Development Commands

Use `make help` to list all commands.

Windows note: if `make.exe` is blocked by App Control policy, run `./make.cmd <target>` (for example, `./make.cmd ci`).

```sh
make install       # Poetry install
make run           # Run scheduler (poetry run app)
make test          # Pytest + coverage
make test-quick    # Pytest without coverage
make lint          # Flake8
make type-check    # MyPy
make format        # Black (targeted paths)
make format-check  # Black check only
make isort-check   # isort check (includes main.ipynb)
make format-all    # Black + Ruff --fix + isort (project sources + main.ipynb)
make check         # format-check + isort-check + lint + type-check + test
make fix           # format-all
make deadcode      # deadcode analyzer
```

## Testing

Pytest config and markers live in `pytest.ini`.

Examples:

```sh
poetry run pytest -m unit
poetry run pytest -m integration
poetry run pytest tests/test_s3_storage.py
```

Available markers:

- `unit`
- `integration`
- `slow`
- `aws`
- `youtube`

## Architecture Overview

- `backend/task_scheduler_services.py`: scheduler loop and job routing
- `backend/jobs/`: job handlers (image, prompt, youtube, etc.)
- Fallback behavior: if a task's `job_type` has no mapped handler, scheduler uses `NoJob`, logs an error, and marks the task as `FAILED` while incrementing `failed_count`
- `backend/generator/`: workflow generators and domain logic
- `backend/services/agent_service.py`: model/prompt orchestration
- `backend/ai/`: provider adapters
- `backend/database/`: DynamoDB access layer
- `backend/integration/`: external services (YouTube, S3, image generation, TTS)
- `backend/data/`: Pydantic/domain data models
- `backend/ui/` + `gui.py`: NiceGUI pages and app entry

## Project Layout

```text
backend.completeautomate/
├── backend/
│   ├── ai/                           # LLM provider wrappers (OpenAI, Groq, DeepSeek, etc.)
│   ├── config/                       # env loading, logging setup, session config
│   ├── data/                         # Core data models (Task, Prompt, YouTube, Image, S3)
│   ├── database/                     # DynamoDB access layer and DB-specific repositories
│   │   ├── image/
│   │   ├── task/
│   │   └── youtube/
│   ├── enum/                         # Enums for job/status/team/db keys/prompt types
│   ├── exception/                    # Custom app exception types
│   ├── generator/                    # Domain generators (image/youtube/analysis/summarize)
│   ├── helper/                       # Startup + utility helpers
│   ├── integration/                  # External integrations (YouTube API, S3, TTS, agents)
│   ├── jobs/                         # Job executors mapped from task job type
│   ├── output/                       # Generated output assets (json/images/pickle)
│   ├── services/                     # Shared services (e.g., agent service)
│   ├── team/                         # Team role implementations used in workflows
│   ├── ui/                           # NiceGUI pages (home/tasks/youtube/prompt)
│   └── task_scheduler_services.py    # Main scheduler/orchestration service
├── tests/                            # Unit + integration tests
├── logs/                             # Runtime logs (app/error logs)
├── gui.py                            # NiceGUI app entrypoint
├── main.py                           # Scheduler CLI entrypoint
├── main.ipynb                        # Notebook playground for manual flows
├── pyproject.toml                    # Poetry deps + tooling config
├── pytest.ini                        # Pytest config + markers
├── tox.ini                           # Tox envs for lint/type/test
└── Makefile                          # Common development commands
```

Key page modules under `backend/ui/`:

- `main.py`: dashboard navigation
- `tasks.py`: task list, add-task form, inline status update, delete action
- `video.py`: video list sorted by published date (desc), description preview
- `prompt.py`: prompt list table with expandable details

## Contributing

1. Create a branch from `develop`
2. Run `make check`
3. Open a PR to `develop`
