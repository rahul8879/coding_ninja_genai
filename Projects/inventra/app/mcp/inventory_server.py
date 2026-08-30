"""
Inventra Inventory MCP Server.

Exposes InventoryService capabilities through MCP.

Available tools:
    1. get_stock()
    2. reorder_point()
    3. stockout_risk()
    4. list_low_stock_items()

Recommended business flow:

    forecast_demand()
        ↓
    predicted_qty
        ↓
    stockout_risk(sku, predicted_qty)
        ↓
    reorder recommendation
        ↓
    finance / vendor checks

"""

import sys

from fastmcp import FastMCP

from app.services.inventory_service import (
    get_inventory_service,
)


mcp = FastMCP(
    "inventra-inventory"
)


# =========================================================
# Tool 1: Current Stock
# =========================================================

@mcp.tool()
def get_stock(
    sku: str,
) -> dict:
    """
    Return the current inventory state for a product SKU.

    Use this when the user asks:
        - how much stock is available
        - current inventory quantity
        - reorder threshold
        - product/vendor mapping

    Args:
        sku:
            Product SKU, e.g. SKU045.

    Returns:
        Current stock and product metadata.

        If an "error" key is returned, do not guess.
    """

    service = get_inventory_service()

    return service.get_stock(
        sku=sku
    )


# =========================================================
# Tool 2: Reorder Threshold
# =========================================================

@mcp.tool()
def reorder_point(
    sku: str,
) -> dict:
    """
    Return the configured reorder threshold for a SKU.

    Important:
        The current Inventra dataset contains a
        reorder_threshold field.

        This tool does not invent statistical safety stock
        or service-level assumptions.

    Args:
        sku:
            Product SKU.

    Returns:
        Current stock, reorder threshold, and whether the
        SKU already requires reorder based on current stock.
    """

    service = get_inventory_service()

    return service.reorder_point(
        sku=sku
    )


# =========================================================
# Tool 3: Forecast-aware Stock Risk
# =========================================================

@mcp.tool()
def stockout_risk(
    sku: str,
    predicted_demand: float,
) -> dict:
    """
    Evaluate inventory risk using forecasted demand.

    ALWAYS use the numeric output returned by forecast_demand().
    Never ask the LLM to estimate predicted_demand.

    Calculation:

        projected stock =
            current stock - predicted demand

    A reorder is recommended when:

        projected stock <= reorder threshold

    Args:
        sku:
            Product SKU.

        predicted_demand:
            Numeric demand prediction from Forecast MCP.

    Returns:
        Current stock, predicted demand, projected stock,
        reorder threshold, stockout risk, reorder recommendation,
        recommended reorder quantity, and estimated reorder cost.
    """

    service = get_inventory_service()

    return service.stockout_risk(
        sku=sku,
        predicted_demand=predicted_demand,
    )


# =========================================================
# Tool 4: Current Low-stock Items
# =========================================================

@mcp.tool()
def list_low_stock_items() -> list[dict]:
    """
    Return all SKUs currently at or below their configured
    reorder threshold.

    This is useful for:
        - operational dashboards
        - proactive inventory checks
        - agent planning
    """

    service = get_inventory_service()

    return service.list_low_stock_items()


# =========================================================
# Start MCP Server
# =========================================================

if __name__ == "__main__":

    if "--http" in sys.argv:

        mcp.run(
            transport="streamable-http"
        )

    else:

        mcp.run(
            transport="stdio"
        )
