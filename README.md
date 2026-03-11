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
- [Mock Data Factories](#mock-data-factories)
- [Architecture Overview](#architecture-overview)
- [Response Formats](#response-formats)
- [Project Layout](#project-layout)
- [Contributing](#contributing)

## Highlights

- Multi-agent backend for task scheduling and automation workflows
- Multi-provider AI support (OpenAI, DeepSeek, Perplexity, OpenRouter, xAI Grok, Qwen)
- End-to-end YouTube workflow automation: channel/video sync, analysis, metadata, and thumbnails
- Image generation and prompt pipelines (FLUX, Grok, Qwen)
- NiceGUI dashboard for tasks, videos, channels, prompts, and operations
- AWS persistence with DynamoDB + S3, plus offline mode via Moto mocks
- Strong developer ergonomics: logging, typed models, cache invalidation, and unit/integration tests

## Project Health

Current internal score: **7.5/10**

### What is working well

- Modular architecture with clear separation across AI, data, database, jobs, integrations, and UI
- Solid developer workflow with Make targets, pytest markers, linting, and type checking
- Functional NiceGUI dashboards with active task/video/prompt operations and ongoing UX improvements
- Strong observability and reliability patterns: manager-layer logging, lazy imports, and cache invalidation
- Typed codebase with mypy validation and Plotly-powered YouTube analytics visualization

### Improvement areas

- UI page logic has grown and can be further componentize
- Some runtime configuration is still tightly coupled to environment setup
- Need stronger end-to-end GUI flow validation for confidence in regressions

### Gradual Improvement Tracker

Use this checklist to track progress toward a **9/10** quality target.

- [ ] Extract shared reusable table utilities/components for `tasks.py`, `video.py`, and `prompt.py`
- [ ] Add explicit confirmation dialog before task deletion
- [ ] Add sorting controls in Tasks table (not just static ordering)
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
<summary><strong>TODO Items</strong> (click to expand)</summary>

- [ ] Improve features
  - [x] `Created By` seems redundant as there is already trails
  - [ ] Higher lvl component (UI and Generator) should never access DB directly
  - [ ] Improve the logger (Show proper details) - Added to managers (platform, startup, task)
  - [ ] Add playlist details to YouTube Video DB
  - [ ] Standardize update data in DB
  - [ ] Fix transcripts for grammar and other errors in DB
  - [ ] Job only to fix transcript or do it while getting videos
- [ ] Set up image generation
  - [ ] Standardize the image generation
  - [ ] Make the image generation more generic to be used
  - [ ] Put all the generated image prompt to review
- [ ] GUI Enhancements (Top priority)
  - [ ] Update the title, description in DB after Metadata suggestion updated
  - [ ] Move to new routes
  - [ ] Clicking on `Task` navigate button should route to correct page
  - [ ] Channel to show both channel details and videos
  - [ ] Show channel detail and videos in tabs
  - [ ] Ability to perform all actions from GUI
  - [ ] Show the current status of video Tasks (Metadata Suggester, Thumbnail Suggester)
  - [ ] View images from S3 and Local
  - [ ] Button to download S3 Object to local
- [ ] Find trending topic in a niche (YouTube, Google, other Social Media)
  - [ ] YouTube topic suggester
  - [ ] Pointer for video to create
  - [ ] Find next week topic
  - [ ] Use Google trends
- [ ] Agent to analyze result
  - [ ] Add AI review step for generated answers
  - [ ] Agent to review tasks (only once)
- [ ] Twitter Integrate
  - [ ] Create Tweet for YouTube Post
  - [ ] Post tweets
- [ ] Add one shot / few shot prompt examples for image and other generation tasks
- [ ] Ability to run the agent tasks in parallel
- [ ] Complete TODOs
- [ ] Remove Deadcode
- [ ] Test all the prompts once done
- [ ] Improve on prompt suggester
- [ ] Mock data (use factory)
  - [ ] All data needs to be mocked
- [ ] Set Up GitHub Cron Job
  - [ ] Set up Env and Variable
- [ ] Test Coverage
  - [ ] Mock data from Agents (Positive and Negative)
  - [ ] Mock Integration with YouTube API
  - [ ] Test all the flows from Generator to Updater, Analyze
  - [ ] Test Data for DB integration

- Naming convention for generator
  - Updater (Update data to source)
  - Suggester (Suggest for Something mostly agent)
  - Creator (Create Data on DB)
  - Analyzer (Analysis the data)
  - Generator (Generate Image / Video Sound)

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

- Local text-to-speech
- Dockerfile + DockerHub CD
- App / API Integration
  - Instagram
  - Twitter
  - Redit
  - TikTok
  - LinkedIn
  - Email
  - Signal
  - WhatsApp
- YouTube comments analysis
- Need an mobile APP / Website
- Remove teams as it looks of no use
- Correct transcript
- Create Videos
- Notify user on `REVIEW` via email, Telegram or WhatsApp
- Scrape websites for contact and potential client
- Tailor made email with video for potential client
- Adopt GIT branching strategies
- Backup data to S3

</details>


## UI Routes

Main                            /
tasks                           /tasks
YouTube Channels                /youtube
Channel Id & YouTube Videos     /youtube/{channel_id}?tab={channel / videos} default to channel
YouTube Video detail            /youtube/{channel_id}/{video_id}?section={metadata_review | thumbnail_review}
S3 Storage                      /storage
Prompt                          /prompts
Prompt Detail                   /prompts/{prompt_id}


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

QWEN_API_KEY=...
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

Run one-time test script and exit:

```sh
poetry run app --test true
```

## Image Generation Models

The backend currently supports these image providers/models:

- `FLUX` via OpenRouter (`black-forest-labs/flux.2-flex`)
- `GROK` via xAI (`grok-imagine-image`)
- `QWEN` via DashScope (`qwen-image-max`)

Qwen image generation uses DashScope `MultiModalConversation` with:

- Base URL: `https://dashscope-intl.aliyuncs.com/api/v1`
- API key env var: `QWEN_API_KEY`
- Default image size: `1328*1328`



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
- Channel Details: `http://localhost:8080/channel/{channel_id}`
- Video Details: `http://localhost:8080/video/{ref_id}`
- Prompts: `http://localhost:8080/prompt`
- Prompt Details: `http://localhost:8080/prompt/{task_id}`

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
poetry run app --test true
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

## Mock Data Factories

The project uses `faker` for synthetic data generation in shared test/factory helpers.

Current helpers live in `backend/factory/common.py`:

- `fake_date()`
- `fake_uuid()`
- `fake_url()`

Example usage:

```python
from backend.factory.common import fake_date, fake_url, fake_uuid

payload = {
  "task_id": fake_uuid(),
  "created_at": fake_date(),
  "source_url": fake_url(),
}
```

Tip: seed Faker in tests when deterministic values are needed.

## Architecture Overview

- `backend/task_scheduler_services.py`: scheduler loop and job routing
- `backend/jobs/`: job handlers (image, prompt, youtube, etc.)
- Fallback behavior: if a task's `job_type` has no mapped handler, scheduler uses `NoJob`, logs an error, and marks the task as `FAILED` while incrementing `failed_count`
- `backend/generator/`: workflow generators and domain logic
- `backend/services/agent_service.py`: model/prompt orchestration
- `backend/manager/`: manager layer with comprehensive logging for platform, startup, and task operations
- `backend/factory/common.py`: shared Faker-backed helpers for generating mock values
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
- `video.py`: video list with detail-page navigation, channel detail page (`/channel/{channel_id}`), inline editing for video details/transcript/summary, video/channel Plotly stats dialogs, and ImagePromptDB-backed thumbnail workflow actions
- `prompt.py`: prompt list with detail-page navigation (`/prompt/{task_id}`) and edit support

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


### Links

```
https://docs.resemble.ai/getting-started/quickstart
https://leonardo.ai/pricing/
https://aistudio.google.com/app/
https://docs.langchain.com/oss/python/integrations/chat
https://platform.deepseek.com/usage
https://smith.langchain.com/o/aa8cfe1a-75c1-4fff-bf0c-187edfa443ee/projects
https://console.groq.com/dashboard/usage
```