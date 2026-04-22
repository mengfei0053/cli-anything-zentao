"""Bug management operations."""

from cli_anything.zentao.utils.zentao_backend import ZenTaoBackend


def list_bugs(backend: ZenTaoBackend, product_id: int, branch: str = "all",
              browse_type: str = "all", order_by: str = "id_desc",
              page: int = 1, per_page: int = 20) -> dict:
    """List bugs for a product.

    Args:
        backend: ZenTaoBackend instance
        product_id: Product ID
        branch: Branch filter
        browse_type: Browse type (all, active, resolved, closed, bysearch, etc.)
        order_by: Sort order
        page: Page number
        per_page: Items per page

    Returns:
        Dict with bugs list and pagination info
    """
    return backend.list_bugs(
        product_id=product_id, branch=branch, browse_type=browse_type,
        order_by=order_by, page=page, per_page=per_page,
    )


def get_bug(backend: ZenTaoBackend, bug_id: int) -> dict:
    """Get bug details by ID."""
    return backend.get_bug(bug_id)


def create_bug(backend: ZenTaoBackend, product_id: int, title: str,
               severity: int = 3, pri: int = 3,
               bug_type: str = "codeerror", steps: str = "",
               opened_build: str = "", assigned_to: str = "",
               desc: str = "", **kwargs) -> dict:
    """Create a new bug.

    Args:
        backend: ZenTaoBackend instance
        product_id: Product ID
        title: Bug title
        severity: Severity (1=fatal, 2=serious, 3=general, 4=suggestion)
        pri: Priority (1=highest, 4=lowest)
        bug_type: Type (codeerror, interface, performance, security,
                    standard, designchange, configlevel, install,
                    trackthings, others)
        steps: Steps to reproduce
        opened_build: The build where bug was found
        assigned_to: Assigned user account
        desc: Bug description
        **kwargs: Additional fields (module, os, browser, etc.)

    Returns:
        API response with bug ID
    """
    data = {
        "product": product_id,
        "title": title,
        "severity": severity,
        "pri": pri,
        "type": bug_type,
        "steps": steps,
        "openedBuild": opened_build,
        "assignedTo": assigned_to,
        "desc": desc,
    }
    data.update(kwargs)
    return backend.create_bug(data)


def update_bug(backend: ZenTaoBackend, bug_id: int, **kwargs) -> dict:
    """Update an existing bug.

    Args:
        backend: ZenTaoBackend instance
        bug_id: Bug ID
        **kwargs: Fields to update (title, severity, pri, status, etc.)

    Returns:
        API response
    """
    return backend.update_bug(bug_id, kwargs)


def resolve_bug(backend: ZenTaoBackend, bug_id: int,
                resolution: str = "fixed", resolved_build: str = "",
                **kwargs) -> dict:
    """Resolve a bug.

    Args:
        backend: ZenTaoBackend instance
        bug_id: Bug ID
        resolution: Resolution (fixed, postoned, willnotfix, bydesign,
                    external, notrepro, duplicate, sub)
        resolved_build: The build where bug was resolved
        **kwargs: Additional fields (resolvedBy, etc.)
    """
    data = {"resolution": resolution, "resolvedBuild": resolved_build}
    data.update(kwargs)
    return backend.resolve_bug(bug_id, data=data)


def activate_bug(backend: ZenTaoBackend, bug_id: int) -> dict:
    """Activate a resolved bug (reopen)."""
    return backend.activate_bug(bug_id)


def close_bug(backend: ZenTaoBackend, bug_id: int) -> dict:
    """Close a bug."""
    return backend.close_bug(bug_id)
