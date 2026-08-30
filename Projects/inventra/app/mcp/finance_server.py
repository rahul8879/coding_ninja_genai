"""
Inventra Finance MCP Server.

Exposes FinanceService capabilities as MCP tools.

Available tools:
    1. cash_position()
    2. margin()

"""

import sys
from typing import Optional

from fastmcp import FastMCP

from app.services.finance_service import (
    get_finance_service,
)


# ---------------------------------------------------------
# Create MCP Server
# ---------------------------------------------------------

mcp = FastMCP(
    "inventra-finance"
)


# =========================================================
# Tool 1: Cash Position
# =========================================================

@mcp.tool()
def cash_position(
    region: Optional[str] = None,
) -> dict:
    """
    Calculate Inventra's net cash position.

    Net cash position is calculated from the finance ledger:

        total sale transactions
        -
        total purchase transactions

    The calculation can be performed for:

        - the complete company
        - a specific region

    Args:
        region:
            Optional region filter.

            Examples:
                North
                South
                East
                West
                Central

            If omitted, company-wide cash position
            is returned.

    Returns:
        Dictionary containing:

        - region
        - total_sales
        - sales_transaction_count
        - total_purchases
        - purchase_transaction_count
        - net_cash_position

    Important:
        Always use this tool when the user asks about
        available/net cash position based on Inventra's
        finance ledger.

        Never calculate or invent financial values
        inside the LLM.
    """

    service = get_finance_service()

    return service.cash_position(
        region=region
    )


# =========================================================
# Tool 2: SKU Margin
# =========================================================

@mcp.tool()
def margin(
    sku: str,
) -> dict:
    """
    Analyse historical unit economics for a product SKU.

    Combines:

    1. Inventory unit cost
    2. Historical sales revenue
    3. Historical quantity sold
    4. Finance ledger sale transactions
    5. Finance ledger purchase transactions

    Unit economics:

        average selling price
        -
        unit cost
        =
        unit margin

    Args:
        sku:
            Product SKU.

            Example:
                SKU045

    Returns:
        Dictionary containing:

        - sku
        - product name
        - category
        - unit cost
        - average selling price
        - unit margin
        - unit margin percentage
        - ledger total sales
        - ledger total purchases
        - ledger net cash flow

    Important:
        ledger_net_cash_flow is NOT the same as
        accounting gross margin.

        If the tool returns an "error" key,
        report the error instead of guessing.
    """

    service = get_finance_service()

    return service.margin(
        sku=sku
    )


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