"""Story/Requirement management operations."""

from typing import Optional
from cli_anything.zentao.utils.zentao_backend import ZenTaoBackend


def list_stories(backend: ZenTaoBackend, product_id: int, branch: str = "all",
                 browse_type: str = "all", story_type: str = "story",
                 order_by: str = "id_desc", page: int = 1,
                 per_page: int = 20) -> dict:
    """List stories/requirements for a product.

    Args:
        backend: ZenTaoBackend instance
        product_id: Product ID
        branch: Branch filter (all, specific branch ID)
        browse_type: Browse type (all, bysearch, unclosed, changed, etc.)
        story_type: Story type (story, requirement)
        order_by: Sort order
        page: Page number
        per_page: Items per page

    Returns:
        Dict with stories list and pagination info
    """
    return backend.list_stories(
        product_id=product_id, branch=branch, browse_type=browse_type,
        story_type=story_type, order_by=order_by, page=page, per_page=per_page,
    )


def get_story(backend: ZenTaoBackend, story_id: int,
              story_type: str = "story") -> dict:
    """Get story details by ID."""
    return backend.get_story(story_id, story_type=story_type)


def create_story(backend: ZenTaoBackend, product_id: int, title: str,
                 spec: str = "", story_type: str = "story",
                 pri: int = 3, category: str = "feature",
                 source: str = "", plan: str = "",
                 assigned_to: str = "", estimate: float = 0,
                 module_id: int = 0, **kwargs) -> dict:
    """Create a new story/requirement.

    Args:
        backend: ZenTaoBackend instance
        product_id: Product ID
        title: Story title
        spec: Story specification (detailed description)
        story_type: Type (story, requirement)
        pri: Priority (1=highest, 4=lowest)
        category: Category (feature, interface, performance, security, etc.)
        source: Source (customer, market, research, etc.)
        plan: Product plan IDs (comma-separated)
        assigned_to: Assigned user account
        estimate: Estimated hours
        module_id: Module ID
        **kwargs: Additional fields

    Returns:
        API response with story ID
    """
    data = {
        "product": product_id,
        "title": title,
        "spec": spec,
        "type": story_type,
        "pri": pri,
        "category": category,
        "source": source,
        "plan": plan,
        "assignedTo": assigned_to,
        "estimate": estimate,
        "module": module_id,
    }
    data.update(kwargs)
    return backend.create_story(data)


def update_story(backend: ZenTaoBackend, story_id: int, **kwargs) -> dict:
    """Update an existing story.

    Args:
        backend: ZenTaoBackend instance
        story_id: Story ID
        **kwargs: Fields to update (title, spec, pri, status, etc.)

    Returns:
        API response
    """
    return backend.update_story(story_id, kwargs)


def close_story(backend: ZenTaoBackend, story_id: int,
                reason: str = "") -> dict:
    """Close a story."""
    return backend.close_story(story_id, reason=reason)


def activate_story(backend: ZenTaoBackend, story_id: int) -> dict:
    """Activate a closed story."""
    return backend.activate_story(story_id)
