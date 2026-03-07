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
- [Environment Variables At A Glance](#environment-variables-at-a-glance)
- [YouTube OAuth Notes](#youtube-oauth-notes)
- [Development Commands](#development-commands)
- [Testing](#testing)
- [Architecture Overview](#architecture-overview)
- [Response Formats](#response-formats)
- [Project Layout](#project-layout)
- [Contributing](#contributing)

## Highlights

- Multi-agent orchestration for content and automation tasks
- Multiple LLM providers via LangChain integrations (OpenAI, Groq, DeepSeek, Perplexity, OpenRouter, Qwen)
- YouTube automation (channel/video sync, transcript workflows, thumbnail updates)
- Image generation + prompt pipelines
- AWS-backed persistence (DynamoDB + S3)
- Offline mode support with Moto-mocked AWS services
- Web dashboard built with NiceGUI (`/`, `/tasks`, `/youtube`, `/prompt`)
- Tasks dashboard: dynamic payload fields based on job type, task execution confirmation dialog, inline status updates, status-colored rows, delete action, expandable payload JSON viewer
- Videos dashboard: newest-first by published date, expandable rows, inline editing for title/description/transcript/summary, interactive Plotly stats charts (views/likes/comments over time)
- Prompt dashboard: expandable prompt table with task/role/model metadata
- Comprehensive logging across managers and services for debugging and monitoring
- Test suite with unit and integration markers
- Cache invalidation support for platform data models
- Interactive data visualization with Plotly for YouTube video analytics

## Project Health

Current internal score: **7.5/10**

### What is working well

- Clear modular architecture (`ai`, `data`, `database`, `jobs`, `integration`, `ui`)
- Practical developer workflow (`Makefile`, pytest markers, lint/type checks)
- Functional NiceGUI dashboards with live task operations
- Good momentum with iterative UI improvements (dynamic payload forms, confirmation dialogs, status updates, row actions, sorting, JSON payload rendering)
- Comprehensive logging in manager layer for operational visibility
- Lazy import pattern prevents circular dependencies in data models
- Cache invalidation methods for platform data freshness
- Type-safe code with mypy validation and assert-based type guards
- Plotly integration for rich data visualization in YouTube analytics

### Improvement areas

- UI page logic has grown and can be further componentize
- Some runtime configuration is still tightly coupled to environment setup
- Need stronger end-to-end GUI flow validation for confidence in regressions

### Gradual Improvement Tracker

Use this checklist to track progress toward a **9/10** quality target.

- [ ] Extract shared reusable table utilities/components for `tasks.py`, `video.py`, and `prompt.py`
- [ ] Add explicit confirmation dialog before task deletion
- [ ] Add sorting controls in Tasks table (not just static ordering)
- [x] Add field-level payload templates/validators for common `JobEnum` task types
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


- [ ] Test if it's able to generate good image prompts with multiple options
  - [ ] Test all the prompts once done
- [ ] Need to set up Qwen  
- [ ] Add one shot / few shot prompt examples for image and other generation tasks
- [ ] Find trending topic in a niche (YouTube, Google, other Social Media)
  - [ ] Use Google trends
  - [ ] YouTube idea suggester
- [ ] Twitter Integrate
  - [ ] Create Tweet for YouTube Post
  - [ ] Post tweets
- [ ] Higher lvl component (UI and Generator) should never access DB directly
- [ ] Improve the logger (Show proper details) - Added to managers (platform, startup, task)
- [ ] Ability to run the agent tasks in parallel
- [ ] Create short videos
- [ ] Mock data (use factory)
  - [ ] Use Faker for data
- [ ] Improve on prompt suggester
- [ ] Fix TODOs and Dead code
- [ ] Set Up GitHub Cron Job
  - [ ] Set up Env and variable
- [ ] Agent to analyze result
  - [ ] Add AI review step for generated answers
  - [ ] Agent to review tasks (only once)
- [ ] Test Coverage
  - [ ] Mock data from Agents (Positive and Negative)
  - [ ] Mock Integration with YouTube API
  - [ ] Test all the flows from Generator to Updater, Analyze
  - [ ] Test Data for DB integration
- [ ] GUI Enhancements
  - [ ] Page for Youtube Channel
  - [ ] Need to add UI for Youtube Channel
  - [ ] Run `poetry run app` from UI
  - [ ] Analytics dashboard
  - [ ] Ability to perform all tasks from GUI
- [ ] Fix transcripts for grammar and naming errors
- [ ] Add Playlist details to YouTube Video DB

- Naming convention for generator
  - Updater (Update data to source)
  - Suggester (Suggest for Something mostly agent)
  - Creator (Create Data on DB)
  - Analyzer (Analysis the data)
  - Generator (Generate Image / Video Sound)
  - Add Post to TikTok
  - Add Instagram

### YouTube Workflow Pipeline

Task creation flows from top to bottom. Each stage is a separate scheduled job that fetches, processes, and creates the next task:

```
YouTubeChannelCreator (Initial Task)
│
├── Action: Fetch channel info from YouTube API
├── Store: YouTubeChannelDB
└── Creates: YouTubeVideoGenerator
    │
    ├── Action: Fetch all videos for channel
    ├── Store: YouTubeVideoDB
    └── Creates: YouTubeVideoAnalyzer
        │
        ├── Action: Analyze video stats and content
        └── Creates: YouTubeMetadataSuggester
            │
            ├── Action: Use LLM to generate title/description/tags
            ├── Store: Prompt + suggestions in DB
            └── Creates: YouTubeMetadataUpdater (if enabled)
                │
                ├── Action: Update YouTube video with suggested metadata
                └── Creates: ImagePromptSuggester (if thumbnail update enabled)
                    │
                    ├── Action: Generate image prompt from video content
                    └── Creates: ImageGenerator
                        │
                        ├── Action: Generate thumbnail image from prompt
                        └── Creates: YouTubeThumbnailUpdater
                            │
                            └── Action: Upload generated thumbnail to YouTube (FINAL STEP)
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

If `OFFLINE` is not set, the app defaults to `false`.

## Environment Variables At A Glance

| Variable | Required | Purpose |
| --- | --- | --- |
| `VERSION` | Yes | Runtime label (for example `local`, `dev`, `prod`). |
| `COMPANY_NAME` | Yes | Branding/display name used in UI and logs. |
| `AWS_CLIENT_ID` | Yes (online mode) | AWS access key ID. |
| `AWS_SECRET` | Yes (online mode) | AWS secret access key. |
| `AWS_REGION` | Yes | AWS region for DynamoDB/S3 resources. |
| `AWS_SECRET_MANAGER` | Optional | Secret manager key/path if used in your deployment. |
| `AWS_TABLE` | Yes | DynamoDB table name for app data. |
| `AWS_S3_BUCKET` | Yes | S3 bucket for persisted output assets. |
| `OFFLINE` | Optional | Local Moto mode flag (`true/1/yes/on` enables offline mode). |
| `YOUTUBE_API_KEY` | Required for YouTube API workflows | Server-to-server YouTube API calls. |
| `YOUTUBE_CHANNEL_ID` | Required for default channel workflows | Primary channel identifier. |
| `OPENAI_API_KEY` | Optional | Enables OpenAI-backed generation paths. |
| `DEEPSEEK_API_KEY` | Optional | Enables DeepSeek-backed generation paths. |
| `GROQ_API_KEY` | Optional | Enables Groq-backed generation paths. |
| `PPLX_API_KEY` | Optional | Enables Perplexity-backed generation paths. |
| `OPEN_ROUTE_API_KEY` | Optional | Enables OpenRouter-backed generation paths. |

Notes:

- In offline mode, AWS calls are routed to Moto and bootstrap local resources automatically.
- You only need to provide API keys for providers you actually use.

### 3) Run the app

```sh
poetry run app
```

Run a single task by ID (one-time execution):

```sh
poetry run app --task-id <task_id>
```

When `--task-id` is provided, the scheduler executes only that task and exits.

Run one-time transformation and exit:

```sh
poetry run app --transform true
```

Use `--transform true` for a one-time transformation run.

### 4) Run the dashboard

```sh
poetry run python -m gui
```

Open: `http://localhost:8080`

You can also toggle AWS offline mode at runtime from the dashboard header using the
`Offline` switch:

- `On`: uses Moto-mocked AWS (S3 + DynamoDB)
- `Off`: uses configured real AWS credentials/resources

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
OFFLINE=true poetry run pytest tests/test_s3_storage.py tests/test_integration.py
poetry run tox -e pytest
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
- `backend/manager/`: manager layer with comprehensive logging for platform, startup, and task operations
- `backend/ai/`: provider adapters
- `backend/database/`: DynamoDB access layer
- `backend/integration/`: external services (YouTube, S3, image generation, TTS)
- `backend/data/`: Pydantic/domain data models with cache invalidation support for platform data
- `backend/ui/` + `gui.py`: NiceGUI pages and app entry

## Response Formats

### YouTube Video Analyzer

File: `backend/generator/response_format/youtube_video_analyzer_response.py`

`YouTubeVideoAnalyzerResponse` fields:

- `title: str`
- `description: str`
- `tags: list[str]`

Batch wrapper:

- `YouTubeVideoAnalyzerListResponse.details: list[YouTubeVideoAnalyzerResponse]`

Example payload:

```json
{
  "details": [
    {
      "title": "How I Automated My YouTube Workflow",
      "description": "A short breakdown of task scheduling and metadata automation.",
      "tags": ["youtube", "automation", "ai"]
    }
  ]
}
```

## Project Layout

```text
backend.completeautomate/
├── backend/
│   ├── ai/                           # LLM provider wrappers (OpenAI, Groq, DeepSeek, Perplexity, OpenRouter, Qwen)
│   ├── config/                       # env loading, logging setup, session config
│   ├── data/                         # Core data models (Task, Prompt, YouTube, Image, S3, Platform, Team, Message)
│   ├── database/                     # DynamoDB access layer and DB-specific repositories
│   │   ├── agent/
│   │   ├── image/
│   │   ├── platform/
│   │   ├── prompt/
│   │   ├── task/
│   │   ├── youtube/
│   │   └── dynamo_database.py
│   ├── enum/                         # Enums for job/status/team/db keys/prompt types/platforms/images
│   ├── exception/                    # Custom app exception types
│   ├── factory/                      # Factory classes for agent and task creation
│   ├── generator/                    # Domain generators (image/youtube/analysis/summarize/metadata)
│   │   ├── response_format/
│   │   └── youtube_*.py
│   ├── helper/                       # Startup + utility helpers
│   │   ├── folder_helper/
│   │   └── start_up/
│   ├── integration/                  # External integrations
│   │   ├── agent/
│   │   ├── image_generation/
│   │   ├── storage/
│   │   ├── text_to_speech/
│   │   └── youtube/
│   ├── jobs/                         # Job executors mapped from task job type
│   │   ├── base_job.py
│   │   ├── image_generator_job.py
│   │   ├── image_prompt_job.py
│   │   ├── youtube_job.py
│   │   └── no_job.py
│   ├── manager/                      # Manager classes for platform, startup, and task operations
│   ├── output/                       # Generated output assets (json/images/pickle)
│   ├── services/                     # Shared services (e.g., agent service)
│   ├── team/                         # Team role implementations used in workflows
│   ├── ui/                           # NiceGUI pages and navigation
│   │   ├── main.py
│   │   ├── navigation.py
│   │   ├── tasks.py
│   │   ├── video.py
│   │   └── prompt.py
│   └── task_scheduler_services.py    # Main scheduler/orchestration service
├── tests/                            # Unit + integration tests
│   └── database/
├── logs/                             # Runtime logs (app/error logs)
├── .github/                          # GitHub Actions CI/CD workflows
├── gui.py                            # NiceGUI app entrypoint
├── main.py                           # Scheduler CLI entrypoint
├── main.ipynb                        # Notebook playground for manual flows
├── pyproject.toml                    # Poetry deps + tooling config
├── poetry.lock                       # Poetry lock file
├── pytest.ini                        # Pytest config + markers
├── tox.ini                           # Tox envs for lint/type/test
└── Makefile                          # Common development commands
```

Key modules:

**UI pages** (`backend/ui/`):
- `main.py`: home dashboard page
- `navigation.py`: shared navigation component
- `tasks.py`: task list with dynamic payload forms (11 job types), task execution confirmation dialog, inline status updates, delete action, expandable payload JSON viewer
- `video.py`: video list with expandable rows, inline editing for video details/transcript/summary (uses ref_id)
- `prompt.py`: prompt list table with expandable details

**Jobs** (`backend/jobs/`):
- `base_job.py`: base job class
- `image_generator_job.py`: image generation tasks
- `image_prompt_job.py`: image prompt generation tasks
- `youtube_job.py`: YouTube-related task execution
- `prompt_suggester_job.py`: prompt suggestion tasks
- `no_job.py`: fallback for unmapped job types

**Factories** (`backend/factory/`):
- `agent_factory.py`: creates AI agent instances
- `task_factory.py`: creates task objects

**Managers** (`backend/manager/`)  - *Enhanced with comprehensive logging*:
- `platform_manager.py`: platform operations with logging
- `start_up_manager.py`: application startup logic with lifecycle logging
- `task_manager.py`: task lifecycle management with operation tracking

## Contributing

1. Create a branch from `develop`
2. Run `make check`
3. Open a PR to `develop`
