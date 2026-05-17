# Complete Automate Backend

![CI](https://github.com/vimalmenon/backend.completeautomate/workflows/CI/badge.svg)

Python backend for **Complete Automate** — a multi-agent AI automation platform. Manages YouTube content pipelines, multi-provider AI generation (text, image, speech, video), job scheduling, and cloud persistence.

---

## Highlights

- **Multi-agent job scheduler** with state-machine task progression and retry logic
- **End-to-end YouTube workflow**: channel sync, video discovery, transcript analysis, metadata optimization, thumbnail generation, community posts
- **Multi-provider AI**: 6 text, 3 image, 2 speech, 1 video provider via LangChain adapter pattern
- **Prompt management system** with versioned prompts, per-task AI model assignment, Jinja2 template rendering
- **Cloud-native persistence**: DynamoDB + S3, with full offline mode via Moto mocks
- **FastAPI dashboard** with job management, YouTube channel/video views, prompt editing, and S3 browser
- **Structured code quality**: Black, Ruff, isort, Mypy, Pytest, flake8, deadcode analyzer

---

## Roadmap

- NEXT
  - [ ][4] Set Up LangGraph for YouTubeShorts Videos
  - [ ][4] Set up State in LangGraph
  - [ ][2] Set up Text To Speech (TTS)
  - [x][4] Sort the Job Status ["IN_Process", "Review", "Complete", "Failed"] and created_date
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

  **Phase 1: Foundation — PromptResult Table**
  - [x] Create DynamoDB table for prompt results (`PromptResult`)
  - [x] Wire `PromptResultDBData` model to `PromptResultDatabase` CRUD
  - [x] Add API endpoints for prompt results (list, get, update)
  - [x] Add prompt result display to the dashboard

  **Phase 2: Prompt Agent Migration**
  - [ ] [2] Audit all generators — find hardcoded prompts still outside the Prompt Agent system
  - [x] Move `YouTubeVideoMetadata` prompt fully into Prompt Agent
  - [x] Move `YouTubeVideoSummarization` prompt fully into Prompt Agent
  - [x] Move `YouTubeVideoCommunityPost` prompt fully into Prompt Agent
  - [x] Move `YouTubeThumbnailImageGenerationPrompt` prompt fully into Prompt Agent
  - [x] Move `YouTubeShortSpeechGenerationPrompt` prompt fully into Prompt Agent
  - [x] Move `YouTubeVideoTwitterPost` prompt fully into Prompt Agent
  - [x] Remove fallback/legacy prompt paths from generators

  **Phase 3: PromptImprover Loop**
  - [x] Build PromptImprover pipeline in `prompt_reviewer.py`:
    - Load all prompts from DB
    - For each prompt, run AI evaluation against `prompt_data`
    - Score the prompt quality (relevance, clarity, structure)
    - Generate improved version with reflection
    - Save both result and new version
  - [x] Pass real `prompt_data` to PromptImprover (via managed list on PromptDBData)
  - [x] Store evaluation results to `PromptResult` table
  - [ ] Add prompt version comparison view in dashboard

  **Phase 4: Few-Shot & Testing**
  - [ ] [3] Add `examples` field to `PromptVersionDBData` model
  - [ ] [4] Build few-shot example management (add/remove/list)
  - [ ] [4] Add few-shot injection into AgentService template rendering
  - [ ] [4] Create prompt generation tests
    - [ ] Render each prompt template with mock data
    - [ ] Validate output schema matches expected response format
    - [ ] Test with edge cases (empty transcript, missing fields)
  - [ ] [4] Build prompt version rollback mechanism

  **Phase 5: Parallel Execution**
  - [ ] [4] Run PromptImprover evaluation in parallel across all prompts
  - [ ] [5] Run PromptImprover for each prompt_data entry in parallel
  - [ ] [5] Add progress tracking for parallel runs
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

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     main.py (CLI entrypoint)              │
│   $ poetry run app [--job-id <id>] [--action <name>]     │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                   JobScheduler                           │
│  Iterates active jobs, routes to correct job handler     │
│  ┌────────────┬────────────┬──────────────┬───────────┐  │
│  │YouTube     │YouTube     │YouTube Stats │Prompt     │  │
│  │ChannelJob  │VideoJob    │UpdaterJob    │Suggester  │  │
│  └─────┬──────┴─────┬──────┴──────┬───────┴─────┬─────┘  │
│        │            │             │             │        │
│  ┌─────▼────┐ ┌─────▼──────┐ ┌───▼────┐ ┌─────▼─────┐  │
│  │Generator │ │Generator   │ │Gen.    │ │Gen.       │  │
│  │ Layer    │ │ Layer      │ │ Layer  │ │ Layer     │  │
│  └─────┬────┘ └─────┬──────┘ └───┬────┘ └─────┬─────┘  │
│        │            │             │             │        │
│  ┌─────▼────────────▼─────────────▼─────────────▼─────┐  │
│  │                   Manager Layer                     │  │
│  │    (JobManager, YouTubeChannelManager,              │  │
│  │     YouTubeVideoManager, PlatformManager,           │  │
│  │     PromptManager, DataManager)                     │  │
│  └─────────────────────┬───────────────────────────────┘  │
│                        │                                  │
│  ┌─────────────────────▼───────────────────────────────┐  │
│  │  Database Layer (DynamoDB + Moto mock)              │  │
│  │  S3 Storage                                         │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│                     FastAPI Dashboard                      │
│  backend/api/main.py  │  $ poetry run dev                  │
│  Routes: /api/v1/jobs, /api/v1/channel, /api/v1/prompts    │
│          /api/v1/data, /api/v1/health                      │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│  Agent / AI Layer                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐  │
│  │Text Gen. │ │Image Gen.│ │Speech Gen│ │Video Gen.   │  │
│  │OpenAI    │ │Qwen      │ │Qwen TTS  │ │Manus (scaf) │  │
│  │DeepSeek  │ │Grok      │ │Resemble  │ │             │  │
│  │Grok      │ │OpenRouter│ │          │ │             │  │
│  │Perplexity│ │(FLUX)    │ │          │ │             │  │
│  │Qwen      │ │          │ │          │ │             │  │
│  │OpenRouter│ │          │ │          │ │             │  │
│  └──────────┘ └──────────┘ └──────────┘ └─────────────┘  │
│         │              ┌──────────────────────────┐       │
│         └──────────────┤  GeneralAgent (Orchestr.)│       │
│   ┌──────────────┐     │  - Jinja2 prompt render  │       │
│   │Prompt Agents │     │  - Message DB persistence│       │
│   │- Summarize   │     │  - Structured output     │       │
│   │- Metadata    │     │  - Reinvoke / iteration  │       │
│   │- Community   │     │  - Offline mock mode     │       │
│   │- Thumbnail   │     └──────────────────────────┘       │
│   │- Twitter     │                                        │
│   └──────────────┘                                        │
└───────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Category | Tech |
|---|---|
| **Language** | Python 3.13+ |
| **Package Manager** | Poetry |
| **Framework** | FastAPI (Uvicorn) |
| **Database** | DynamoDB (via boto3) |
| **Object Storage** | S3 (via boto3) |
| **AI Orchestration** | LangChain, LangGraph |
| **Prompt Engine** | Jinja2 templates |
| **Dashboard** | NiceGUI |
| **CI** | GitHub Actions (Python 3.13 & 3.14 matrix) |
| **Testing** | Pytest + pytest-cov + tox |
| **Linting** | Black, Ruff, isort, flake8, Mypy, deadcode |

---

## Project Structure

```
backend.completeautomate/
├── main.py                           # CLI entrypoint (scheduler)
├── pyproject.toml                    # Poetry config + tool settings
├── Makefile                          # Dev commands (test, lint, format, etc.)
├── pytest.ini                        # Pytest markers & config
├── tox.ini                           # Tox config
├── .flake8                           # Flake8 config
├── .gitignore
│
├── backend/
│   ├── ai/                           # AI provider wrappers
│   │   ├── text_generation/          #   OpenAI, DeepSeek, Grok, Perplexity, Qwen, OpenRouter
│   │   ├── image_generation/         #   Qwen, Grok, OpenRouter (FLUX)
│   │   ├── speech_generation/        #   Qwen TTS, Resemble
│   │   └── video_generation/         #   Manus (scaffolded)
│   │
│   ├── api/                          # FastAPI route handlers
│   │   ├── main.py                   #   FastAPI app, CORS, lifespan
│   │   ├── channel/channel_api.py    #   YouTube channel endpoints
│   │   ├── jobs/jobs_api.py          #   Job CRUD
│   │   ├── data/data_api.py          #   Data upload/download
│   │   ├── prompts/prompts_api.py    #   Prompt management
│   │   └── health/health_api.py      #   Health check
│   │
│   ├── config/                       # App configuration
│   │   ├── env.py                    #   Environment variables (Env class)
│   │   ├── session.py               #   AWS session + offline bootstrapping
│   │   └── logging_config.py        #   Rotating file + console logging
│   │
│   ├── data/                         # Pydantic/dataclass data models
│   │   ├── job.py                    #   JobData, JobDataResponse
│   │   ├── prompt.py                 #   PromptDBData, PromptVersionDBData
│   │   ├── platform.py               #   PlatformDBData (YouTube video/channel)
│   │   ├── youtube_video.py          #   YouTubeVideoDBData, metadata, thumbnails
│   │   ├── youtube_channel.py        #   YouTubeChannelDBData
│   │   ├── youtube_short.py          #   YouTubeShort data
│   │   ├── image.py                  #   ImagePromptData
│   │   ├── s3.py                     #   S3Data
│   │   ├── message.py                #   MessageDBData (agent conversations)
│   │   └── task.py                   #   Task data models
│   │
│   ├── database/                     # DynamoDB access layer
│   │   ├── base_database.py          #   Abstract base
│   │   ├── dynamo_database.py        #   DbManager (DynamoDB client wrapper)
│   │   ├── job/job_database.py       #   Job CRUD
│   │   ├── platform/                 #   Platform DB operations
│   │   ├── prompt/                   #   Prompt CRUD
│   │   ├── youtube/                  #   YouTube channel/video DB
│   │   ├── agent/                    #   Agent message DB
│   │   └── mocked/                   #   Mocked DB for offline mode
│   │
│   ├── enum/                         # Enumerations
│   │   ├── job.py                    #   JobTypeEnum, JobsStatusEnum
│   │   ├── ai.py                     #   AIModelEnum, AIImageModelEnum, etc.
│   │   ├── youtube.py               #   YouTubeVideoTaskEnum, YouTubeVideoStatusEnum
│   │   ├── platform.py              #   PlatformEnum
│   │   ├── prompt.py                #   PromptTaskEnum, PromptStatusEnum
│   │   ├── action.py                #   ActionEnum (CLI actions)
│   │   ├── db_keys.py               #   DynamoDB key names
│   │   ├── s3.py                    #   S3ContentTypeEnum
│   │   ├── image.py                 #   Image enums
│   │   ├── team.py                  #   TeamEnum (team roles)
│   │   └── action.py                #   ActionEnum
│   │
│   ├── exception/                    # AppException
│   │
│   ├── factory/                      # Test data factories (Faker-backed)
│   │   ├── common.py                 #   fake_date(), fake_uuid(), fake_url()
│   │   ├── job_factory.py
│   │   ├── platform_factory.py
│   │   ├── youtube_channel_factory.py
│   │   ├── youtube_video_factory.py
│   │   ├── youtube_api_factory.py
│   │   ├── agent_response_factory.py
│   │   └── s3_factory.py
│   │
│   ├── generator/                    # Domain generators (workflow logic)
│   │   ├── base_generator.py         #   Abstract base generator
│   │   ├── youtube/
│   │   │   ├── youtube_channel_creator.py   # Onboarding, channel sync, video checker
│   │   │   ├── youtube_video_generator.py   # Full video pipeline (7 tasks)
│   │   │   ├── youtube_short_generator.py   # Shorts (placeholder)
│   │   │   └── youtube_stats_updater.py     # Periodic stats refresh
│   │   ├── prompt/
│   │   │   └── prompt_reviewer.py           # Prompt improvement loop
│   │   └── response_format/                 # Typed AI response schemas
│   │       ├── youtube_video_analyzer_response.py
│   │       ├── youtube_video_community_posts_response.py
│   │       └── image_prompt_response.py
│   │
│   ├── helper/                       # Utility helpers
│   │   └── folder_helper/
│   │       └── folder_helper.py      #   File/path utilities, pickle helpers
│   │
│   ├── integration/                  # External service adapters
│   │   ├── youtube/
│   │   │   ├── youtube_api.py        #   YouTube Data API v3 client
│   │   │   ├── youtube_auth.py       #   OAuth 2.0 flow
│   │   │   ├── youtube_studio_post.py #   Community posts via Studio
│   │   │   └── mock_youtube_api.py   #   Mock for offline/testing
│   │   ├── storage/
│   │   │   └── s3_storage.py         #   S3 upload/download/list/delete
│   │   └── agent/
│   │       └── general_agent.py      #   Agent orchestrator (invoke, reinvoke, generate)
│   │
│   ├── jobs/                         # Job handlers (routers)
│   │   ├── base_job.py               #   Abstract base job
│   │   ├── youtube_channel_job.py    #   Channel onboarding + sync + video checker
│   │   ├── youtube_video_job.py      #   Video pipeline
│   │   ├── youtube_short_job.py      #   Shorts (placeholder)
│   │   ├── youtube_stats_updater_job.py  # Periodic stats sync
│   │   ├── prompt_suggester_job.py   #   Prompt improvement
│   │   └── no_job.py                #   Fallback for unknown job types
│   │
│   ├── jobs_scheduler.py             # Scheduler loop + job routing
│   │
│   ├── manager/                      # Business logic managers
│   │   ├── job_manager.py            #   Job CRUD + status transitions
│   │   ├── job_scheduler_manager.py  #   Scheduler state management
│   │   ├── youtube_video_manager.py  #   Video data CRUD
│   │   ├── youtube_channel_manager.py #   Channel data CRUD
│   │   ├── platform_manager.py       #   Platform data CRUD
│   │   ├── prompt_manager.py         #   Prompt CRUD
│   │   ├── data_manager.py           #   S3 ↔ local data sync
│   │   ├── action_manager.py         #   CLI action handler
│   │   ├── start_up_manager.py       #   Startup/shutdown lifecycle
│   │   ├── health_manager.py         #   Health checks
│   │   └── transform.py              #   Data transformation
│   │
│   ├── prompt_agent/                 # Domain-specific AI prompt agents
│   │   ├── agent/
│   │   │   ├── base_agent.py         #   Abstract agent with prompt DB access
│   │   │   ├── langgraph_agent.py    #   LangGraph state machine agent
│   │   │   └── langchain_agent.py    #   LangChain agent (stub)
│   │   ├── youtube_video_summarization/
│   │   ├── youtube_video_metadata/
│   │   ├── youtube_video_community_post/
│   │   ├── youtube_video_twitter_post/
│   │   ├── youtube_thumbnail_image_generation_prompt/
│   │   └── youtube_short_speech_generation_prompt/
│   │
│   └── services/                     # Service layer
│       ├── agent_service.py          #   AgentService, AgentImageService
│       ├── email_service.py          #   SMTP email (Zoho)
│       └── video_service.py          #   AgentVideoService
│
├── example/                          # Standalone provider examples
│   ├── qwen_speech_full_expression_example.py
│   ├── manus_video_example.py
│   └── resemble_speech_example.py
│
├── tests/                            # Test suite
│   ├── conftest.py
│   ├── test_api_main.py
│   ├── test_channel_api.py
│   ├── test_data_manager.py
│   ├── test_data_models.py
│   ├── test_email_service.py
│   ├── test_enums.py
│   ├── test_folder_helper.py
│   ├── test_general_agent.py
│   ├── test_integration.py
│   ├── test_jobs.py
│   ├── test_langgraph_agent.py
│   ├── test_manus_video_generator.py
│   ├── test_prompt_manager.py
│   ├── test_qwen_speech_generator.py
│   ├── test_resemble_speech_generator.py
│   ├── test_s3_storage.py
│   ├── test_session.py
│   ├── test_video_service.py
│   ├── test_youtube_api.py
│   ├── test_youtube_channel_offline.py
│   └── test_agent_service.py
│
└── .github/
    ├── workflows/ci.yml              # CI pipeline
    ├── copilot-instructions.md        # Copilot project context
    └── agents/poetry-fastapi-dev.agent.md  # Copilot dev agent
```

---

## Prerequisites

- Python `>=3.13,<3.15`
- [Poetry](https://python-poetry.org/)
- AWS account with DynamoDB + S3 (optional — offline mode available)
- API keys for desired AI providers

---

## Setup

```sh
git clone https://github.com/vimalmenon/backend.completeautomate.git
cd backend.completeautomate

# Install dotenv plugin (reads .env automatically)
poetry self add poetry-plugin-dotenv

# Install all dependencies
poetry install
```

---

## Configuration (Environment Variables)

Create a `.env` file in the project root:

```env
# Required
VERSION=0.0.1
COMPANY_NAME=Complete Automate

# AWS
AWS_CLIENT_ID=your_aws_key
AWS_SECRET=your_aws_secret
AWS_REGION=us-east-1
AWS_SECRET_MANAGER=arn:aws:secretsmanager:...
AWS_TABLE=your_dynamodb_table_name
AWS_S3_BUCKET=your_s3_bucket_name

# AI Providers
GROK_API_KEY=xai-...
PPLX_API_KEY=pplx-...
OPEN_ROUTE_API_KEY=sk-or-...
OPENAI_API_KEY=sk-...
QWEN_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...
RESEMBLE_API_KEY=...

# YouTube
YOUTUBE_API_KEY=your_youtube_api_key
YOUTUBE_CHANNEL_ID=@your_channel

# SMTP (for email service)
SMTP_USERNAME=hello@completeautomate.com
SMTP_PASSWORD=your_password

# Optional
CORS_ALLOWED_ORIGINS=http://localhost:8080,http://localhost:3000
OFFLINE=false
```

---

## Running the App

### Job Scheduler

```sh
# Run all active jobs
poetry run app

# Run a specific job by ID
poetry run app --job-id <uuid>

# Run with CLI action
poetry run app --action show_jobs
```

### FastAPI Dashboard

```sh
poetry run dev
```

Opens at `http://127.0.0.1:8000` with auto-reload.

### NiceGUI Dashboard

```sh
poetry run python -m gui
```

Opens at `http://localhost:8080`.

---

## CLI Actions

| Action | Description |
|---|---|
| `poetry run app --action show_jobs` | Display all jobs in a table |
| `poetry run app --action transform` | Run one-time data transformation |
| `poetry run app --action restore_from_s3` | Restore database from S3 backups |
| `poetry run app --action download_to_local` | Download DB data to local pickle files |
| `poetry run app --action restore_from_local` | Restore database from local pickle files |

---

## YouTube Pipeline

The YouTube pipeline is the core automation workflow. Jobs and tasks flow from onboarding through video processing to publishing.

```
[Dashboard] Create: YouTubeChannelOnboarding job
│
├── Job: YouTubeChannel  (sync channel info from API)
│
└── Job: YouTubeChannelVideoChecker  (find new videos)
      │
      └── Job: YouTubeVideo (per-video pipeline)
            ├── Task: YouTubeVideoStart
            │     Fetch video from API → store in DB
            │     Includes transcript capture if available
            │
            ├── Task: YouTubeVideoFixTranscript  [REVIEW]
            │     AI summarization of transcript
            │     User reviews/edits transcript
            │
            ├── Task: YouTubeVideoMetadataSelection  [REVIEW]
            │     AI generates title/description/tag suggestions
            │     User selects best option
            │     Updates YouTube metadata + generates thumbnails
            │
            ├── Task: YouTubeVideoThumbnailSelection  [REVIEW]
            │     AI generates thumbnail prompt suggestions
            │     Images generated via Qwen/Grok/FLUX → uploaded to S3
            │     User selects thumbnail → uploaded to YouTube
            │     Community post generated via AI
            │
            └── Task: YouTubeVideoComplete
                  Terminal state
```

**Key behavior:**
- `[REVIEW]` stages pause and wait for user action in the dashboard
- Videos older than 2 weeks are skipped automatically
- Failed jobs auto-retry up to 4 times before marking FAILED
- YouTube Stats Updater runs periodically (every 2 days) to refresh channel/video stats
- Channel + video stats history is preserved (appended, not overwritten)

---

## AI Provider Matrix

### Text Generation

| Provider | Models | LangChain Adapter |
|---|---|---|
| **OpenAI** | gpt-5-nano, gpt-4o-mini, gpt-5 | `ChatOpenAI` |
| **DeepSeek** | deepseek-chat, deepseek-reasoner | `ChatDeepSeek` |
| **Grok (xAI)** | grok-3 | `ChatXAI` |
| **Perplexity** | sonar | `ChatPerplexity` |
| **Qwen** | qwen3.5-plus (w/ thinking) | `ChatQwen` |
| **OpenRouter** | qwen/qwen3-max-thinking, qwen3-coder, qwen3-coder:free | `ChatOpenAI` (custom base_url) |

### Image Generation

| Provider | Model | Method |
|---|---|---|
| **Qwen** | qwen-image-max | DashScope MultiModalConversation |
| **Grok** | grok-imagine-image | xAI API |
| **OpenRouter** | black-forest-labs/flux.2-flex | OpenRouter + FLUX |

### Speech Generation

| Provider | Model | Method |
|---|---|---|
| **Qwen** | qwen3-tts-instruct-flash-realtime | DashScope WebSocket TTS |
| **Resemble** | resemble-1 | Resemble SDK |

### Video Generation

| Provider | Model | Status |
|---|---|---|
| **Manus** | manus-avatar-v1 | Scaffolded (client adapter needed) |

---

## Prompt Management System

Prompts are versioned and stored in DynamoDB. Each prompt has:

- **Task type** (e.g., `YouTubeVideoSummarization`, `YouTubeVideoMetadata`)
- **Multiple versions** with full history
- **Active version selector** per prompt
- **AI model assignment** per version (each prompt version can use a different LLM)
- **Jinja2 templates** with `{{ variable }}` rendering
- **Prompt data** for evaluation/testing
- **Reflection message** for AI self-improvement

Prompt tasks:

| Task | Purpose |
|---|---|
| `YouTubeVideoSummarization` | Summarize video transcript |
| `YouTubeVideoMetadata` | Generate title/description/tags |
| `YouTubeVideoCommunityPost` | Write YouTube community posts |
| `YouTubeVideoTwitterPost` | Draft tweet threads (TODO) |
| `YouTubeThumbnailImageGenerationPrompt` | Generate image prompts for thumbnails |
| `YouTubeShortSpeechGenerationPrompt` | Generate speech for YouTube Shorts |

---

## GeneralAgent Orchestrator

The `GeneralAgent` is the central AI invocation engine:

1. Loads prompt templates from the Prompt DB
2. Renders Jinja2 templates with task-specific data
3. Selects the configured AI model for that prompt version
4. Optionally enforces structured JSON output via Pydantic response formats
5. Persists conversation history to DynamoDB (AgentMessageDB)
6. Supports `reinvoke()` for iterative refinement
7. Provides clean mock responses in offline mode

---

## Offline Mode

Set `OFFLINE=true` in `.env` to run without AWS credentials:

- DynamoDB is replaced by Moto mock (in-memory)
- S3 is replaced by Moto mock
- AI responses return structured mock data instead of calling live APIs
- YouTube API is replaced by `MockYouTubeAPI`
- Data can be persisted as local pickle files and restored later

```sh
OFFLINE=true poetry run app
```

The offline dashboard also includes a runtime toggle switch.

---

## Data Backup & Sync

The `DataManager` handles syncing between DynamoDB and S3/local pickle files:

| Action | What it does |
|---|---|
| `restore_from_s3` | Download pickle files from S3 → upload to DynamoDB |
| `download_to_local` | Export DynamoDB data → pickle files → upload to S3 |
| `restore_from_local` | Upload local pickle files → DynamoDB |
| `start_up_script` | On startup, download client_secret.json and token.pickle from S3 |

Synced data sets:
- YouTube videos
- YouTube channels
- Prompts
- Jobs
- Platform data
- YouTube OAuth credentials (client_secret.json, token.pickle)
- Thumbnail images

---

## Development Commands

```sh
make install       # Poetry install
make run           # Run scheduler (poetry run app)
make test          # Pytest + coverage
make test-quick    # Pytest without coverage
make lint          # Flake8
make type-check    # Mypy
make format        # Black (targeted paths)
make format-check  # Black check only
make isort-check   # isort check
make format-all    # Black + Ruff --fix + isort
make check         # format-check + isort-check + lint + type-check + test
make fix           # format-all
make deadcode      # Dead code analyzer
make clean         # Remove cache and build files
make ci            # CI target (runs all, continues on failure)
```

---

## Testing

```sh
# Run all tests with coverage
poetry run pytest tests/ -v --cov=backend --cov-report=term-missing

# Run specific markers
poetry run pytest -m unit
poetry run pytest -m integration

# Run a specific test file
poetry run pytest tests/test_s3_storage.py

# Offline mode tests
OFFLINE=true poetry run pytest tests/test_s3_storage.py tests/test_integration.py

# Via tox
poetry run tox -e pytest
```

### Test Markers

| Marker | Scope |
|---|---|
| `unit` | Fast, isolated unit tests |
| `integration` | Tests requiring external services |
| `slow` | Long-running tests |
| `aws` | Tests requiring real AWS credentials |
| `youtube` | Tests requiring YouTube API |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| **Jobs** | | |
| GET | `/api/v1/jobs` | List all jobs |
| GET | `/api/v1/jobs/{job_id}` | Get job details |
| POST | `/api/v1/jobs` | Create a new job |
| PUT | `/api/v1/jobs/{job_id}` | Update job status/data |
| DELETE | `/api/v1/jobs/{job_id}` | Delete a job |
| **Channels** | | |
| GET | `/api/v1/channel` | List YouTube channels |
| GET | `/api/v1/channel/{channel_id}` | Get channel details |
| GET | `/api/v1/channel/{channel_id}/videos` | List videos for channel |
| **Prompts** | | |
| GET | `/api/v1/prompts` | List all prompts |
| GET | `/api/v1/prompts/{prompt_id}` | Get prompt details |
| PUT | `/api/v1/prompts/{prompt_id}` | Update prompt |
| **Data** | | |
| GET | `/api/v1/data` | List data items |
| GET | `/api/v1/data/{data_id}` | Get data details |
| **Health** | | |
| GET | `/api/v1/health` | Health check |

---

## Team

Defined in `TeamEnum`:

| Role | Name |
|---|---|
| Owner | Vimal Menon |
| Researcher | Christopher Morris |
| Social Media Manager | Samantha Rogers |
| Manager | Elara Turner |
| Graphic Designer | Iris Cooper |
| Content Writer | Sam Morris |

---

## Thumbnail Size Handling

YouTube rejects thumbnails larger than 2 MB. The backend automatically:

1. Checks image size before upload
2. Converts to JPEG if oversized
3. Progressively resizes until under the 2 MB limit
4. Cleans up temp files after upload

---

## YouTube OAuth

Some operations need OAuth. The app looks for:

- `backend/output/json/client_secret.json` — OAuth client credentials
- `backend/output/pickle/token.pickle` — Cached OAuth token

These are synced from S3 on startup. If no token exists, the app launches the OAuth flow on the first authenticated YouTube request.

---

## Contributing

1. Branch from `main`
2. Make focused changes
3. Run `make check` before committing
4. Open a PR — CI runs Black, Flake8, Mypy, and Pytest
