"""Product management operations."""

from typing import Optional
from cli_anything.zentao.utils.zentao_backend import ZenTaoBackend


def list_products(backend: ZenTaoBackend, status: str = "all",
                  order_by: str = "order_asc", page: int = 1,
                  per_page: int = 20) -> dict:
    """List all products.

    Args:
        backend: ZenTaoBackend instance
        status: Filter by status (all, noclosed, closed)
        order_by: Sort order (order_asc, order_desc, id_desc, name_asc)
        page: Page number
        per_page: Items per page

    Returns:
        Dict with products list and pagination info
    """
    return backend.list_products(status=status, order_by=order_by,
                                  page=page, per_page=per_page)


def get_product(backend: ZenTaoBackend, product_id: int) -> dict:
    """Get product details by ID."""
    return backend.get_product(product_id)


def create_product(backend: ZenTaoBackend, name: str, code: str,
                   product_type: str = "normal", desc: str = "",
                   po: str = "", qd: str = "", rd: str = "",
                   acl: str = "open", **kwargs) -> dict:
    """Create a new product.

    Args:
        backend: ZenTaoBackend instance
        name: Product name
        code: Product code (unique identifier)
        product_type: Type (normal, platform, branch)
        desc: Product description
        po: Product Owner account
        qd: Quality Director account
        rd: Release Director account
        acl: Access control (open, private, whitelist)
        **kwargs: Additional fields

    Returns:
        API response with product ID
    """
    data = {
        "name": name,
        "code": code,
        "type": product_type,
        "desc": desc,
        "PO": po,
        "QD": qd,
        "RD": rd,
        "acl": acl,
    }
    data.update(kwargs)
    return backend.create_product(data)


def update_product(backend: ZenTaoBackend, product_id: int, **kwargs) -> dict:
    """Update an existing product.

    Args:
        backend: ZenTaoBackend instance
        product_id: Product ID
        **kwargs: Fields to update (name, code, desc, status, etc.)

    Returns:
        API response
    """
    return backend.update_product(product_id, kwargs)


def delete_product(backend: ZenTaoBackend, product_id: int) -> dict:
    """Delete a product."""
    return backend.delete_product(product_id)
