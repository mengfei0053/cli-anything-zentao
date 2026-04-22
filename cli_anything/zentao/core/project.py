"""Project management operations."""

from typing import Optional
from cli_anything.zentao.utils.zentao_backend import ZenTaoBackend


def list_projects(backend: ZenTaoBackend, status: str = "all",
                  order_by: str = "order_asc", page: int = 1,
                  per_page: int = 20) -> dict:
    """List all projects.

    Args:
        backend: ZenTaoBackend instance
        status: Filter by status (all, undone, closed, waited)
        order_by: Sort order
        page: Page number
        per_page: Items per page

    Returns:
        Dict with projects list and pagination info
    """
    return backend.list_projects(status=status, order_by=order_by,
                                  page=page, per_page=per_page)


def get_project(backend: ZenTaoBackend, project_id: int) -> dict:
    """Get project details by ID."""
    return backend.get_project(project_id)


def create_project(backend: ZenTaoBackend, name: str, code: str,
                   model: str = "scrum", project_type: str = "sprint",
                   begin: str = "", end: str = "", desc: str = "",
                   parent: int = 0, **kwargs) -> dict:
    """Create a new project.

    Args:
        backend: ZenTaoBackend instance
        name: Project name
        code: Project code (unique identifier)
        model: Project model (scrum, waterfall, kanban, devops)
        project_type: Type (sprint, stage, ops, feature, etc.)
        begin: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD)
        desc: Project description
        parent: Parent project ID
        **kwargs: Additional fields (budget, days, etc.)

    Returns:
        API response with project ID
    """
    data = {
        "name": name,
        "code": code,
        "model": model,
        "type": project_type,
        "begin": begin,
        "end": end,
        "desc": desc,
        "parent": parent,
    }
    data.update(kwargs)
    return backend.create_project(data)


def update_project(backend: ZenTaoBackend, project_id: int, **kwargs) -> dict:
    """Update an existing project.

    Args:
        backend: ZenTaoBackend instance
        project_id: Project ID
        **kwargs: Fields to update (name, code, begin, end, desc, status, etc.)

    Returns:
        API response
    """
    return backend.update_project(project_id, kwargs)


def delete_project(backend: ZenTaoBackend, project_id: int) -> dict:
    """Delete a project."""
    return backend.delete_project(project_id)
