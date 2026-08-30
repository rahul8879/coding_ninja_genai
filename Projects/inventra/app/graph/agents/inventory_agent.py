from app.graph.mcp_client import get_tools
from app.graph.mcp_utils import get_error, normalize_mcp_output
from app.graph.state import InventraState


async def inventory_agent(state: InventraState) -> dict:
    sku = state.get("sku")

    if not sku:
        return {"error": "Inventory lookup requires a SKU."}

    tools = await get_tools()

    # Reorder workflow: use predicted demand.
    if state.get("forecast_result"):
        predicted = state["forecast_result"].get("predicted_qty")

        if predicted is None:
            return {"error": "Forecast result is missing predicted_qty."}

        raw = await tools[
            "inventory_stockout_risk"
        ].ainvoke(
            {
                "sku": sku,
                "predicted_demand": predicted,
            }
        )

    # Inventory-only request.
    else:
        raw = await tools[
            "inventory_get_stock"
        ].ainvoke({"sku": sku})

    result = normalize_mcp_output(raw)

    if error := get_error(result):
        return {
            "inventory_result": result,
            "error": error,
        }

    return {"inventory_result": result}
