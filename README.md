# cli-anything-zentao

CLI interface for the [ZenTao](https://www.zentao.pm/) project management system, built using the [CLI-Anything](https://github.com/HKUDS/CLI-Anything) methodology.

## Overview

This CLI lets AI agents and developers interact with ZenTao's project management features entirely from the command line — no browser or GUI required. It supports both one-shot subcommand mode and an interactive REPL.

### Features

- **Product management** — create, list, update, delete products
- **Project management** — sprint/project CRUD
- **Story/requirement management** — full lifecycle (create, edit, close, activate)
- **Task management** — create, edit, start, finish, close, cancel
- **Bug management** — create, edit, resolve, activate, close
- **Test case management** — create, update, list
- **Build management** — create, list, delete
- **`--json` flag** — machine-readable output for agent consumption
- **Interactive REPL** — with history, auto-suggest, and branded prompt

## Installation

### Prerequisites

- Python 3.8+
- A running ZenTao instance (accessible via HTTP)

### Install from source

```bash
cd /path/to/agent-harness/
pip install -e .
```

### Install with REPL support

```bash
pip install -e ".[repl]"
```

### Install with dev dependencies

```bash
pip install -e ".[dev]"
```

## Configuration

Set environment variables to connect to your ZenTao server:

```bash
export ZENTAO_URL="http://localhost/zentao"
export ZENTAO_USER="admin"
export ZENTAO_PASSWORD="your_password"
```

Alternatively, pass credentials via CLI flags:

```bash
cli-anything-zentao --url http://localhost/zentao --user admin --password xxx
```

Or use a pre-generated session token:

```bash
export ZENTAO_TOKEN="your-session-token"
```

## Usage

### Interactive REPL (default)

```bash
cli-anything-zentao
```

This launches an interactive session with a branded prompt:

```
◆ cli-anything · ZenTao    v1.0.0
◇ Install:   npx skills add HKUDS/CLI-Anything --skill cli-anything-zentao -g -y
◇ Global skill:  ~/.agents/skills/cli-anything-zentao/SKILL.md

   Type help for commands, quit to exit

   Type help for commands, quit to exit

zentao ❯ products
zentao ❯ create-product "My Product" MP
zentao ❯ quit
```

### Subcommand mode

```bash
# Test connection
cli-anything-zentao connect

# List products (JSON output)
cli-anything-zentao --json product list

# Create a project
cli-anything-zentao project create "Sprint 1" "SP1" \
  --model scrum --type sprint \
  --begin 2025-01-01 --end 2025-01-31

# Create a story
cli-anything-zentao story create 1 "Login feature" \
  --spec "As a user I want to login" --pri 1

# Create a task
cli-anything-zentao task create 5 "Write unit tests" \
  --type devel --pri 2 --assigned-to dev1

# Create a bug
cli-anything-zentao bug create 1 "Null pointer on login" \
  --severity 2 --pri 1 --type codeerror

# Resolve a bug
cli-anything-zentao bug resolve 42 --resolution fixed

# Create a test case
cli-anything-zentao testcase create 1 "Verify login" \
  --steps "1. Enter creds 2. Click login" --pri 1

# Create a build
cli-anything-zentao build create 1 "v1.0.0" \
  --builder ci-bot --desc "Release build"
```

### JSON output

All commands support the `--json` flag for machine-readable output:

```bash
cli-anything-zentao --json product list
```

## Command Reference

| Command | Description |
|---------|-------------|
| `connect` | Test connection to ZenTao server |
| `product list` | List all products |
| `product get <id>` | Get product details |
| `product create <name> <code>` | Create a new product |
| `product update <id>` | Update a product |
| `product delete <id>` | Delete a product |
| `project list` | List all projects |
| `project get <id>` | Get project details |
| `project create <name> <code>` | Create a new project |
| `project update <id>` | Update a project |
| `project delete <id>` | Delete a project |
| `story list <product_id>` | List stories for a product |
| `story get <id>` | Get story details |
| `story create <product_id> <title>` | Create a story |
| `story update <id>` | Update a story |
| `story close <id>` | Close a story |
| `story activate <id>` | Activate a closed story |
| `task list <execution_id>` | List tasks for an execution |
| `task get <id>` | Get task details |
| `task create <exec_id> <name>` | Create a task |
| `task update <id>` | Update a task |
| `task start <id>` | Start a task |
| `task finish <id>` | Finish a task |
| `task close <id>` | Close a task |
| `task cancel <id>` | Cancel a task |
| `bug list <product_id>` | List bugs for a product |
| `bug get <id>` | Get bug details |
| `bug create <product_id> <title>` | Create a bug |
| `bug update <id>` | Update a bug |
| `bug resolve <id>` | Resolve a bug |
| `bug activate <id>` | Reopen a resolved bug |
| `bug close <id>` | Close a bug |
| `testcase list <product_id>` | List test cases |
| `testcase get <id>` | Get test case details |
| `testcase create <product_id> <title>` | Create a test case |
| `testcase update <id>` | Update a test case |
| `build list` | List builds |
| `build get <id>` | Get build details |
| `build create <product_id> <name>` | Create a build |
| `build delete <id>` | Delete a build |

## Testing

### Run unit tests (no server required)

```bash
python -m pytest cli_anything/zentao/tests/test_core.py -v
```

### Run E2E tests (requires ZenTao server)

```bash
export ZENTAO_URL="http://localhost/zentao"
export ZENTAO_USER="admin"
export ZENTAO_PASSWORD="your_password"
python -m pytest cli_anything/zentao/tests/ -v
```

### Run with force-installed mode

```bash
CLI_ANYTHING_FORCE_INSTALLED=1 python -m pytest cli_anything/zentao/tests/ -v
```

## AI Agent Integration

Install the SKILL.md for AI agent discovery:

```bash
npx skills add HKUDS/CLI-Anything --skill cli-anything-zentao -g -y
```

The skill file provides agents with complete command reference and usage examples.

## License

MIT
