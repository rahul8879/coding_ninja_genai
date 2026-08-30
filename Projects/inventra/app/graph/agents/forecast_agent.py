from datetime import datetime
from app.graph.mcp_client import get_tools
from app.graph.mcp_utils import get_error, normalize_mcp_output
from app.graph.state import InventraState


async def forecast_agent(state: InventraState) -> dict:
    sku = state.get("sku")
    region = state.get("region")

    if not sku:
        return {"error": "Forecast requires a SKU."}

    if not region:
        return {"error": "Forecast requires a region."}

    tools = await get_tools()

    # 1. Weather
    raw_weather = await tools[
        "weather_get_weather_forecast"
    ].ainvoke(
        {
            "region": region,
            "date": state.get("target_date"),
        }
    )

    weather = normalize_mcp_output(raw_weather)

    if error := get_error(weather):
        return {
            "weather_result": weather,
            "error": error,
        }

    # 2. Calendar features
    forecast_date = datetime.strptime(
        weather["date"],
        "%Y-%m-%d",
    )

    # 3. Demand forecast
    raw_forecast = await tools[
        "forecast_forecast_demand"
    ].ainvoke(
        {
            "sku": sku,
            "region": region,
            "weather_condition": weather["weather_condition"],
            "temperature": weather["temperature"],
            "rainfall": weather["rainfall"],
            "humidity": weather["humidity"],
            "month": forecast_date.month,
            "day_of_week": forecast_date.weekday(),
            "is_weekend": int(forecast_date.weekday() >= 5),
        }
    )

    forecast = normalize_mcp_output(raw_forecast)

    if error := get_error(forecast):
        return {
            "weather_result": weather,
            "forecast_result": forecast,
            "error": error,
        }

    return {
        "weather_result": weather,
        "forecast_result": forecast,
    }
