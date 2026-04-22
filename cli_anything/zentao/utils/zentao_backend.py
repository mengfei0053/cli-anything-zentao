"""ZenTao backend integration.

Provides HTTP API and optional direct MySQL database access to ZenTao.

ZenTao exposes a REST-like API through its web interface with token-based
authentication. This module handles:
- HTTP API calls to ZenTao web server
- Session management and authentication
- Database queries (optional, for read-heavy operations)
- Error handling with clear configuration instructions
"""

import os
import json
import hashlib
import urllib.parse
import urllib.request
import urllib.error
from typing import Any, Optional


class ZenTaoAPIError(Exception):
    """Raised when a ZenTao API call fails."""
    def __init__(self, message: str, status_code: int = 0, response: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ZenTaoConfigError(Exception):
    """Raised when ZenTao configuration is missing or invalid."""
    pass


class ZenTaoBackend:
    """Backend integration with ZenTao project management system.

    Supports two connection modes:
    1. HTTP API (default) — interacts with ZenTao web server via HTTP
    2. Direct MySQL (optional) — reads directly from database for performance

    Environment variables for configuration:
        ZENTAO_URL: Base URL of ZenTao instance (e.g., http://localhost/zentao)
        ZENTAO_USER: Username for authentication
        ZENTAO_PASSWORD: Password for authentication
        ZENTAO_TOKEN: Pre-generated session token (alternative to user/password)
        ZENTAO_DB_HOST: MySQL host (optional, for direct DB mode)
        ZENTAO_DB_PORT: MySQL port (default: 3306)
        ZENTAO_DB_NAME: Database name (default: zentao)
        ZENTAO_DB_USER: MySQL username
        ZENTAO_DB_PASSWORD: MySQL password
    """

    def __init__(self, url: Optional[str] = None, user: Optional[str] = None,
                 password: Optional[str] = None, token: Optional[str] = None):
        """Initialize backend connection.

        Args:
            url: ZenTao base URL. Falls back to ZENTAO_URL env var.
            user: Username. Falls back to ZENTAO_USER env var.
            password: Password. Falls back to ZENTAO_PASSWORD env var.
            token: Pre-generated token. Falls back to ZENTAO_TOKEN env var.
        """
        self.url = (url or os.environ.get("ZENTAO_URL", "")).rstrip("/")
        self.user = user or os.environ.get("ZENTAO_USER", "")
        self.password = password or os.environ.get("ZENTAO_PASSWORD", "")
        self.token = token or os.environ.get("ZENTAO_TOKEN", "")
        self._session_id: Optional[str] = None
        self._rand: Optional[str] = None

        if not self.url:
            raise ZenTaoConfigError(
                "ZenTao URL not configured. Set ZENTAO_URL environment variable "
                "or pass url= to ZenTaoBackend().\n"
                "Example: export ZENTAO_URL=http://localhost/zentao"
            )

    def _generate_token(self) -> str:
        """Generate ZenTao-style session token from credentials.

        ZenTao uses: token = md5(md5(password) + rand + account)
        where rand is obtained from the login page.
        """
        if self.token:
            return self.token

        if not self.user or not self.password:
            raise ZenTaoConfigError(
                "Authentication not configured. Set ZENTAO_USER and ZENTAO_PASSWORD, "
                "or ZENTAO_TOKEN for pre-generated token.\n"
                "Example: export ZENTAO_USER=admin ZENTAO_PASSWORD=123456"
            )

        # First, try to get the rand value from the login page
        if not self._rand:
            try:
                login_url = f"{self.url}/user-login.html"
                req = urllib.request.Request(login_url)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    html = resp.read().decode("utf-8", errors="replace")
                    # Extract rand from the page (ZenTao embeds it in JavaScript)
                    import re
                    match = re.search(r"['\"]rand['\"]\s*:\s*['\"]([^'\"]+)['\"]", html)
                    if match:
                        self._rand = match.group(1)
            except Exception:
                # If we can't get rand, use a default (some versions don't require it)
                self._rand = ""

        # token = md5(md5(password) + rand + account)
        pwd_hash = hashlib.md5(self.password.encode()).hexdigest()
        token_input = f"{pwd_hash}{self._rand}{self.user}"
        return hashlib.md5(token_input.encode()).hexdigest()

    def _get_session_id(self) -> str:
        """Login and get session ID."""
        if self._session_id:
            return self._session_id

        token = self._generate_token()
        login_url = (
            f"{self.url}/api.php?module=user&method=login"
            f"&account={urllib.parse.quote(self.user)}"
            f"&password={urllib.parse.quote(self.password)}"
        )

        try:
            req = urllib.request.Request(login_url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                # Extract session cookie
                cookies = resp.headers.get_all("Set-Cookie") or []
                for cookie in cookies:
                    if "zentaosid" in cookie.lower():
                        import http.cookies
                        c = http.cookies.SimpleCookie(cookie)
                        if "zentaosid" in c:
                            self._session_id = c["zentaosid"].value
                            return self._session_id
                # Fallback: try the response body
                body = resp.read().decode("utf-8", errors="replace")
                data = json.loads(body) if body else {}
                if data.get("status") == "success":
                    self._session_id = "authenticated"
                    return self._session_id
        except urllib.error.HTTPError as e:
            raise ZenTaoAPIError(
                f"Login failed: HTTP {e.code}",
                status_code=e.code,
                response=e.read().decode("utf-8", errors="replace"),
            )
        except urllib.error.URLError as e:
            raise ZenTaoAPIError(f"Login failed: {e.reason}")

        raise ZenTaoAPIError("Login failed: no session ID received")

    def _build_url(self, module: str, method: str, params: Optional[dict] = None) -> str:
        """Build API URL for a ZenTao module/method call."""
        base = f"{self.url}/api.php?module={module}&method={method}"
        if params:
            for key, value in params.items():
                if value is not None:
                    encoded = urllib.parse.quote(str(value))
                    base += f"&{key}={encoded}"
        return base

    def _make_request(self, url: str, method: str = "GET",
                      data: Optional[dict] = None) -> dict:
        """Make HTTP request to ZenTao API.

        Args:
            url: Full API URL
            method: HTTP method (GET/POST)
            data: POST data as dict

        Returns:
            Parsed JSON response
        """
        if data:
            post_data = json.dumps(data).encode("utf-8")
        else:
            post_data = None

        req = urllib.request.Request(url, data=post_data, method=method)
        req.add_header("Content-Type", "application/json")

        # Add session cookie if available
        if self._session_id:
            req.add_header("Cookie", f"zentaosid={self._session_id}")

        # Add token-based auth header
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                # Try JSON first
                try:
                    return json.loads(body)
                except json.JSONDecodeError:
                    return {"raw": body, "status_code": resp.status}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            raise ZenTaoAPIError(
                f"API request failed: HTTP {e.code} — {e.reason}",
                status_code=e.code,
                response=error_body,
            )
        except urllib.error.URLError as e:
            raise ZenTaoAPIError(f"API request failed: {e.reason}")

    def call(self, module: str, method: str, params: Optional[dict] = None,
             post_data: Optional[dict] = None) -> dict:
        """Call a ZenTao API endpoint.

        Args:
            module: ZenTao module name (e.g., 'product', 'project', 'bug')
            method: Method name (e.g., 'browse', 'create', 'view')
            params: URL query parameters
            post_data: POST body data

        Returns:
            API response as dict
        """
        url = self._build_url(module, method, params)
        http_method = "POST" if post_data else "GET"
        return self._make_request(url, method=http_method, data=post_data)

    # ── Product operations ─────────────────────────────────────────────

    def list_products(self, status: str = "all", order_by: str = "order_asc",
                      page: int = 1, per_page: int = 20) -> dict:
        """List all products.

        Args:
            status: Filter by status (all, noclosed, closed)
            order_by: Sort order
            page: Page number
            per_page: Items per page

        Returns:
            Dict with products list and pagination info
        """
        params = {
            "browseType": status,
            "orderBy": order_by,
            "recTotal": 0,
            "recPerPage": per_page,
            "pageID": page,
        }
        return self.call("product", "all", params)

    def get_product(self, product_id: int) -> dict:
        """Get product details."""
        return self.call("product", "view", {"productID": product_id})

    def create_product(self, data: dict) -> dict:
        """Create a new product.

        Args:
            data: Product fields (name, code, type, desc, PO, etc.)

        Returns:
            API response with product ID
        """
        return self.call("product", "create", post_data=data)

    def update_product(self, product_id: int, data: dict) -> dict:
        """Update an existing product."""
        params = {"productID": product_id, "action": "edit"}
        return self.call("product", "edit", params, post_data=data)

    def delete_product(self, product_id: int) -> dict:
        """Delete a product."""
        return self.call("product", "delete", {"productID": product_id})

    # ── Project operations ─────────────────────────────────────────────

    def list_projects(self, status: str = "all", order_by: str = "order_asc",
                      page: int = 1, per_page: int = 20) -> dict:
        """List all projects."""
        params = {
            "browseType": status,
            "orderBy": order_by,
            "recTotal": 0,
            "recPerPage": per_page,
            "pageID": page,
        }
        return self.call("project", "browse", params)

    def get_project(self, project_id: int) -> dict:
        """Get project details."""
        return self.call("project", "view", {"projectID": project_id})

    def create_project(self, data: dict) -> dict:
        """Create a new project.

        Args:
            data: Project fields (name, code, model, type, begin, end, desc, etc.)

        Returns:
            API response with project ID
        """
        return self.call("project", "create", post_data=data)

    def update_project(self, project_id: int, data: dict) -> dict:
        """Update an existing project."""
        params = {"projectID": project_id}
        return self.call("project", "edit", params, post_data=data)

    def delete_project(self, project_id: int) -> dict:
        """Delete a project."""
        return self.call("project", "delete", {"projectID": project_id})

    # ── Story/Requirement operations ───────────────────────────────────

    def list_stories(self, product_id: int, branch: str = "all",
                     browse_type: str = "all", story_type: str = "story",
                     order_by: str = "id_desc", page: int = 1,
                     per_page: int = 20) -> dict:
        """List stories/requirements for a product."""
        params = {
            "productID": product_id,
            "branch": branch,
            "browseType": browse_type,
            "storyType": story_type,
            "orderBy": order_by,
            "recTotal": 0,
            "recPerPage": per_page,
            "pageID": page,
        }
        return self.call("story", "browse", params)

    def get_story(self, story_id: int, story_type: str = "story") -> dict:
        """Get story details."""
        params = {"storyID": story_id, "storyType": story_type}
        return self.call("story", "view", params)

    def create_story(self, data: dict) -> dict:
        """Create a new story/requirement.

        Args:
            data: Story fields (product, title, spec, type, pri, etc.)

        Returns:
            API response with story ID
        """
        return self.call("story", "create", post_data=data)

    def update_story(self, story_id: int, data: dict) -> dict:
        """Update an existing story."""
        params = {"storyID": story_id}
        return self.call("story", "edit", params, post_data=data)

    def close_story(self, story_id: int, reason: str = "") -> dict:
        """Close a story."""
        params = {"storyID": story_id}
        post_data = {"reason": reason} if reason else None
        return self.call("story", "close", params, post_data=post_data)

    def activate_story(self, story_id: int) -> dict:
        """Activate a closed story."""
        return self.call("story", "activate", {"storyID": story_id})

    # ── Task operations ────────────────────────────────────────────────

    def list_tasks(self, execution_id: int, status: str = "all",
                   order_by: str = "id_desc", page: int = 1,
                   per_page: int = 20) -> dict:
        """List tasks for an execution."""
        params = {
            "executionID": execution_id,
            "status": status,
            "orderBy": order_by,
            "recTotal": 0,
            "recPerPage": per_page,
            "pageID": page,
        }
        return self.call("task", "browse", params)

    def get_task(self, task_id: int) -> dict:
        """Get task details."""
        return self.call("task", "view", {"taskID": task_id})

    def create_task(self, data: dict) -> dict:
        """Create a new task.

        Args:
            data: Task fields (execution, name, type, pri, estimate, assignedTo, etc.)

        Returns:
            API response with task ID
        """
        return self.call("task", "create", post_data=data)

    def update_task(self, task_id: int, data: dict) -> dict:
        """Update an existing task."""
        params = {"taskID": task_id}
        return self.call("task", "edit", params, post_data=data)

    def start_task(self, task_id: int) -> dict:
        """Start a task."""
        return self.call("task", "start", {"taskID": task_id})

    def finish_task(self, task_id: int, data: Optional[dict] = None) -> dict:
        """Finish a task."""
        params = {"taskID": task_id}
        return self.call("task", "finish", params, post_data=data)

    def close_task(self, task_id: int) -> dict:
        """Close a task."""
        return self.call("task", "close", {"taskID": task_id})

    def cancel_task(self, task_id: int) -> dict:
        """Cancel a task."""
        return self.call("task", "cancel", {"taskID": task_id})

    # ── Bug operations ─────────────────────────────────────────────────

    def list_bugs(self, product_id: int, branch: str = "all",
                  browse_type: str = "all", order_by: str = "id_desc",
                  page: int = 1, per_page: int = 20) -> dict:
        """List bugs for a product."""
        params = {
            "productID": product_id,
            "branch": branch,
            "browseType": browse_type,
            "orderBy": order_by,
            "recTotal": 0,
            "recPerPage": per_page,
            "pageID": page,
        }
        return self.call("bug", "browse", params)

    def get_bug(self, bug_id: int) -> dict:
        """Get bug details."""
        return self.call("bug", "view", {"bugID": bug_id})

    def create_bug(self, data: dict) -> dict:
        """Create a new bug.

        Args:
            data: Bug fields (product, title, severity, pri, type, steps, openedBuild, etc.)

        Returns:
            API response with bug ID
        """
        return self.call("bug", "create", post_data=data)

    def update_bug(self, bug_id: int, data: dict) -> dict:
        """Update an existing bug."""
        params = {"bugID": bug_id}
        return self.call("bug", "edit", params, post_data=data)

    def resolve_bug(self, bug_id: int, data: dict) -> dict:
        """Resolve a bug.

        Args:
            data: Resolution fields (resolution, resolvedBuild, resolvedBy, etc.)
        """
        params = {"bugID": bug_id}
        return self.call("bug", "resolve", params, post_data=data)

    def activate_bug(self, bug_id: int) -> dict:
        """Activate a resolved bug."""
        return self.call("bug", "activate", {"bugID": bug_id})

    def close_bug(self, bug_id: int) -> dict:
        """Close a bug."""
        return self.call("bug", "close", {"bugID": bug_id})

    # ── Test Case operations ───────────────────────────────────────────

    def list_testcases(self, product_id: int, branch: str = "all",
                       browse_type: str = "all", case_type: str = "",
                       order_by: str = "id_desc", page: int = 1,
                       per_page: int = 20) -> dict:
        """List test cases for a product."""
        params = {
            "productID": product_id,
            "branch": branch,
            "browseType": browse_type,
            "caseType": case_type,
            "orderBy": order_by,
            "recTotal": 0,
            "recPerPage": per_page,
            "pageID": page,
        }
        return self.call("testcase", "browse", params)

    def get_testcase(self, case_id: int) -> dict:
        """Get test case details."""
        return self.call("testcase", "view", {"caseID": case_id})

    def create_testcase(self, data: dict) -> dict:
        """Create a new test case.

        Args:
            data: Test case fields (product, title, precondition, steps, pri, type, etc.)

        Returns:
            API response with test case ID
        """
        return self.call("testcase", "create", post_data=data)

    def update_testcase(self, case_id: int, data: dict) -> dict:
        """Update an existing test case."""
        params = {"caseID": case_id}
        return self.call("testcase", "edit", params, post_data=data)

    # ── Build operations ───────────────────────────────────────────────

    def list_builds(self, execution_id: int = 0, product_id: int = 0,
                    page: int = 1, per_page: int = 20) -> dict:
        """List builds."""
        params = {
            "executionID": execution_id,
            "productID": product_id,
            "recTotal": 0,
            "recPerPage": per_page,
            "pageID": page,
        }
        return self.call("build", "browse", params)

    def get_build(self, build_id: int) -> dict:
        """Get build details."""
        return self.call("build", "view", {"buildID": build_id})

    def create_build(self, data: dict) -> dict:
        """Create a new build.

        Args:
            data: Build fields (product, execution, name, date, builder, desc, etc.)

        Returns:
            API response with build ID
        """
        return self.call("build", "create", post_data=data)

    def delete_build(self, build_id: int) -> dict:
        """Delete a build."""
        return self.call("build", "delete", {"buildID": build_id})

    # ── User operations ────────────────────────────────────────────────

    def list_users(self) -> dict:
        """List all users."""
        return self.call("user", "manage")

    def get_user(self, user_id: int) -> dict:
        """Get user details."""
        return self.call("user", "view", {"userID": user_id})

    def create_user(self, data: dict) -> dict:
        """Create a new user.

        Args:
            data: User fields (account, password, realname, email, dept, etc.)

        Returns:
            API response
        """
        return self.call("user", "create", post_data=data)

    def update_user(self, user_id: int, data: dict) -> dict:
        """Update an existing user."""
        params = {"userID": user_id}
        return self.call("user", "edit", params, post_data=data)

    def delete_user(self, user_id: int) -> dict:
        """Delete a user."""
        return self.call("user", "delete", {"userID": user_id})

    # ── Report/Query operations ────────────────────────────────────────

    def get_product_report(self, product_id: int, browse_type: str = "all",
                           chart_type: str = "pie") -> dict:
        """Get product bug report."""
        params = {
            "productID": product_id,
            "browseType": browse_type,
            "chartType": chart_type,
        }
        return self.call("bug", "report", params)

    def get_task_report(self, execution_id: int, browse_type: str = "all",
                        chart_type: str = "default") -> dict:
        """Get task report for an execution."""
        params = {
            "executionID": execution_id,
            "browseType": browse_type,
            "chartType": chart_type,
        }
        return self.call("task", "report", params)

    # ── Connection test ────────────────────────────────────────────────

    # ── Effort / Work Hour ─────────────────────────────────────────────

    def list_efforts(self, task_id: int, account: str = "", order_by: str = "date,id") -> dict:
        """List effort (work hour) records for a task."""
        params = {"taskIdList": task_id, "orderBy": order_by}
        if account:
            params["account"] = account
        return self.call("task", "getTaskEfforts", params)

    def get_effort(self, effort_id: int) -> dict:
        """Get effort record by ID."""
        return self.call("task", "getTaskEfforts", {"taskIdList": "", "effortID": effort_id})

    def add_effort(self, data: dict) -> dict:
        """Add effort (work hour) to a task."""
        return self.call("task", "addTaskEffort", post_data=data)

    def update_effort(self, data: dict) -> dict:
        """Update an effort record."""
        return self.call("task", "updateEffort", post_data=data)

    def delete_effort(self, effort_id: int) -> dict:
        """Delete (soft-delete) an effort record."""
        return self.call("task", "deleteWorkhour", {"effortID": effort_id})

    def test_connection(self) -> dict:
        """Test connection to ZenTao instance.

        Returns:
            Dict with status and message
        """
        try:
            # Try to access the index page
            index_url = f"{self.url}/api.php?module=index&method=index"
            req = urllib.request.Request(index_url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                try:
                    data = json.loads(body)
                    return {"status": "ok", "message": "Connected to ZenTao", "response": data}
                except json.JSONDecodeError:
                    return {"status": "ok", "message": "Connected to ZenTao (non-JSON response)", "url": self.url}
        except urllib.error.HTTPError as e:
            return {"status": "warning", "message": f"HTTP {e.code} — server reachable but auth may be needed"}
        except Exception as e:
            return {"status": "error", "message": f"Connection failed: {e}"}
