# Complete Automate Backend

![CI](https://github.com/vimalmenon/backend.completeautomate/workflows/CI/badge.svg)
![Project Rating](https://img.shields.io/badge/Project%20Rating-8.0%2F10-yellow)

Python backend for multi-agent automation workflows, with task scheduling, YouTube automation, and image generation.

## Table of Contents

- [Highlights](#highlights)
- [Project Health](#project-health)
- [Roadmap](#roadmap)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
  - [1) Install dependencies](#1-install-dependencies)
  - [2) Run the app](#2-run-the-app)
  - [3) Run the dashboard](#3-run-the-dashboard)
- [YouTube OAuth Notes](#youtube-oauth-notes)
- [Thumbnail Upload Size Handling](#thumbnail-upload-size-handling)
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
- AWS persistence with DynamoDB + S3, plus offline mode via Moto mocks
- Strong developer ergonomics: logging, typed models, cache invalidation, and unit/integration tests

## Roadmap

- NEXT
  - [ ][3] Sort videos by published date
  - [ ][1] Set up feature branch 
  - [ ][6] Set Up LangGraph
  - [ ][2] Set up Text To Speech (TTS)
  - [ ][3] Set up email
    - [ ] support@completeautomate.com
    - [ ] info@completeautomate.com
  - [ ][8] Refactor Prompt

<details>
<summary><strong>TODO Items</strong> (click to expand)</summary>

- [ ] API
  - [ ] Auth
    - [ ] [3] Set up `Basic Auth`
    - [ ] [6] Set up AWS Cognito
- [ ] Text to Speech
  - [ ] [3] Create a AI services for text to Speech
  - [ ] [1] Check the voice generated extension (mp3 / mov)
  - [ ] [4] Add API for Resemble AI for TTS
  - [ ] [3] Upload to S3
- [ ] Bugs
- [ ] Fix
  - [ ] [3] YouTube Video and Channel Stats data more than 5 months should be changed to months
- [ ] [8] Streamline AI Generation
  - [ ] Text Generation
  - [ ] Image Generation
  - [ ] Speech Generation
- [ ] Fix / Improve YouTube
  - [ ] [5] Add Twitter Post Suggestion
  - [ ] [1] Rename `YouTubeStatsUpdaterTaskData` to better name
  - [ ] [3] `user_message` added to `YouTubeVideo`
    - [ ] [3] Add `user_message` on all the AI Request expect thumbnail
    - [ ] [2] Add `user_message` to required prompts
    - [ ] [5] Metadata suggestion to be provided with `user_message`
    - [ ] [4] Summarize to have essence `user_message`
  - [ ] Playlist
    - [ ] [4] Get all videos in playlist
- [ ] Improve Jobs
  - [ ] [5] Run Jobs in parallel
  - [ ] [5] Ability to run the agent tasks in parallel
- [ ] Offline Feature
  - [ ] [4] Need a database for Mocked API when Offline
  - [ ] [4] Store the response received from API (in JSON Format)
  - [ ] [4] Mock data from Agents (Positive and Negative)
  - [ ] [4] All data needs to be mocked
- [ ] [20] Improve on prompt
  - [ ] [4] Create prompt improver result
  - [ ] [4] Move all prompts to Prompt Agent
  - [ ] [4] Need to pass data To `Prompt Improver` to test and evaluate
  - [ ] [5] Pass real data to `prompt_data` to PromptImprover (minimum 2 data to be given)
  - [ ] Can We use one cls for PromptImprover and Prompt? (Not possible)
    - [ ] Cannot use one class / DB for both prompt and improver
    - [ ] Create another table for `PromptResult`
  - [ ] Should be able to test the prompts generated
  - [ ] Add one shot / few shot prompt for prompts
  - [ ] Run PromptImprover in parallel
- [ ] Send Notification
  - [ ] [6] Send Signal
  - [ ] [6] Send Email
  - [ ] [6] Send WhatsApp message
- [ ] Loggers
  - [ ] Send the logs to some common place (AWS Logger)
  - [ ] Improve the logger (Show proper details) - Added to managers (platform, startup, task)
- [ ] Start multiple tasks in parallel
- [ ] Find trending topic in a niche (YouTube, Google, other Social Media)
  - [ ] YouTube topic suggester
  - [ ] Use Google trends
  - [ ] API to search the `Trends`
  - [ ] Find next week topic
- [ ] Create a pointer for YouTube Video
  - [ ] Generate the required images for presenting
  - [ ] Create a pointers required
  - [ ] Pointer for video to create
- [ ] [8] Twitter Integrate
- [ ] Test Coverage
  - [ ] Mock Integration with YouTube API
  - [ ] Test all the flows from Generator to Updater, Analyze
  - [ ] Test Data for DB integration
- [ ] Email
  - [ ] [3] Set up Email with CompleteAutomate (support@completeautomate.com)

```
A high-quality YouTube thumbnail in a 16:9 aspect ratio (1280x720). The theme is 'AI Foundations' with a sleek dark-mode tech aesthetic featuring neon purple and blue accents. The layout is divided into three clear visual sections: 1) A glowing neural network brain icon labeled 'AI', 2) A futuristic robot holding a digital toolbox labeled 'AGENT', and 3) A clean flowchart of connected nodes and lines labeled 'WORKFLOW'. In the top-left corner, place a high-contrast yellow badge with bold black text that says 'PART 1'. In the center or bottom, feature large, cinematic 3D white typography that says 'AI vs AGENT vs WORKFLOW'. Near the corner, add a small floating graphic of a digital coin or currency symbol with the text 'Tokens = '. Professional cinematic lighting, 8k resolution, clean and modern developer UI style.
```

**Ideas / Low Priority:**

- Local text-to-speech
- Dockerfile + DockerHub CD
- App / API Integration
  - Instagram
  - Twitter
  - Reddit
  - TikTok
  - LinkedIn
  - Email
  - Signal
  - WhatsApp
- YouTube comments analysis
- Remove teams as it looks of no use
- Create Videos
- Scrape websites for contacts and potential client
- Tailor made email with video for potential client
- Adopt GIT branching strategies
- Set Up N8N
- Make a Webpage based on the post
</details>

## YouTube Workflow Pipeline

Jobs and tasks flow from top to bottom. Channel-level jobs run continuously; video-level tasks are gated by user review at each `REVIEW` step.

```
[Dashboard] Create: YouTubeChannelOnboarding job
│
├── Job: YouTubeChannel  (YouTubeChannelCreatorJob)
│     Action: Sync channel info from YouTube API → YouTubeChannelDB
│
└── Job: YouTubeChannelVideoChecker  (YouTubeChannelVideoCheckerJob)
      Action: List all channel videos → create a YouTubeVideo job per new video
      │
      └── Job: YouTubeVideo  (YouTubeVideoGenerator)
            Progresses through tasks in sequence:
            │
            ├── Task: YouTubeVideoStart
            │     Action: Fetch video from YouTube API → store in YouTubeVideoDB
            │
            ├── Task: YouTubeVideoFixTranscript  [REVIEW]
            │     Action: Generate transcript summary + metadata suggestions via AI
            │     User: Review / edit transcript, then double-click to advance
            │
            ├── Task: YouTubeVideoMetadataSelection  [REVIEW]
            │     Action: User selects best metadata option
            │     Then:  Update YouTube video metadata, generate thumbnail prompt
            │             suggestions, and generate thumbnail images
            │
            ├── Task: YouTubeVideoThumbnailSelection  [REVIEW]
            │     Action: User selects best thumbnail
            │     Then:  Upload thumbnail to YouTube, mark video as reviewed
            │
            └── Task: YouTubeVideoComplete
                  Terminal state — pipeline finished for this video
```

**Key Points:**

- Start by creating a `YouTubeChannelOnboarding` job from the Jobs dashboard
- Channel-level jobs (`YouTubeChannel`, `YouTubeChannelVideoChecker`) run on a continuous schedule
- The single `YouTubeVideo` job handles the full video pipeline via internal task stages
- `[REVIEW]` stages pause and wait for user action in the dashboard before advancing
- Each job can be retried or repositioned in the queue via the dashboard

## UI Routes

Main /
tasks /tasks
YouTube Channels /youtube
Channel Id & YouTube Videos /youtube/{channel_id}?tab={channel / videos} default to channel
YouTube Video detail /youtube/{channel_id}/{video_id}?section={metadata_review | thumbnail_review}
S3 Storage /storage
Prompt /prompts
Prompt Detail /prompts/{prompt_id}

## YouTube Video Page (Current UI)

The `/youtube/{channel_id}/{video_id}` page currently includes:

- Header actions: **Show Graph** (opens Plotly stats dialog) and **Edit Transcript** (opens transcript editor dialog)
- Video summary card with thumbnail, title, published/language badges, and tag badges
- Inline latest video stats (views, likes, comments, stats updated)
- Task Flow card showing pipeline stages and current status per stage
- Double-click on editable Task Flow steps (e.g., **Fix Transcript**, **Metadata Selection**, **Thumbnail Selection**) to update status
- Metadata Suggestions section with per-option status update controls
- Thumbnail Suggestions section with image preview and single-option select (promote) action
- Thumbnail Prompt Suggestions section with per-option status update controls
- Transcript card with fixed-height scroll area
- Summarized Transcript card (shown when available) with fixed-height scroll area

Transcript editor dialog supports:

- In-place editing and save to DB
- Live character count
- Persistent modal behavior (prevents accidental close by outside click)

## Thumbnail Upload Size Handling

YouTube rejects thumbnails larger than `2 MB` (`2097152` bytes). The backend now handles this automatically before upload:

- Entry point: `YouTubeAPI.update_thumbnail`
- Reusable function: `YouTubeAPI.reduce_image_size(image_path, max_size_bytes=2*1024*1024)`
- Behavior:
  - If image is already within size limit, it uploads as-is
  - If oversized, it converts/compresses to JPEG and progressively resizes until under the limit
  - Upload uses the optimized temporary file and cleans it up after request

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

### 2) Run the app

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

## Image Generation Models

The backend currently supports these image providers/models:

- `FLUX` via OpenRouter (`black-forest-labs/flux.2-flex`)
- `GROK` via xAI (`grok-imagine-image`)
- `QWEN` via DashScope (`qwen-image-max`)

Qwen image generation uses DashScope `MultiModalConversation` with:

- Base URL: `https://dashscope-intl.aliyuncs.com/api/v1`
- API key env var: `QWEN_API_KEY`
- Default image size: `1328*1328`

### 3) Run the dashboard

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
- Jobs: `http://localhost:8080/jobs`
- Tasks (alias): `http://localhost:8080/tasks`
- YouTube Channel: `http://localhost:8080/youtube/{channel_id}`
- YouTube Video: `http://localhost:8080/youtube/{channel_id}/{video_id}`
- Prompt: `http://localhost:8080/prompt`
- Prompt Details: `http://localhost:8080/prompt/{task_id}`
- S3 Bucket: `http://localhost:8080/s3`

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

The project uses `faker` for synthetic data generation in shared test/factory helpers and domain-specific factory functions.

**Common helpers** in `backend/factory/common.py`:

- `fake_date()` — generate fake datetime
- `fake_uuid()` — generate fake UUID
- `fake_url()` — generate fake URL

**Domain factories** in `backend/factory/`:

- `create_youtube_channel_job_factory(**kwargs)` — creates `YouTubeJobData`
- `platform_channel_factory(**kwargs)` — creates `PlatformDBData` for YouTube channels
- `platform_video_factory(**kwargs)` — creates `PlatformDBData` for YouTube videos
- `image_generator_factory(**kwargs)` — creates image generation mock data

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

- `backend/jobs_scheduler.py`: scheduler loop and job routing
- `backend/jobs/`: job handlers (youtube channel/video/short, stats updater, prompt suggester)
- Fallback behavior: if a task's `job_type` has no mapped handler, scheduler uses `NoJob`, logs an error, and marks the task as `FAILED` while incrementing `failed_count`
- `backend/api/`: FastAPI route handlers for jobs, prompts, channels, and data
- `backend/generator/`: workflow generators and domain logic (YouTube channel, video, short, stats)
- `backend/prompt_agent/`: prompt agents for AI generation (metadata, summarization, community posts, thumbnails)
- `backend/manager/`: manager layer with logging for all domain operations
- `backend/factory/common.py`: shared Faker-backed helpers for generating mock values
- `backend/ai/`: provider adapters
- `backend/database/`: DynamoDB access layer (includes mocked DB for offline mode)
- `backend/integration/`: external services (YouTube, S3, image generation, TTS)
- `backend/data/`: Pydantic/domain data models with cache invalidation support for platform data

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
│   ├── api/                          # FastAPI route handlers
│   │   ├── main.py
│   │   ├── channel_api.py
│   │   ├── data_api.py
│   │   ├── health_api.py
│   │   ├── jobs_api.py
│   │   └── prompts_api.py
│   ├── config/                       # env loading, logging setup, session config
│   ├── data/                         # Core data models (Task, Prompt, YouTube, Image, S3, Platform, Message)
│   ├── database/                     # DynamoDB access layer and DB-specific repositories
│   │   ├── agent/
│   │   ├── image/
│   │   ├── job/
│   │   ├── mocked/
│   │   ├── platform/
│   │   ├── prompt/
│   │   ├── task/
│   │   └── youtube/
│   ├── enum/                         # Enums for job/status/db keys/prompt types/platforms/images
│   ├── exception/                    # Custom app exception types
│   ├── factory/                      # Factory helpers for test data and domain objects
│   │   ├── common.py
│   │   ├── job_factory.py
│   │   ├── platform_factory.py
│   │   ├── youtube_channel_factory.py
│   │   ├── youtube_video_factory.py
│   │   └── youtube_api_factory.py
│   ├── generator/                    # Domain generators (youtube/analysis/summarize/metadata)
│   │   ├── response_format/
│   │   ├── base_generator.py
│   │   ├── youtube_channel_creator.py
│   │   ├── youtube_short_generator.py
│   │   ├── youtube_stats_updater.py
│   │   └── youtube_video_generator.py
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
│   │   ├── youtube_channel_job.py
│   │   ├── youtube_video_job.py
│   │   ├── youtube_short_job.py
│   │   ├── youtube_stats_updater_job.py
│   │   ├── prompt_suggester_job.py
│   │   └── no_job.py
│   ├── manager/                      # Manager layer with logging for all domain operations
│   │   ├── action_manager.py
│   │   ├── data_manager.py
│   │   ├── job_manager.py
│   │   ├── platform_manager.py
│   │   ├── prompt_manager.py
│   │   ├── start_up_manager.py
│   │   ├── transform.py
│   │   ├── youtube_channel_manager.py
│   │   └── youtube_video_manager.py
│   ├── output/                       # Generated output assets (json/images/pickle)
│   ├── prompt_agent/                 # Prompt agents for AI generation tasks
│   │   ├── youtube_short_speech_generation_prompt_agent.py
│   │   ├── youtube_thumbnail_image_generation_prompt_agent.py
│   │   ├── youtube_video_community_post_agent.py
│   │   ├── youtube_video_metadata_agent.py
│   │   ├── youtube_video_summarization_agent.py
│   │   └── youtube_video_twitter_post_agent.py
│   ├── services/                     # Shared services (e.g., agent service)
│   └── jobs_scheduler.py             # Main scheduler/orchestration service
├── tests/                            # Unit + integration tests
│   └── database/
├── logs/                             # Runtime logs (app/error logs)
├── .github/                          # GitHub Actions CI/CD workflows
├── main.py                           # Scheduler CLI entrypoint
├── pyproject.toml                    # Poetry deps + tooling config
├── poetry.lock                       # Poetry lock file
├── pytest.ini                        # Pytest config + markers
├── tox.ini                           # Tox envs for lint/type/test
└── Makefile                          # Common development commands
```

Key modules:

**API** (`backend/api/`):

- `main.py`: FastAPI app setup and router registration
- `channel_api.py`: YouTube channel endpoints
- `data_api.py`: data access endpoints
- `health_api.py`: health check endpoint
- `jobs_api.py`: job management endpoints
- `prompts_api.py`: prompt endpoints

**Jobs** (`backend/jobs/`):

- `base_job.py`: base job class
- `youtube_channel_job.py`: YouTube channel sync tasks
- `youtube_video_job.py`: YouTube video pipeline tasks
- `youtube_short_job.py`: YouTube Shorts tasks
- `youtube_stats_updater_job.py`: stats update tasks
- `prompt_suggester_job.py`: prompt suggestion tasks
- `no_job.py`: fallback for unmapped job types

**Prompt Agents** (`backend/prompt_agent/`):

- `youtube_video_metadata_agent.py`: metadata suggestion prompts
- `youtube_video_summarization_agent.py`: transcript summarization prompts
- `youtube_video_community_post_agent.py`: community post prompts
- `youtube_video_twitter_post_agent.py`: Twitter post prompts
- `youtube_short_speech_generation_prompt_agent.py`: short speech generation prompts
- `youtube_thumbnail_image_generation_prompt_agent.py`: thumbnail image generation prompts

**Factories** (`backend/factory/`):

- `common.py`: shared Faker-backed helpers (`fake_date()`, `fake_uuid()`, `fake_url()`)
- `job_factory.py`: creates `YouTubeJobData` instances
- `platform_factory.py`: creates `PlatformDBData` instances
- `youtube_channel_factory.py`: creates YouTube channel mock data
- `youtube_video_factory.py`: creates YouTube video mock data
- `youtube_api_factory.py`: creates YouTube API response mock data

**Managers** (`backend/manager/`):

- `action_manager.py`: action execution management
- `data_manager.py`: data access and transformation
- `job_manager.py`: job lifecycle management
- `platform_manager.py`: platform operations with logging
- `prompt_manager.py`: prompt data management
- `start_up_manager.py`: application startup logic with lifecycle logging
- `transform.py`: data transformation utilities
- `youtube_channel_manager.py`: YouTube channel operations
- `youtube_video_manager.py`: YouTube video operations

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
https://common-buy-intl.alibabacloud.com/coding-plan?accounttraceid=06b40b9cb7924958ad831f64029fd8a5zrqj
https://github.com/settings/copilot/features
```
