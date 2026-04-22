#!/usr/bin/env python3
"""cli-anything-zentao: CLI interface for ZenTao project management system.

Usage:
    cli-anything-zentao [OPTIONS] COMMAND [ARGS]...

Global options:
    --json          Output in JSON format (machine-readable)
    --url URL       ZenTao server URL (or ZENTAO_URL env var)
    --user USER     Username (or ZENTAO_USER env var)
    --password PASS Password (or ZENTAO_PASSWORD env var)
    --token TOKEN   Session token (or ZENTAO_TOKEN env var)

Commands:
    connect     Test connection to ZenTao
    product     Product management (list/create/update/delete)
    project     Project management (list/create/update/delete)
    story       Story/requirement management (list/create/edit/close/activate)
    task        Task management (list/create/edit/start/finish/close/cancel)
    bug         Bug management (list/create/edit/resolve/activate/close)
    testcase    Test case management (list/create/update)
    build       Build management (list/create/delete)
    repl        Interactive REPL mode (default when no subcommand given)
"""

import json
import sys
import os
from typing import Optional

import click

from cli_anything.zentao.utils.zentao_backend import (
    ZenTaoBackend, ZenTaoAPIError, ZenTaoConfigError,
)
from cli_anything.zentao.utils.repl_skin import ReplSkin

# Core operations
from cli_anything.zentao.core.project import (
    list_projects, get_project, create_project, update_project, delete_project,
)
from cli_anything.zentao.core.product import (
    list_products, get_product, create_product, update_product, delete_product,
)
from cli_anything.zentao.core.story import (
    list_stories, get_story, create_story, update_story, close_story, activate_story,
)
from cli_anything.zentao.core.task import (
    list_tasks, get_task, create_task, update_task,
    start_task, finish_task, close_task, cancel_task,
)
from cli_anything.zentao.core.bug import (
    list_bugs, get_bug, create_bug, update_bug,
    resolve_bug, activate_bug as activate_bug_op, close_bug as close_bug_op,
)
from cli_anything.zentao.core.testcase import (
    list_testcases, get_testcase, create_testcase, update_testcase,
)
from cli_anything.zentao.core.build import (
    list_builds, get_build, create_build, delete_build,
)


# ── Helpers ───────────────────────────────────────────────────────────

def _make_backend(url: Optional[str], user: Optional[str],
                  password: Optional[str], token: Optional[str]) -> ZenTaoBackend:
    """Create a ZenTaoBackend from CLI options."""
    try:
        return ZenTaoBackend(url=url, user=user, password=password, token=token)
    except ZenTaoConfigError as e:
        raise click.ClickException(str(e))


def _output(result: dict, as_json: bool):
    """Print result as JSON or human-readable table."""
    if as_json:
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # Simple human-readable output
        if "status" in result and result.get("status") in ("success", "ok"):
            click.echo(click.style("✓ Success", fg="green"))
            # Print key fields
            data = result.get("result", result)
            if isinstance(data, dict):
                for key, value in data.items():
                    if value is not None and str(value).strip():
                        click.echo(f"  {click.style(key + ':', fg='cyan')} {value}")
            elif isinstance(data, list):
                click.echo(f"  Found {len(data)} items")
        elif "error" in result:
            click.echo(click.style(f"✗ Error: {result['error']}", fg="red"))
        else:
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))


# ── Main CLI group ────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "as_json", is_flag=True, default=False,
              help="Output in JSON format")
@click.option("--url", default=None,
              help="ZenTao server URL (env: ZENTAO_URL)")
@click.option("--user", default=None,
              help="Username (env: ZENTAO_USER)")
@click.option("--password", default=None,
              help="Password (env: ZENTAO_PASSWORD)")
@click.option("--token", default=None,
              help="Session token (env: ZENTAO_TOKEN)")
@click.pass_context
def cli(ctx, as_json, url, user, password, token):
    """cli-anything-zentao — CLI interface for ZenTao."""
    ctx.ensure_object(dict)
    ctx.obj["as_json"] = as_json
    ctx.obj["url"] = url
    ctx.obj["user"] = user
    ctx.obj["password"] = password
    ctx.obj["token"] = token

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── REPL mode ─────────────────────────────────────────────────────────

@cli.command()
@click.pass_context
def repl(ctx):
    """Interactive REPL mode for ZenTao."""
    as_json = ctx.obj.get("as_json", False)
    url = ctx.obj.get("url")
    user = ctx.obj.get("user")
    password = ctx.obj.get("password")
    token = ctx.obj.get("token")

    skin = ReplSkin("zentao", version="1.0.0")
    skin.print_banner()

    # Build backend
    try:
        backend = _make_backend(url, user, password, token)
    except click.ClickException as e:
        skin.error(str(e))
        skin.info("Set ZENTAO_URL, ZENTAO_USER, ZENTAO_PASSWORD to configure.")
        sys.exit(1)

    # Test connection
    skin.info("Testing connection to ZenTao...")
    conn = backend.test_connection()
    if conn.get("status") == "error":
        skin.error(f"Connection failed: {conn.get('message', 'unknown')}")
        sys.exit(1)
    elif conn.get("status") == "warning":
        skin.warning(f"{conn.get('message', 'unknown')}")
    else:
        skin.success("Connected to ZenTao")

    # Build command registry
    commands = {
        "products": "List products",
        "product <id>": "Get product details",
        "create-product <name> <code>": "Create a product",
        "projects": "List projects",
        "project <id>": "Get project details",
        "create-project <name> <code>": "Create a project",
        "stories <product_id>": "List stories for a product",
        "story <id>": "Get story details",
        "create-story <product_id> <title>": "Create a story",
        "tasks <execution_id>": "List tasks for an execution",
        "task <id>": "Get task details",
        "create-task <exec_id> <name>": "Create a task",
        "start-task <id>": "Start a task",
        "finish-task <id>": "Finish a task",
        "bugs <product_id>": "List bugs for a product",
        "bug <id>": "Get bug details",
        "create-bug <product_id> <title>": "Create a bug",
        "resolve-bug <id>": "Resolve a bug",
        "testcases <product_id>": "List test cases",
        "testcase <id>": "Get test case details",
        "create-testcase <product_id> <title>": "Create a test case",
        "builds": "List builds",
        "build <id>": "Get build details",
        "create-build <product_id> <name>": "Create a build",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    pt_session = skin.create_prompt_session()

    while True:
        try:
            line = skin.get_input(pt_session, context="zentao")
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        if not line.strip():
            continue

        parts = line.strip().split()
        cmd = parts[0].lower()

        if cmd in ("quit", "exit", "q"):
            skin.print_goodbye()
            break
        elif cmd == "help":
            skin.help(commands)
            continue
        elif cmd == "connect":
            conn = backend.test_connection()
            skin.status("Status", conn.get("status", "unknown"))
            skin.status("Message", conn.get("message", ""))
            continue

        try:
            result = _dispatch_repl(backend, parts)
            if as_json:
                click.echo(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                _output(result, False)
        except ZenTaoAPIError as e:
            skin.error(f"API error: {e}")
        except Exception as e:
            skin.error(f"Error: {e}")


def _dispatch_repl(backend: ZenTaoBackend, parts: list) -> dict:
    """Dispatch a REPL command line to the appropriate operation."""
    cmd = parts[0].lower()
    args = parts[1:]

    if cmd == "products":
        return list_products(backend)
    elif cmd == "product":
        return get_product(backend, int(args[0]))
    elif cmd == "create-product":
        return create_product(backend, args[0], args[1])

    elif cmd == "projects":
        return list_projects(backend)
    elif cmd == "project":
        return get_project(backend, int(args[0]))
    elif cmd == "create-project":
        return create_project(backend, args[0], args[1])

    elif cmd == "stories":
        return list_stories(backend, int(args[0]))
    elif cmd == "story":
        return get_story(backend, int(args[0]))
    elif cmd == "create-story":
        return create_story(backend, int(args[0]), args[1])

    elif cmd == "tasks":
        return list_tasks(backend, int(args[0]))
    elif cmd == "task":
        return get_task(backend, int(args[0]))
    elif cmd == "create-task":
        return create_task(backend, int(args[0]), args[1])
    elif cmd == "start-task":
        return start_task(backend, int(args[0]))
    elif cmd == "finish-task":
        return finish_task(backend, int(args[0]))

    elif cmd == "bugs":
        return list_bugs(backend, int(args[0]))
    elif cmd == "bug":
        return get_bug(backend, int(args[0]))
    elif cmd == "create-bug":
        return create_bug(backend, int(args[0]), args[1])
    elif cmd == "resolve-bug":
        return resolve_bug(backend, int(args[0]))

    elif cmd == "testcases":
        return list_testcases(backend, int(args[0]))
    elif cmd == "testcase":
        return get_testcase(backend, int(args[0]))
    elif cmd == "create-testcase":
        return create_testcase(backend, int(args[0]), args[1])

    elif cmd == "builds":
        return list_builds(backend)
    elif cmd == "build":
        return get_build(backend, int(args[0]))
    elif cmd == "create-build":
        return create_build(backend, int(args[0]), args[1])

    else:
        raise ValueError(f"Unknown command: {cmd}")


# ── Connect command ───────────────────────────────────────────────────

@cli.command()
@click.pass_context
def connect(ctx):
    """Test connection to ZenTao server."""
    backend = _make_backend(
        ctx.obj.get("url"), ctx.obj.get("user"),
        ctx.obj.get("password"), ctx.obj.get("token"),
    )
    result = backend.test_connection()
    _output(result, ctx.obj.get("as_json", False))


# ── Product commands ──────────────────────────────────────────────────

@cli.group()
@click.pass_context
def product(ctx):
    """Product management."""
    pass


@product.command("list")
@click.option("--status", default="all", help="Filter: all, noclosed, closed")
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
@click.pass_context
def product_list(ctx, status, page, per_page):
    """List all products."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = list_products(backend, status=status, page=page, per_page=per_page)
    _output(result, ctx.parent.obj.get("as_json", False))


@product.command("get")
@click.argument("product_id", type=int)
@click.pass_context
def product_get(ctx, product_id):
    """Get product details."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = get_product(backend, product_id)
    _output(result, ctx.parent.obj.get("as_json", False))


@product.command("create")
@click.argument("name")
@click.argument("code")
@click.option("--type", "product_type", default="normal")
@click.option("--desc", default="")
@click.option("--po", default="", help="Product Owner account")
@click.pass_context
def product_create(ctx, name, code, product_type, desc, po):
    """Create a new product."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = create_product(backend, name, code,
                            product_type=product_type, desc=desc, po=po)
    _output(result, ctx.parent.obj.get("as_json", False))


@product.command("update")
@click.argument("product_id", type=int)
@click.option("--name", default=None)
@click.option("--desc", default=None)
@click.pass_context
def product_update(ctx, product_id, name, desc):
    """Update an existing product."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    kwargs = {}
    if name is not None:
        kwargs["name"] = name
    if desc is not None:
        kwargs["desc"] = desc
    result = update_product(backend, product_id, **kwargs)
    _output(result, ctx.parent.obj.get("as_json", False))


@product.command("delete")
@click.argument("product_id", type=int)
@click.pass_context
def product_delete(ctx, product_id):
    """Delete a product."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = delete_product(backend, product_id)
    _output(result, ctx.parent.obj.get("as_json", False))


# ── Project commands ──────────────────────────────────────────────────

@cli.group()
@click.pass_context
def project(ctx):
    """Project management."""
    pass


@project.command("list")
@click.option("--status", default="all")
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
@click.pass_context
def project_list(ctx, status, page, per_page):
    """List all projects."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = list_projects(backend, status=status, page=page, per_page=per_page)
    _output(result, ctx.parent.obj.get("as_json", False))


@project.command("get")
@click.argument("project_id", type=int)
@click.pass_context
def project_get(ctx, project_id):
    """Get project details."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = get_project(backend, project_id)
    _output(result, ctx.parent.obj.get("as_json", False))


@project.command("create")
@click.argument("name")
@click.argument("code")
@click.option("--model", default="scrum")
@click.option("--type", "project_type", default="sprint")
@click.option("--begin", default="", help="Start date YYYY-MM-DD")
@click.option("--end", default="", help="End date YYYY-MM-DD")
@click.option("--desc", default="")
@click.pass_context
def project_create(ctx, name, code, model, project_type, begin, end, desc):
    """Create a new project."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = create_project(backend, name, code, model=model,
                            project_type=project_type, begin=begin, end=end,
                            desc=desc)
    _output(result, ctx.parent.obj.get("as_json", False))


@project.command("update")
@click.argument("project_id", type=int)
@click.option("--name", default=None)
@click.option("--desc", default=None)
@click.pass_context
def project_update(ctx, project_id, name, desc):
    """Update an existing project."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    kwargs = {}
    if name is not None:
        kwargs["name"] = name
    if desc is not None:
        kwargs["desc"] = desc
    result = update_project(backend, project_id, **kwargs)
    _output(result, ctx.parent.obj.get("as_json", False))


@project.command("delete")
@click.argument("project_id", type=int)
@click.pass_context
def project_delete(ctx, project_id):
    """Delete a project."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = delete_project(backend, project_id)
    _output(result, ctx.parent.obj.get("as_json", False))


# ── Story commands ────────────────────────────────────────────────────

@cli.group()
@click.pass_context
def story(ctx):
    """Story/requirement management."""
    pass


@story.command("list")
@click.argument("product_id", type=int)
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
@click.pass_context
def story_list(ctx, product_id, page, per_page):
    """List stories for a product."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = list_stories(backend, product_id, page=page, per_page=per_page)
    _output(result, ctx.parent.obj.get("as_json", False))


@story.command("get")
@click.argument("story_id", type=int)
@click.pass_context
def story_get(ctx, story_id):
    """Get story details."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = get_story(backend, story_id)
    _output(result, ctx.parent.obj.get("as_json", False))


@story.command("create")
@click.argument("product_id", type=int)
@click.argument("title")
@click.option("--spec", default="", help="Story specification")
@click.option("--pri", default=3, type=int, help="Priority 1-4")
@click.pass_context
def story_create(ctx, product_id, title, spec, pri):
    """Create a new story."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = create_story(backend, product_id, title, spec=spec, pri=pri)
    _output(result, ctx.parent.obj.get("as_json", False))


@story.command("update")
@click.argument("story_id", type=int)
@click.option("--title", default=None)
@click.option("--spec", default=None)
@click.pass_context
def story_update(ctx, story_id, title, spec):
    """Update an existing story."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    kwargs = {}
    if title is not None:
        kwargs["title"] = title
    if spec is not None:
        kwargs["spec"] = spec
    result = update_story(backend, story_id, **kwargs)
    _output(result, ctx.parent.obj.get("as_json", False))


@story.command("close")
@click.argument("story_id", type=int)
@click.option("--reason", default="")
@click.pass_context
def story_close(ctx, story_id, reason):
    """Close a story."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = close_story(backend, story_id, reason=reason)
    _output(result, ctx.parent.obj.get("as_json", False))


@story.command("activate")
@click.argument("story_id", type=int)
@click.pass_context
def story_activate(ctx, story_id):
    """Activate a closed story."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = activate_story(backend, story_id)
    _output(result, ctx.parent.obj.get("as_json", False))


# ── Task commands ─────────────────────────────────────────────────────

@cli.group()
@click.pass_context
def task(ctx):
    """Task management."""
    pass


@task.command("list")
@click.argument("execution_id", type=int)
@click.option("--status", default="all")
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
@click.pass_context
def task_list(ctx, execution_id, status, page, per_page):
    """List tasks for an execution."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = list_tasks(backend, execution_id, status=status,
                        page=page, per_page=per_page)
    _output(result, ctx.parent.obj.get("as_json", False))


@task.command("get")
@click.argument("task_id", type=int)
@click.pass_context
def task_get(ctx, task_id):
    """Get task details."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = get_task(backend, task_id)
    _output(result, ctx.parent.obj.get("as_json", False))


@task.command("create")
@click.argument("execution_id", type=int)
@click.argument("name")
@click.option("--type", "task_type", default="devel")
@click.option("--pri", default=3, type=int)
@click.option("--estimate", default=0, type=float)
@click.option("--assigned-to", default="")
@click.option("--desc", default="")
@click.pass_context
def task_create(ctx, execution_id, name, task_type, pri, estimate,
                assigned_to, desc):
    """Create a new task."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = create_task(backend, execution_id, name,
                         task_type=task_type, pri=pri, estimate=estimate,
                         assigned_to=assigned_to, desc=desc)
    _output(result, ctx.parent.obj.get("as_json", False))


@task.command("update")
@click.argument("task_id", type=int)
@click.option("--name", default=None)
@click.option("--assigned-to", default=None)
@click.pass_context
def task_update(ctx, task_id, name, assigned_to):
    """Update an existing task."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    kwargs = {}
    if name is not None:
        kwargs["name"] = name
    if assigned_to is not None:
        kwargs["assignedTo"] = assigned_to
    result = update_task(backend, task_id, **kwargs)
    _output(result, ctx.parent.obj.get("as_json", False))


@task.command("start")
@click.argument("task_id", type=int)
@click.pass_context
def task_start(ctx, task_id):
    """Start a task."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = start_task(backend, task_id)
    _output(result, ctx.parent.obj.get("as_json", False))


@task.command("finish")
@click.argument("task_id", type=int)
@click.option("--consumed", default=0, type=float)
@click.pass_context
def task_finish(ctx, task_id, consumed):
    """Finish a task."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = finish_task(backend, task_id, consumed=consumed)
    _output(result, ctx.parent.obj.get("as_json", False))


@task.command("close")
@click.argument("task_id", type=int)
@click.pass_context
def task_close(ctx, task_id):
    """Close a task."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = close_task(backend, task_id)
    _output(result, ctx.parent.obj.get("as_json", False))


@task.command("cancel")
@click.argument("task_id", type=int)
@click.pass_context
def task_cancel(ctx, task_id):
    """Cancel a task."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = cancel_task(backend, task_id)
    _output(result, ctx.parent.obj.get("as_json", False))


# ── Bug commands ──────────────────────────────────────────────────────

@cli.group()
@click.pass_context
def bug(ctx):
    """Bug management."""
    pass


@bug.command("list")
@click.argument("product_id", type=int)
@click.option("--browse-type", default="all")
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
@click.pass_context
def bug_list(ctx, product_id, browse_type, page, per_page):
    """List bugs for a product."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = list_bugs(backend, product_id, browse_type=browse_type,
                       page=page, per_page=per_page)
    _output(result, ctx.parent.obj.get("as_json", False))


@bug.command("get")
@click.argument("bug_id", type=int)
@click.pass_context
def bug_get(ctx, bug_id):
    """Get bug details."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = get_bug(backend, bug_id)
    _output(result, ctx.parent.obj.get("as_json", False))


@bug.command("create")
@click.argument("product_id", type=int)
@click.argument("title")
@click.option("--severity", default=3, type=int, help="1-4 (4=lowest)")
@click.option("--pri", default=3, type=int, help="1-4 (4=lowest)")
@click.option("--type", "bug_type", default="codeerror")
@click.option("--steps", default="")
@click.option("--assigned-to", default="")
@click.option("--desc", default="")
@click.pass_context
def bug_create(ctx, product_id, title, severity, pri, bug_type, steps,
               assigned_to, desc):
    """Create a new bug."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = create_bug(backend, product_id, title, severity=severity,
                        pri=pri, bug_type=bug_type, steps=steps,
                        assigned_to=assigned_to, desc=desc)
    _output(result, ctx.parent.obj.get("as_json", False))


@bug.command("update")
@click.argument("bug_id", type=int)
@click.option("--title", default=None)
@click.option("--severity", default=None, type=int)
@click.pass_context
def bug_update(ctx, bug_id, title, severity):
    """Update an existing bug."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    kwargs = {}
    if title is not None:
        kwargs["title"] = title
    if severity is not None:
        kwargs["severity"] = severity
    result = update_bug(backend, bug_id, **kwargs)
    _output(result, ctx.parent.obj.get("as_json", False))


@bug.command("resolve")
@click.argument("bug_id", type=int)
@click.option("--resolution", default="fixed")
@click.pass_context
def bug_resolve(ctx, bug_id, resolution):
    """Resolve a bug."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = resolve_bug(backend, bug_id, resolution=resolution)
    _output(result, ctx.parent.obj.get("as_json", False))


@bug.command("activate")
@click.argument("bug_id", type=int)
@click.pass_context
def bug_activate(ctx, bug_id):
    """Activate (reopen) a resolved bug."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = activate_bug_op(backend, bug_id)
    _output(result, ctx.parent.obj.get("as_json", False))


@bug.command("close")
@click.argument("bug_id", type=int)
@click.pass_context
def bug_close(ctx, bug_id):
    """Close a bug."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = close_bug_op(backend, bug_id)
    _output(result, ctx.parent.obj.get("as_json", False))


# ── Test case commands ────────────────────────────────────────────────

@cli.group()
@click.pass_context
def testcase(ctx):
    """Test case management."""
    pass


@testcase.command("list")
@click.argument("product_id", type=int)
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
@click.pass_context
def testcase_list(ctx, product_id, page, per_page):
    """List test cases for a product."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = list_testcases(backend, product_id, page=page, per_page=per_page)
    _output(result, ctx.parent.obj.get("as_json", False))


@testcase.command("get")
@click.argument("case_id", type=int)
@click.pass_context
def testcase_get(ctx, case_id):
    """Get test case details."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = get_testcase(backend, case_id)
    _output(result, ctx.parent.obj.get("as_json", False))


@testcase.command("create")
@click.argument("product_id", type=int)
@click.argument("title")
@click.option("--precondition", default="")
@click.option("--steps", default="")
@click.option("--pri", default=3, type=int)
@click.option("--type", "case_type", default="functional")
@click.pass_context
def testcase_create(ctx, product_id, title, precondition, steps, pri,
                    case_type):
    """Create a new test case."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = create_testcase(backend, product_id, title,
                             precondition=precondition, steps=steps,
                             pri=pri, case_type=case_type)
    _output(result, ctx.parent.obj.get("as_json", False))


@testcase.command("update")
@click.argument("case_id", type=int)
@click.option("--title", default=None)
@click.option("--steps", default=None)
@click.pass_context
def testcase_update(ctx, case_id, title, steps):
    """Update an existing test case."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    kwargs = {}
    if title is not None:
        kwargs["title"] = title
    if steps is not None:
        kwargs["steps"] = steps
    result = update_testcase(backend, case_id, **kwargs)
    _output(result, ctx.parent.obj.get("as_json", False))


# ── Build commands ────────────────────────────────────────────────────

@cli.group()
@click.pass_context
def build(ctx):
    """Build management."""
    pass


@build.command("list")
@click.option("--execution-id", default=0, type=int)
@click.option("--product-id", default=0, type=int)
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
@click.pass_context
def build_list(ctx, execution_id, product_id, page, per_page):
    """List builds."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = list_builds(backend, execution_id=execution_id,
                         product_id=product_id, page=page, per_page=per_page)
    _output(result, ctx.parent.obj.get("as_json", False))


@build.command("get")
@click.argument("build_id", type=int)
@click.pass_context
def build_get(ctx, build_id):
    """Get build details."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = get_build(backend, build_id)
    _output(result, ctx.parent.obj.get("as_json", False))


@build.command("create")
@click.argument("product_id", type=int)
@click.argument("name")
@click.option("--execution-id", default=0, type=int)
@click.option("--date", default="", help="YYYY-MM-DD")
@click.option("--builder", default="")
@click.option("--desc", default="")
@click.pass_context
def build_create(ctx, product_id, name, execution_id, date, builder, desc):
    """Create a new build."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = create_build(backend, product_id, name,
                          execution_id=execution_id, date=date,
                          builder=builder, desc=desc)
    _output(result, ctx.parent.obj.get("as_json", False))


@build.command("delete")
@click.argument("build_id", type=int)
@click.pass_context
def build_delete(ctx, build_id):
    """Delete a build."""
    backend = _make_backend(
        ctx.parent.obj.get("url"), ctx.parent.obj.get("user"),
        ctx.parent.obj.get("password"), ctx.parent.obj.get("token"),
    )
    result = delete_build(backend, build_id)
    _output(result, ctx.parent.obj.get("as_json", False))


if __name__ == "__main__":
    cli()
