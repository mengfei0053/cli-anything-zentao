"""Task effort (工时) operations."""

from typing import Optional


def list_efforts(backend, task_id: int, account: str = "", order_by: str = "date,id") -> list:
    """List all efforts (work hours) for a task."""
    return backend.list_efforts(task_id, account, order_by)


def get_effort(backend, effort_id: int) -> dict:
    """Get effort details by ID."""
    return backend.get_effort(effort_id)


def add_effort(backend, task_id: int, consumed: float, left: Optional[float] = None,
               date: Optional[str] = None, account: Optional[str] = None,
               work: Optional[str] = None) -> dict:
    """Add effort (work hour) record to a task."""
    data = {"task": task_id, "consumed": consumed}
    if left is not None:
        data["left"] = left
    if date:
        data["date"] = date
    if account:
        data["account"] = account
    if work:
        data["work"] = work
    return backend.add_effort(data)


def update_effort(backend, effort_id: int, consumed: Optional[float] = None,
                  left: Optional[float] = None, date: Optional[str] = None,
                  work: Optional[str] = None) -> dict:
    """Update an effort record."""
    data = {"id": effort_id}
    if consumed is not None:
        data["consumed"] = consumed
    if left is not None:
        data["left"] = left
    if date:
        data["date"] = date
    if work is not None:
        data["work"] = work
    return backend.update_effort(data)


def delete_effort(backend, effort_id: int) -> dict:
    """Delete (soft-delete) an effort record."""
    return backend.delete_effort(effort_id)
