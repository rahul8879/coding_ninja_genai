from app.graph.state import InventraState


async def aggregate_results(state: InventraState) -> dict:
    return {
        "aggregated_result": {
            "request": {
                "sku": state.get("sku"),
                "vendor_id": state.get("vendor_id"),
                "region": state.get("region"),
                "target_date": state.get("target_date"),
                "intent": state.get("intent"),
            },
            "weather": state.get("weather_result"),
            "forecast": state.get("forecast_result"),
            "inventory": state.get("inventory_result"),
            "reorder_needed": state.get("reorder_needed"),
            "finance": state.get("finance_result"),
            "vendor": state.get("vendor_result"),
        }
    }
