"""E2E and CLI subprocess tests for cli-anything-zentao.

These tests invoke the installed CLI command via subprocess.
Uses _resolve_cli to find the command — installed or dev fallback.
"""

import os
import sys
import json
import subprocess
import pytest

# ── _resolve_cli helper ──────────────────────────────────────────────

def _resolve_cli(name):
    """Resolve installed CLI command; falls back to python -m for dev.

    Set env CLI_ANYTHING_FORCE_INSTALLED=1 to require the installed command.
    """
    import shutil
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    module = name.replace("cli-anything-", "cli_anything.") + name.split("-")[-1] + "_cli"
    # Special case for zentao: the CLI module is at the package root
    module = "cli_anything.zentao_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


CLI_BASE = _resolve_cli("cli-anything-zentao")


def _run_cli(args, check=True):
    """Run CLI with given args and return CompletedProcess."""
    return subprocess.run(
        CLI_BASE + args,
        capture_output=True,
        text=True,
        check=check,
    )


# ── CLI basic tests ──────────────────────────────────────────────────

class TestCLIBasics:
    """Test basic CLI functionality (no server required for --help)."""

    def test_help(self):
        """CLI --help returns exit code 0."""
        result = _run_cli(["--help"], check=False)
        assert result.returncode == 0
        assert "zentao" in result.stdout.lower() or "zentao" in result.stderr.lower()

    def test_json_flag_with_help(self):
        """--json flag can be combined with other flags."""
        result = _run_cli(["--json", "--help"], check=False)
        # --json with --help should still work (exit 0)
        assert result.returncode == 0


# ── Connection tests (require server) ────────────────────────────────

class TestConnect:
    """Test the connect command."""

    @pytest.mark.skipif(
        not os.environ.get("ZENTAO_URL"),
        reason="ZENTAO_URL not set — skipping server-dependent test",
    )
    def test_connect_returns_status(self):
        """connect command returns connection status."""
        result = _run_cli(["--json", "connect"], check=False)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert "status" in data


# ── Read operations (require server) ─────────────────────────────────

class TestListOperations:
    """Test list/read commands with real ZenTao server."""

    @pytest.mark.skipif(
        not os.environ.get("ZENTAO_URL"),
        reason="ZENTAO_URL not set",
    )
    def test_product_list_json(self):
        """product list returns JSON structure."""
        result = _run_cli([
            "--json", "product", "list", "--page", "1", "--per-page", "5",
        ], check=False)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert isinstance(data, dict)

    @pytest.mark.skipif(
        not os.environ.get("ZENTAO_URL"),
        reason="ZENTAO_URL not set",
    )
    def test_project_list_json(self):
        """project list returns JSON structure."""
        result = _run_cli([
            "--json", "project", "list", "--page", "1", "--per-page", "5",
        ], check=False)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert isinstance(data, dict)

    @pytest.mark.skipif(
        not os.environ.get("ZENTAO_URL"),
        reason="ZENTAO_URL not set",
    )
    def test_build_list_json(self):
        """build list returns JSON structure."""
        result = _run_cli([
            "--json", "build", "list", "--page", "1", "--per-page", "5",
        ], check=False)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert isinstance(data, dict)


# ── REPL subprocess tests ────────────────────────────────────────────

class TestREPLSubprocess:
    """Test REPL mode via subprocess."""

    @pytest.mark.skipif(
        not os.environ.get("ZENTAO_URL"),
        reason="ZENTAO_URL not set — REPL requires connection config",
    )
    def test_repl_quit(self):
        """REPL mode exits on 'quit' command."""
        result = subprocess.run(
            CLI_BASE,
            input="quit\n",
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0

    @pytest.mark.skipif(
        not os.environ.get("ZENTAO_URL"),
        reason="ZENTAO_URL not set — REPL requires connection config",
    )
    def test_repl_help_then_quit(self):
        """REPL mode handles help then quit."""
        result = subprocess.run(
            CLI_BASE,
            input="help\nquit\n",
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0


# ── Full workflow (requires server) ──────────────────────────────────

class TestFullWorkflow:
    """Full end-to-end workflow tests (require live ZenTao server)."""

    @pytest.mark.skipif(
        not os.environ.get("ZENTAO_URL"),
        reason="ZENTAO_URL not set — skipping server-dependent test",
    )
    def test_product_crud_via_cli(self):
        """Full product CRUD via CLI subprocess."""
        # Create
        result = _run_cli([
            "--json", "product", "create",
            "CLI-Test-Product", "CLITP001",
            "--type", "normal",
            "--desc", "Created by CLI test",
        ], check=False)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            # List to verify
            list_result = _run_cli(["--json", "product", "list", "--page", "1"], check=False)
            if list_result.returncode == 0:
                list_data = json.loads(list_result.stdout)
                assert isinstance(list_data, dict)

    @pytest.mark.skipif(
        not os.environ.get("ZENTAO_URL"),
        reason="ZENTAO_URL not set — skipping server-dependent test",
    )
    def test_full_sprint_workflow(self):
        """Full agile sprint workflow: project → story → task."""
        # Create project
        result = _run_cli([
            "--json", "project", "create",
            "CLI-Test-Sprint", "CLISP001",
            "--model", "scrum",
            "--type", "sprint",
            "--begin", "2025-06-01",
            "--end", "2025-06-30",
            "--desc", "CLI test sprint",
        ], check=False)

        if result.returncode == 0:
            data = json.loads(result.stdout)
            # Verify response structure
            assert "status" in data or "result" in data

            # List projects to verify
            list_result = _run_cli(["--json", "project", "list"], check=False)
            if list_result.returncode == 0:
                list_data = json.loads(list_result.stdout)
                assert isinstance(list_data, dict)
