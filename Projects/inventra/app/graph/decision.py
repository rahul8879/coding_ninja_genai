from app.graph.state import InventraState


async def reorder_decision(state: InventraState) -> dict:
    """Deterministic reorder gate."""

    inventory = state.get("inventory_result") or {}

    return {
        "reorder_needed": bool(
            inventory.get("reorder_recommended", False)
        )
    }
