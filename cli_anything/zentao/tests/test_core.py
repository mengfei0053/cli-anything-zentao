"""Unit tests for cli-anything-zentao core modules.

Tests use mocked backends — no real ZenTao server required.
"""

import pytest
import os
import sys

# Ensure we can import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from cli_anything.zentao.utils.zentao_backend import (
    ZenTaoBackend, ZenTaoAPIError, ZenTaoConfigError,
)
from cli_anything.zentao.core.product import (
    create_product, update_product, delete_product,
)
from cli_anything.zentao.core.project import (
    create_project, update_project, delete_project,
)
from cli_anything.zentao.core.story import (
    create_story, update_story, close_story, activate_story,
)
from cli_anything.zentao.core.task import (
    create_task, update_task, start_task, finish_task, close_task, cancel_task,
)
from cli_anything.zentao.core.effort import (
    list_efforts, get_effort, add_effort, update_effort, delete_effort,
)
from cli_anything.zentao.core.bug import (
    create_bug, update_bug, resolve_bug, activate_bug, close_bug,
)
from cli_anything.zentao.core.testcase import (
    create_testcase, update_testcase,
)
from cli_anything.zentao.core.build import (
    create_build, delete_build,
)


# ── Mock backend ─────────────────────────────────────────────────────

class MockBackend:
    """A fake ZenTaoBackend that records calls and returns canned responses."""

    def __init__(self, url="http://test/zentao", user="admin", password="123456"):
        self.url = url
        self.user = user
        self.calls = []

    def _record(self, method_name, *args, **kwargs):
        self.calls.append((method_name, args, kwargs))
        return {"status": "success", "result": {"id": len(self.calls)}}

    def list_products(self, **kw):
        return self._record("list_products", **kw)

    def get_product(self, product_id):
        return self._record("get_product", product_id)

    def create_product(self, data):
        return self._record("create_product", data)

    def update_product(self, product_id, data):
        return self._record("update_product", product_id, data)

    def delete_product(self, product_id):
        return self._record("delete_product", product_id)

    def list_projects(self, **kw):
        return self._record("list_projects", **kw)

    def get_project(self, project_id):
        return self._record("get_project", project_id)

    def create_project(self, data):
        return self._record("create_project", data)

    def update_project(self, project_id, data):
        return self._record("update_project", project_id, data)

    def delete_project(self, project_id):
        return self._record("delete_project", project_id)

    def list_stories(self, **kw):
        return self._record("list_stories", **kw)

    def get_story(self, story_id, **kw):
        return self._record("get_story", story_id, **kw)

    def create_story(self, data):
        return self._record("create_story", data)

    def update_story(self, story_id, data):
        return self._record("update_story", story_id, data)

    def close_story(self, story_id, **kw):
        return self._record("close_story", story_id, **kw)

    def activate_story(self, story_id):
        return self._record("activate_story", story_id)

    def list_tasks(self, **kw):
        return self._record("list_tasks", **kw)

    def get_task(self, task_id):
        return self._record("get_task", task_id)

    def create_task(self, data):
        return self._record("create_task", data)

    def update_task(self, task_id, data):
        return self._record("update_task", task_id, data)

    def start_task(self, task_id):
        return self._record("start_task", task_id)

    def finish_task(self, task_id, data=None):
        return self._record("finish_task", task_id, data=data)

    def close_task(self, task_id):
        return self._record("close_task", task_id)

    def cancel_task(self, task_id):
        return self._record("cancel_task", task_id)

    # ── Effort ──

    def list_efforts(self, task_id, account="", order_by="date,id"):
        return self._record("list_efforts", task_id, account=account, order_by=order_by)

    def get_effort(self, effort_id):
        return self._record("get_effort", effort_id)

    def add_effort(self, data):
        return self._record("add_effort", data)

    def update_effort(self, data):
        return self._record("update_effort", data)

    def delete_effort(self, effort_id):
        return self._record("delete_effort", effort_id)

    def list_bugs(self, **kw):
        return self._record("list_bugs", **kw)

    def get_bug(self, bug_id):
        return self._record("get_bug", bug_id)

    def create_bug(self, data):
        return self._record("create_bug", data)

    def update_bug(self, bug_id, data):
        return self._record("update_bug", bug_id, data)

    def resolve_bug(self, bug_id, data=None):
        return self._record("resolve_bug", bug_id, data=data)

    def activate_bug(self, bug_id):
        return self._record("activate_bug", bug_id)

    def close_bug(self, bug_id):
        return self._record("close_bug", bug_id)

    def list_testcases(self, **kw):
        return self._record("list_testcases", **kw)

    def get_testcase(self, case_id):
        return self._record("get_testcase", case_id)

    def create_testcase(self, data):
        return self._record("create_testcase", data)

    def update_testcase(self, case_id, data):
        return self._record("update_testcase", case_id, data)

    def list_builds(self, **kw):
        return self._record("list_builds", **kw)

    def get_build(self, build_id):
        return self._record("get_build", build_id)

    def create_build(self, data):
        return self._record("create_build", data)

    def delete_build(self, build_id):
        return self._record("delete_build", build_id)

    def test_connection(self):
        return {"status": "ok", "message": "Connected to ZenTao"}


@pytest.fixture
def mock_backend():
    return MockBackend()


# ── ZenTaoBackend tests ──────────────────────────────────────────────

class TestZenTaoBackendInit:
    def test_backend_init_from_env(self, monkeypatch):
        monkeypatch.setenv("ZENTAO_URL", "http://env-test/zentao")
        monkeypatch.setenv("ZENTAO_USER", "envuser")
        monkeypatch.setenv("ZENTAO_PASSWORD", "envpass")
        backend = ZenTaoBackend()
        assert backend.url == "http://env-test/zentao"
        assert backend.user == "envuser"

    def test_backend_init_from_args(self):
        backend = ZenTaoBackend(
            url="http://args-test/zentao", user="argsuser", password="argspass"
        )
        assert backend.url == "http://args-test/zentao"
        assert backend.user == "argsuser"

    def test_backend_missing_url_raises(self):
        with pytest.raises(ZenTaoConfigError, match="ZENTAO_URL"):
            ZenTaoBackend(url="", user="", password="")

    def test_backend_url_strip_trailing_slash(self):
        backend = ZenTaoBackend(
            url="http://test/zentao/", user="u", password="p"
        )
        assert backend.url == "http://test/zentao"


class TestZenTaoBackendURL:
    def test_build_url_simple(self):
        backend = ZenTaoBackend(url="http://test/zentao", user="u", password="p")
        url = backend._build_url("product", "all")
        assert "module=product" in url
        assert "method=all" in url

    def test_build_url_with_params(self):
        backend = ZenTaoBackend(url="http://test/zentao", user="u", password="p")
        url = backend._build_url("story", "view", {"storyID": 42})
        assert "storyID=42" in url

    def test_build_url_none_params_skipped(self):
        backend = ZenTaoBackend(url="http://test/zentao", user="u", password="p")
        url = backend._build_url("task", "view", {"taskID": 1, "foo": None})
        assert "taskID=1" in url
        assert "foo" not in url


class TestExceptions:
    def test_api_error_exception(self):
        err = ZenTaoAPIError("test error", status_code=404, response="not found")
        assert str(err) == "test error"
        assert err.status_code == 404
        assert err.response == "not found"

    def test_config_error_exception(self):
        err = ZenTaoConfigError("missing config")
        assert str(err) == "missing config"


# ── Product operation tests ──────────────────────────────────────────

class TestProductOperations:
    def test_create_product_builds_data(self, mock_backend):
        result = create_product(mock_backend, "Test Product", "TP",
                                product_type="normal", desc="A test product")
        assert result["status"] == "success"
        call_name, call_args, call_kwargs = mock_backend.calls[0]
        assert call_name == "create_product"
        data = call_args[0]
        assert data["name"] == "Test Product"
        assert data["code"] == "TP"
        assert data["type"] == "normal"

    def test_create_product_with_kwargs(self, mock_backend):
        result = create_product(mock_backend, "Extra", "EX", po="admin", extra_field="value")
        assert result["status"] == "success"
        data = mock_backend.calls[0][1][0]
        assert data["PO"] == "admin"
        assert data["extra_field"] == "value"

    def test_update_product(self, mock_backend):
        result = update_product(mock_backend, 5, name="Updated", desc="New desc")
        assert result["status"] == "success"
        assert mock_backend.calls[0][0] == "update_product"

    def test_delete_product(self, mock_backend):
        result = delete_product(mock_backend, 3)
        assert result["status"] == "success"
        assert mock_backend.calls[0][0] == "delete_product"


# ── Project operation tests ──────────────────────────────────────────

class TestProjectOperations:
    def test_create_project_builds_data(self, mock_backend):
        result = create_project(mock_backend, "Sprint 1", "SP1",
                                model="scrum", project_type="sprint",
                                begin="2025-01-01", end="2025-01-31")
        assert result["status"] == "success"
        data = mock_backend.calls[0][1][0]
        assert data["name"] == "Sprint 1"
        assert data["model"] == "scrum"
        assert data["begin"] == "2025-01-01"

    def test_create_project_default_model(self, mock_backend):
        result = create_project(mock_backend, "Default", "DEF")
        assert result["status"] == "success"
        data = mock_backend.calls[0][1][0]
        assert data["model"] == "scrum"
        assert data["type"] == "sprint"

    def test_update_project(self, mock_backend):
        result = update_project(mock_backend, 10, name="Updated Project")
        assert result["status"] == "success"

    def test_delete_project(self, mock_backend):
        result = delete_project(mock_backend, 7)
        assert result["status"] == "success"


# ── Story operation tests ────────────────────────────────────────────

class TestStoryOperations:
    def test_create_story_builds_data(self, mock_backend):
        result = create_story(mock_backend, product_id=1, title="Login feature",
                              spec="As a user I want to login", pri=1)
        assert result["status"] == "success"
        data = mock_backend.calls[0][1][0]
        assert data["product"] == 1
        assert data["title"] == "Login feature"
        assert data["pri"] == 1

    def test_create_story_priority_range(self, mock_backend):
        for pri in [1, 2, 3, 4]:
            mock_backend.calls.clear()
            result = create_story(mock_backend, product_id=1, title="Test", pri=pri)
            assert result["status"] == "success"
            data = mock_backend.calls[0][1][0]
            assert data["pri"] == pri

    def test_update_story(self, mock_backend):
        result = update_story(mock_backend, 20, title="Updated title")
        assert result["status"] == "success"

    def test_close_story(self, mock_backend):
        result = close_story(mock_backend, 15, reason="done")
        assert result["status"] == "success"

    def test_activate_story(self, mock_backend):
        result = activate_story(mock_backend, 15)
        assert result["status"] == "success"


# ── Task operation tests ─────────────────────────────────────────────

class TestTaskOperations:
    def test_create_task_builds_data(self, mock_backend):
        result = create_task(mock_backend, execution_id=5, name="Write tests",
                             task_type="devel", estimate=4.0, assigned_to="dev1")
        assert result["status"] == "success"
        data = mock_backend.calls[0][1][0]
        assert data["execution"] == 5
        assert data["name"] == "Write tests"
        assert data["type"] == "devel"

    def test_create_task_with_all_fields(self, mock_backend):
        result = create_task(mock_backend, execution_id=5, name="Full task",
                             task_type="design", pri=1, estimate=8,
                             assigned_to="designer", desc="Design the UI")
        data = mock_backend.calls[0][1][0]
        assert data["pri"] == 1
        assert data["desc"] == "Design the UI"

    def test_start_task(self, mock_backend):
        result = start_task(mock_backend, 42)
        assert result["status"] == "success"

    def test_finish_task(self, mock_backend):
        result = finish_task(mock_backend, 42, consumed=3.5)
        assert result["status"] == "success"

    def test_close_task(self, mock_backend):
        result = close_task(mock_backend, 42)
        assert result["status"] == "success"

    def test_cancel_task(self, mock_backend):
        result = cancel_task(mock_backend, 42)
        assert result["status"] == "success"


# ── Bug operation tests ──────────────────────────────────────────────

class TestBugOperations:
    def test_create_bug_builds_data(self, mock_backend):
        result = create_bug(mock_backend, product_id=1,
                            title="Null pointer on login", severity=2, pri=1,
                            bug_type="codeerror", steps="1. Open app\n2. Click login")
        assert result["status"] == "success"
        data = mock_backend.calls[0][1][0]
        assert data["product"] == 1
        assert data["title"] == "Null pointer on login"
        assert data["severity"] == 2

    def test_resolve_bug_builds_data(self, mock_backend):
        result = resolve_bug(mock_backend, 100, resolution="fixed",
                             resolved_build="v1.2.0")
        assert result["status"] == "success"
        call_name, call_args, call_kwargs = mock_backend.calls[0]
        assert call_name == "resolve_bug"
        data = call_kwargs.get("data")
        assert data["resolution"] == "fixed"

    def test_bug_severity_levels(self, mock_backend):
        for sev in [1, 2, 3, 4]:
            mock_backend.calls.clear()
            result = create_bug(mock_backend, product_id=1,
                                title="Test", severity=sev)
            assert result["status"] == "success"
            data = mock_backend.calls[0][1][0]
            assert data["severity"] == sev

    def test_activate_bug(self, mock_backend):
        result = activate_bug(mock_backend, 99)
        assert result["status"] == "success"

    def test_close_bug(self, mock_backend):
        result = close_bug(mock_backend, 99)
        assert result["status"] == "success"


# ── Test case operation tests ────────────────────────────────────────

class TestTestcaseOperations:
    def test_create_testcase_builds_data(self, mock_backend):
        result = create_testcase(mock_backend, product_id=1,
                                 title="Verify login with valid credentials",
                                 precondition="User exists",
                                 steps="1. Enter username\n2. Enter password\n3. Click login",
                                 pri=1, case_type="functional")
        assert result["status"] == "success"
        data = mock_backend.calls[0][1][0]
        assert data["product"] == 1
        assert data["title"] == "Verify login with valid credentials"
        assert data["type"] == "functional"

    def test_update_testcase(self, mock_backend):
        result = update_testcase(mock_backend, 55, title="Updated test",
                                 steps="Updated steps")
        assert result["status"] == "success"


# ── Build operation tests ────────────────────────────────────────────

class TestBuildOperations:
    def test_create_build_builds_data(self, mock_backend):
        result = create_build(mock_backend, product_id=1, name="v1.0.0",
                              builder="ci-bot", desc="Release build")
        assert result["status"] == "success"
        data = mock_backend.calls[0][1][0]
        assert data["product"] == 1
        assert data["name"] == "v1.0.0"
        assert data["builder"] == "ci-bot"

    def test_delete_build(self, mock_backend):
        result = delete_build(mock_backend, 30)
        assert result["status"] == "success"


# ── Effort operation tests ───────────────────────────────────────────

class TestEffortOperations:
    def test_list_efforts(self, mock_backend):
        result = list_efforts(mock_backend, task_id=42)
        assert result["status"] == "success"
        assert mock_backend.calls[0][0] == "list_efforts"
        assert mock_backend.calls[0][1][0] == 42

    def test_list_efforts_with_account(self, mock_backend):
        result = list_efforts(mock_backend, task_id=42, account="dev1")
        assert result["status"] == "success"
        kwargs = mock_backend.calls[0][2]
        assert kwargs["account"] == "dev1"

    def test_get_effort(self, mock_backend):
        result = get_effort(mock_backend, effort_id=101)
        assert result["status"] == "success"

    def test_add_effort_builds_data(self, mock_backend):
        result = add_effort(mock_backend, task_id=42, consumed=3.5, left=4.0, work="开发登录模块")
        assert result["status"] == "success"
        data = mock_backend.calls[0][1][0]
        assert data["task"] == 42
        assert data["consumed"] == 3.5
        assert data["left"] == 4.0
        assert data["work"] == "开发登录模块"

    def test_add_effort_minimal(self, mock_backend):
        result = add_effort(mock_backend, task_id=42, consumed=2.0)
        assert result["status"] == "success"
        data = mock_backend.calls[0][1][0]
        assert "left" not in data
        assert "work" not in data

    def test_update_effort(self, mock_backend):
        result = update_effort(mock_backend, effort_id=101, consumed=4.0, work="更新工作内容")
        assert result["status"] == "success"
        data = mock_backend.calls[0][1][0]
        assert data["id"] == 101
        assert data["consumed"] == 4.0

    def test_delete_effort(self, mock_backend):
        result = delete_effort(mock_backend, effort_id=101)
        assert result["status"] == "success"
        assert mock_backend.calls[0][0] == "delete_effort"
        assert mock_backend.calls[0][1][0] == 101
