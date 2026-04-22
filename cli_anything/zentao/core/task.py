"""Task management operations."""

from cli_anything.zentao.utils.zentao_backend import ZenTaoBackend


def list_tasks(backend: ZenTaoBackend, execution_id: int, status: str = "all",
               order_by: str = "id_desc", page: int = 1,
               per_page: int = 20) -> dict:
    """List tasks for an execution.

    Args:
        backend: ZenTaoBackend instance
        execution_id: Execution/project ID
        status: Filter by status (all, undone, doing, done, closed, cancel)
        order_by: Sort order
        page: Page number
        per_page: Items per page

    Returns:
        Dict with tasks list and pagination info
    """
    return backend.list_tasks(
        execution_id=execution_id, status=status,
        order_by=order_by, page=page, per_page=per_page,
    )


def get_task(backend: ZenTaoBackend, task_id: int) -> dict:
    """Get task details by ID."""
    return backend.get_task(task_id)


def create_task(backend: ZenTaoBackend, execution_id: int, name: str,
                task_type: str = "devel", pri: int = 3,
                estimate: float = 0, assigned_to: str = "",
                desc: str = "", **kwargs) -> dict:
    """Create a new task.

    Args:
        backend: ZenTaoBackend instance
        execution_id: Execution/project ID
        name: Task name
        task_type: Type (devel, design, test, study, discussion, ui, affair)
        pri: Priority (1=highest, 4=lowest)
        estimate: Estimated hours
        assigned_to: Assigned user account
        desc: Task description
        **kwargs: Additional fields (consumed, deadline, module, etc.)

    Returns:
        API response with task ID
    """
    data = {
        "execution": execution_id,
        "name": name,
        "type": task_type,
        "pri": pri,
        "estimate": estimate,
        "assignedTo": assigned_to,
        "desc": desc,
    }
    data.update(kwargs)
    return backend.create_task(data)


def update_task(backend: ZenTaoBackend, task_id: int, **kwargs) -> dict:
    """Update an existing task.

    Args:
        backend: ZenTaoBackend instance
        task_id: Task ID
        **kwargs: Fields to update (name, assignedTo, status, estimate, etc.)

    Returns:
        API response
    """
    return backend.update_task(task_id, kwargs)


def start_task(backend: ZenTaoBackend, task_id: int) -> dict:
    """Start a task (mark as in-progress)."""
    return backend.start_task(task_id)


def finish_task(backend: ZenTaoBackend, task_id: int,
                consumed: float = 0, **kwargs) -> dict:
    """Finish a task.

    Args:
        backend: ZenTaoBackend instance
        task_id: Task ID
        consumed: Actual consumed hours
        **kwargs: Additional fields (finishedBy, etc.)
    """
    data = {"consumed": consumed}
    data.update(kwargs)
    return backend.finish_task(task_id, data=data)


def close_task(backend: ZenTaoBackend, task_id: int) -> dict:
    """Close a task."""
    return backend.close_task(task_id)


def cancel_task(backend: ZenTaoBackend, task_id: int) -> dict:
    """Cancel a task."""
    return backend.cancel_task(task_id)
