"""Build management operations."""

from cli_anything.zentao.utils.zentao_backend import ZenTaoBackend


def list_builds(backend: ZenTaoBackend, execution_id: int = 0,
                product_id: int = 0, page: int = 1,
                per_page: int = 20) -> dict:
    """List builds.

    Args:
        backend: ZenTaoBackend instance
        execution_id: Execution ID filter (0 for all)
        product_id: Product ID filter (0 for all)
        page: Page number
        per_page: Items per page

    Returns:
        Dict with builds list and pagination info
    """
    return backend.list_builds(
        execution_id=execution_id, product_id=product_id,
        page=page, per_page=per_page,
    )


def get_build(backend: ZenTaoBackend, build_id: int) -> dict:
    """Get build details by ID."""
    return backend.get_build(build_id)


def create_build(backend: ZenTaoBackend, product_id: int, name: str,
                 execution_id: int = 0, date: str = "",
                 builder: str = "", desc: str = "",
                 filepath: str = "", **kwargs) -> dict:
    """Create a new build.

    Args:
        backend: ZenTaoBackend instance
        product_id: Product ID
        name: Build name/version
        execution_id: Execution ID (optional)
        date: Build date (YYYY-MM-DD, defaults to today)
        builder: Builder user account
        desc: Build description
        filepath: File path or URL for the build artifact
        **kwargs: Additional fields (stories, bugs, etc.)

    Returns:
        API response with build ID
    """
    data = {
        "product": product_id,
        "name": name,
        "execution": execution_id,
        "date": date,
        "builder": builder,
        "desc": desc,
        "filepath": filepath,
    }
    data.update(kwargs)
    return backend.create_build(data)


def delete_build(backend: ZenTaoBackend, build_id: int) -> dict:
    """Delete a build."""
    return backend.delete_build(build_id)
