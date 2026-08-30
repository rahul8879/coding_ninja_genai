from app.graph.mcp_client import get_tools
from app.graph.mcp_utils import normalize_mcp_output
from app.graph.state import InventraState


async def vendor_agent(state: InventraState) -> dict:
    # Direct vendor query, if supplied.
    vendor_id = state.get("vendor_id")

    # Reorder workflow: vendor comes from inventory.
    if not vendor_id:
        vendor_id = (
            state.get("inventory_result") or {}
        ).get("vendor_id")

    if not vendor_id:
        return {
            "vendor_result": {
                "error": "Vendor ID is not available."
            }
        }

    tools = await get_tools()

    details = normalize_mcp_output(
        await tools["vendor_vendor_details"].ainvoke(
            {"vendor_id": vendor_id}
        )
    )

    lead_time = normalize_mcp_output(
        await tools["vendor_lead_time"].ainvoke(
            {"vendor_id": vendor_id}
        )
    )

    supplier_score = normalize_mcp_output(
        await tools["vendor_supplier_score"].ainvoke(
            {"vendor_id": vendor_id}
        )
    )

    return {
        "vendor_result": {
            "vendor_details": details,
            "lead_time": lead_time,
            "supplier_score": supplier_score,
        }
    }
