from app.graph.mcp_client import get_tools
from app.graph.mcp_utils import normalize_mcp_output
from app.graph.state import InventraState


async def finance_agent(state: InventraState) -> dict:
    tools = await get_tools()

    raw_cash = await tools[
        "finance_cash_position"
    ].ainvoke(
        {"region": state.get("region")}
    )

    cash = normalize_mcp_output(raw_cash)

    margin = None

    if state.get("sku"):
        raw_margin = await tools[
            "finance_margin"
        ].ainvoke(
            {"sku": state["sku"]}
        )
        margin = normalize_mcp_output(raw_margin)

    return {
        "finance_result": {
            "cash_position": cash,
            "margin": margin,
        }
    }
