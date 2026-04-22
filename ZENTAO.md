# ZENTAO.md — Software-Specific SOP for CLI-Anything ZenTao Harness

## Software Overview

**ZenTao** is an open-source project management software (PHP + MySQL) that covers:
- Product management
- Project/execution management (Scrum, Waterfall, Kanban)
- Requirement/story tracking
- Task management
- Bug tracking
- Test case management
- Build/release management

Official site: https://www.zentao.pm/

## Phase 1: Codebase Analysis

### Backend Engine Identification

ZenTao is a web-based PHP application with:
- **REST-like API** — accessible via `/api.php?module=...&method=...`
- **MySQL database** — direct read access possible for reporting
- **Token-based authentication** — MD5-based session tokens
- **Module-based MVC architecture** — each feature is a module (product, project, story, task, bug, testcase, build)

### GUI Actions → API Calls Mapping

| GUI Action | API Module | API Method |
|------------|-----------|------------|
| View products | product | browse / all |
| Create product | product | create |
| Edit product | product | edit |
| Delete product | product | delete |
| View projects | project | browse |
| Create project | project | create |
| Edit project | project | edit |
| Delete project | project | delete |
| View stories | story | browse |
| Create story | story | create |
| Edit story | story | edit |
| Close story | story | close |
| Activate story | story | activate |
| View tasks | task | browse |
| Create task | task | create |
| Edit task | task | edit |
| Start task | task | start |
| Finish task | task | finish |
| Close task | task | close |
| Cancel task | task | cancel |
| View bugs | bug | browse |
| Create bug | bug | create |
| Edit bug | bug | edit |
| Resolve bug | bug | resolve |
| Activate bug | bug | activate |
| Close bug | bug | close |
| View test cases | testcase | browse |
| Create test case | testcase | create |
| Edit test case | testcase | edit |
| View builds | build | browse |
| Create build | build | create |
| Delete build | build | delete |

### Data Model

- **Storage**: MySQL database with custom DAO layer
- **API format**: JSON responses via `/api.php`
- **Authentication**: Cookie-based session (`zentaosid`) or token header
- **Token generation**: `md5(md5(password) + rand + account)`

### Existing CLI Tools

ZenTao ships with its own PHP CLI for maintenance tasks, but the primary automation interface is the HTTP API.

## Phase 2: CLI Architecture Design

### Interaction Model

**Both modes supported**:
1. **Stateful REPL** — Interactive session for exploration and multi-step workflows
2. **Subcommand CLI** — One-shot operations for scripting and agent automation

### Command Groups

| Group | Purpose |
|-------|---------|
| `connect` | Test server connectivity |
| `product` | Product CRUD |
| `project` | Project/execution CRUD |
| `story` | Story/requirement lifecycle |
| `task` | Task lifecycle (create → start → finish → close) |
| `bug` | Bug lifecycle (create → resolve → close, with reopen) |
| `testcase` | Test case management |
| `build` | Build/release management |

### State Model

- **No persistent local state** — all state is stored on the ZenTao server
- **REPL session** maintains connection via `ZenTaoBackend` instance
- **Authentication** cached in session (session ID / token)

### Output Format

- **Human-readable**: Styled success/error messages with key-value display
- **Machine-readable**: `--json` flag outputs full JSON response

## Phase 3: Implementation

### Data Layer

The data layer is the `ZenTaoBackend` class in `utils/zentao_backend.py`:
- Handles HTTP API communication
- Manages authentication (token generation, session cookies)
- Provides typed methods for each API operation
- Returns raw API responses as dicts

### Core Modules

Each domain has a core module that wraps backend calls with sensible defaults:

| Module | Functions |
|--------|-----------|
| `core/product.py` | list, get, create, update, delete |
| `core/project.py` | list, get, create, update, delete |
| `core/story.py` | list, get, create, update, close, activate |
| `core/task.py` | list, get, create, update, start, finish, close, cancel |
| `core/bug.py` | list, get, create, update, resolve, activate, close |
| `core/testcase.py` | list, get, create, update |
| `core/build.py` | list, get, create, delete |

### CLI Entry Point

`zentao_cli.py` — Click-based CLI with:
- Global `--json` flag for machine-readable output
- Global `--url`, `--user`, `--password`, `--token` for authentication
- `invoke_without_command=True` → defaults to REPL
- Command groups for each domain

### REPL

Uses `ReplSkin` from `utils/repl_skin.py`:
- Branded startup banner with ZenTao accent color
- Prompt with context indicator
- Command registry for interactive dispatch
- History and auto-suggest via prompt_toolkit

### Error Handling

- `ZenTaoConfigError` — missing/invalid configuration
- `ZenTaoAPIError` — API call failures (HTTP errors, parse errors)
- Clear error messages with configuration instructions

## Phase 4: Test Planning

See `tests/TEST.md` for the complete test plan.

### Test Layers

1. **Unit tests** (`test_core.py`) — Mocked backend, ~25 tests
2. **E2E tests** (`test_full_e2e.py`) — Real CLI subprocess, ~12 tests
3. **Integration tests** — Require live ZenTao server (skip if unavailable)

## Key Design Decisions

### Why HTTP API over direct database?

- **API is the official interface** — stable, versioned, documented
- **Database is internal** — schema changes between versions
- **API handles authentication** — no need to manage DB credentials
- **Database access is read-only** in the backend (optional optimization)

### Why no local state?

- **ZenTao is server-side** — all data lives on the server
- **Multi-user system** — changes by others are immediately visible
- **No offline mode needed** — agents always work with current server state

### Authentication strategy

1. **Token-based** (preferred) — use pre-generated session token
2. **User/password** — auto-generate token via login page
3. **Environment variables** — `ZENTAO_URL`, `ZENTAO_USER`, `ZENTAO_PASSWORD`, `ZENTAO_TOKEN`

## Common Agent Workflows

### 1. Create a new sprint and populate it

```
# 1. Create project
cli-anything-zentao project create "Sprint 24" "SP24" --model scrum

# 2. Add stories
cli-anything-zentao story create <product_id> "User login" --pri 1
cli-anything-zentao story create <product_id> "Dashboard" --pri 2

# 3. Create tasks for each story
cli-anything-zentao task create <exec_id> "Implement login API" --type devel
cli-anything-zentao task create <exec_id> "Write login tests" --type test

# 4. Start working
cli-anything-zentao task start <task_id>
```

### 2. Bug triage workflow

```
# 1. List active bugs
cli-anything-zentao --json bug list <product_id> --browse-type active

# 2. Review a specific bug
cli-anything-zentao bug get <bug_id>

# 3. Resolve confirmed bugs
cli-anything-zentao bug resolve <bug_id> --resolution fixed

# 4. Close resolved bugs
cli-anything-zentao bug close <bug_id>
```

### 3. Release preparation

```
# 1. Create release build
cli-anything-zentao build create <product_id> "v2.1.0" --builder ci-bot

# 2. Create test cases for new features
cli-anything-zentao testcase create <product_id> "Verify new feature"

# 3. Check for open bugs
cli-anything-zentao bug list <product_id> --browse-type active
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ZENTAO_URL` | Yes | Base URL of ZenTao instance |
| `ZENTAO_USER` | Conditional | Username (if not using token) |
| `ZENTAO_PASSWORD` | Conditional | Password (if not using token) |
| `ZENTAO_TOKEN` | Conditional | Pre-generated session token |
| `CLI_ANYTHING_NO_COLOR` | No | Disable colored output |

## Limitations

- **No batch operations** — each API call handles one item
- **No file attachments** — API doesn't support file uploads via this CLI
- **No real-time notifications** — polling required for updates
- **Pagination required** for large datasets (use `--page` and `--per-page`)
