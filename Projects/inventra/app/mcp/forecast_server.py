"""
Exposes the demand forecasting capability through MCP.
"""
import sys
from typing import Literal

from fastmcp import FastMCP

from app.services.forecast_service import get_forecast_service
from db.session import SessionLocal
from db.models import Inventory

mcp = FastMCP("inventra-forecast")

@mcp.tool()
def forecast_demand(
    sku: str,
    region: str,
    weather_condition: str,
    temperature: float,
    rainfall: float,
    humidity: float,
    month: int,
    day_of_week: int,
    is_weekend: Literal[0, 1],
) -> dict:
    """
    Predict numerical demand for a product.

    ALWAYS use this tool when a numeric demand forecast is required.
    Never estimate demand using the LLM.

    SKU is a business identifier. The service looks up the category
    from the inventory database before calling the ML pipeline.

    Args:
        sku: Product SKU, e.g. SKU045.
        region: Sales region.
        weather_condition: Weather condition such as Rainy or Sunny.
        temperature: Temperature in Celsius.
        rainfall: Rainfall in millimeters.
        humidity: Humidity percentage.
        month: Integer from 1 to 12.
        day_of_week: 0 = Monday ... 6 = Sunday.
        is_weekend: 1 for Saturday/Sunday, otherwise 0.

    Returns:
        Structured demand forecast.
        If an "error" key is returned, do not guess.
    """

    service = get_forecast_service()

    return service.predict(
        sku=sku,
        region=region,
        weather_condition=weather_condition,
        temperature=temperature,
        rainfall=rainfall,
        humidity=humidity,
        month=month,
        day_of_week=day_of_week,
        is_weekend=is_weekend,
    )


@mcp.tool()
def list_valid_skus() -> list[str]:
    """
    Return SKUs available in Inventra's inventory database.

    SKU is not directly used as an ML feature.
    """

    db = SessionLocal()

    try:
        rows = (
            db.query(Inventory.sku)
            .order_by(Inventory.sku)
            .all()
        )

        return [row[0] for row in rows]

    finally:
        db.close()


@mcp.tool()
def list_valid_categories() -> list[str]:
    """Return categories learned by the forecasting model."""

    service = get_forecast_service()

    return sorted(
        service.valid_categories["category"]
    )


@mcp.tool()
def list_valid_regions() -> list[str]:
    """Return regions learned by the forecasting model."""

    service = get_forecast_service()

    return sorted(
        service.valid_categories["region"]
    )


@mcp.tool()
def list_valid_weather_conditions() -> list[str]:
    """Return weather conditions learned by the forecasting model."""

    service = get_forecast_service()

    return sorted(
        service.valid_categories["weather_condition"]
    )


if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")

