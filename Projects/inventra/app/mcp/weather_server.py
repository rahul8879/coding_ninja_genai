"""
Inventra Weather MCP Server.

Exposes real weather forecasts as an MCP capability.

Recommended agent flow:

    User request
        ↓
    get_weather_forecast()
        ↓
    WeatherService
        ↓
    OpenWeatherMap
        ↓
    normalized weather
        ↓
    forecast_demand()

"""

import sys
from typing import Optional

from fastmcp import FastMCP

from app.services.weather_service import (
    get_weather_service,
)


# ---------------------------------------------------------
# Create MCP server
# ---------------------------------------------------------

mcp = FastMCP(
    "inventra-weather"
)


# =========================================================
# Weather Forecast Tool
# =========================================================

@mcp.tool()
def get_weather_forecast(
    region: str,
    date: Optional[str] = None,
) -> dict:
    """
    Get a real weather forecast for an Inventra business region.

    ALWAYS use this tool before forecast_demand() when a
    future-demand question requires weather information.

    Never ask the LLM to invent:
        temperature
        rainfall
        humidity
        weather condition

    Args:
        region:
            One of:
                North
                South
                East
                West
                Central

        date:
            Optional date in YYYY-MM-DD format.

            If omitted, tomorrow is used.

            The OpenWeatherMap 5-day/3-hour endpoint provides
            forecasts only for approximately the next 5 days.

    Returns:
        A structured weather result containing:

            region
            city_used
            date
            temperature
            rainfall
            humidity
            weather_condition
            raw_openweather_condition
            source

        The `weather_condition` field is normalized into the
        same vocabulary used during Inventra model training.

        If an `error` key is returned:
            - do not invent weather values
            - do not call forecast_demand with guessed values
            - report the limitation to the user
    """

    service = get_weather_service()

    return service.get_weather_forecast(
        region=region,
        date=date,
    )


# =========================================================
# Region Discovery Tool
# =========================================================

@mcp.tool()
def list_supported_regions() -> list[str]:
    """
    Return Inventra business regions supported by
    WeatherService.
    """

    from app.services.weather_service import (
        REGION_TO_CITY,
    )

    return sorted(
        REGION_TO_CITY.keys()
    )


# =========================================================
# Start MCP server
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
