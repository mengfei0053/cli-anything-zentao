"""Test case management operations."""

from cli_anything.zentao.utils.zentao_backend import ZenTaoBackend


def list_testcases(backend: ZenTaoBackend, product_id: int, branch: str = "all",
                   browse_type: str = "all", case_type: str = "",
                   order_by: str = "id_desc", page: int = 1,
                   per_page: int = 20) -> dict:
    """List test cases for a product.

    Args:
        backend: ZenTaoBackend instance
        product_id: Product ID
        branch: Branch filter
        browse_type: Browse type (all, normal, automation, manual, etc.)
        case_type: Case type filter
        order_by: Sort order
        page: Page number
        per_page: Items per page

    Returns:
        Dict with test cases list and pagination info
    """
    return backend.list_testcases(
        product_id=product_id, branch=branch, browse_type=browse_type,
        case_type=case_type, order_by=order_by, page=page, per_page=per_page,
    )


def get_testcase(backend: ZenTaoBackend, case_id: int) -> dict:
    """Get test case details by ID."""
    return backend.get_testcase(case_id)


def create_testcase(backend: ZenTaoBackend, product_id: int, title: str,
                    precondition: str = "", steps: str = "",
                    pri: int = 3, case_type: str = "functional",
                    stage: str = "unittest", **kwargs) -> dict:
    """Create a new test case.

    Args:
        backend: ZenTaoBackend instance
        product_id: Product ID
        title: Test case title
        precondition: Prerequisites for running this test
        steps: Test steps (detailed procedure)
        pri: Priority (1=highest, 4=lowest)
        case_type: Type (functional, interface, performance, config,
                   install, security, other)
        stage: Stage (unittest, featuretest, stagetest, phasestage, release)
        **kwargs: Additional fields (module, automation, script, etc.)

    Returns:
        API response with test case ID
    """
    data = {
        "product": product_id,
        "title": title,
        "precondition": precondition,
        "steps": steps,
        "pri": pri,
        "type": case_type,
        "stage": stage,
    }
    data.update(kwargs)
    return backend.create_testcase(data)


def update_testcase(backend: ZenTaoBackend, case_id: int, **kwargs) -> dict:
    """Update an existing test case.

    Args:
        backend: ZenTaoBackend instance
        case_id: Test case ID
        **kwargs: Fields to update (title, steps, pri, status, etc.)

    Returns:
        API response
    """
    return backend.update_testcase(case_id, kwargs)
