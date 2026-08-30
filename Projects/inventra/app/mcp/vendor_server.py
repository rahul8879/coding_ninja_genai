"""
Inventra Vendor MCP Server.

Exposes VendorService capabilities through MCP.

Available tools:
    1. list_vendors()
    2. vendor_details()
    3. lead_time()
    4. supplier_score()

Run:
    python -m app.mcp.vendor_server

Inspector:
    npx @modelcontextprotocol/inspector python -m app.mcp.vendor_server
"""

import sys

from fastmcp import FastMCP

from app.services.vendor_service import get_vendor_service


mcp = FastMCP("inventra-vendor")


@mcp.tool()
def list_vendors() -> list[dict]:
    """Return all vendors available in Inventra's vendor master."""

    service = get_vendor_service()
    return service.list_vendors()


@mcp.tool()
def vendor_details(vendor_id: str) -> dict:
    """
    Return the complete profile for a vendor.

    Args:
        vendor_id: Vendor identifier, e.g. V001.

    If an "error" key is returned, do not guess.
    """

    service = get_vendor_service()

    return service.vendor_details(
        vendor_id=vendor_id
    )


@mcp.tool()
def lead_time(vendor_id: str) -> dict:
    """
    Return vendor lead time and delivery reliability.

    Use this when a reorder decision depends on how quickly
    new stock can arrive.
    """

    service = get_vendor_service()

    return service.lead_time(
        vendor_id=vendor_id
    )


@mcp.tool()
def supplier_score(vendor_id: str) -> dict:
    """
    Return a transparent deterministic supplier score.

    Uses:
        on-time delivery
        quality
        reliability
        return acceptance
        average delay

    This is a POC business-rule score, not an ML prediction.
    """

    service = get_vendor_service()

    return service.supplier_score(
        vendor_id=vendor_id
    )


if __name__ == "__main__":

    if "--http" in sys.argv:
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")
