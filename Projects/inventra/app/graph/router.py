from app.graph.state import InventraState


def after_planner(state: InventraState) -> str:
    if state.get("needs_forecast"):
        return "forecast"

    if state.get("needs_inventory"):
        return "inventory"

    if state.get("needs_finance"):
        return "finance"

    if state.get("needs_vendor"):
        return "vendor"

    return "aggregate"


def after_forecast(state: InventraState) -> str:
    if state.get("error"):
        return "aggregate"

    if state.get("needs_inventory"):
        return "inventory"

    return "aggregate"


def after_inventory(state: InventraState) -> str:
    if state.get("error"):
        return "aggregate"

    if state.get("intent") == "reorder_decision":
        return "reorder_decision"

    return "aggregate"


def after_reorder(state: InventraState) -> str:
    if state.get("reorder_needed"):
        return "finance"

    return "aggregate"


def after_finance(state: InventraState) -> str:
    # Finance-only request should end.
    if state.get("intent") == "finance":
        return "aggregate"

    # Reorder workflow continues to Vendor.
    if state.get("needs_vendor"):
        return "vendor"

    return "aggregate"
