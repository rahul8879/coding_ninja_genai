"""
Inventra Weather Service.

Fetches real weather forecasts from OpenWeatherMap and normalizes them
into the same weather categories used during Inventra model training.

POC region mapping:
    North   -> Delhi
    South   -> Chennai
    East    -> Kolkata
    West    -> Mumbai
    Central -> Nagpur

IMPORTANT:
These are representative cities for a classroom/POC implementation.
A production system should map business regions to actual warehouse/store
coordinates and aggregate weather across those locations.
"""

import os
from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

import requests
from dotenv import load_dotenv


# ---------------------------------------------------------
# Load environment variables from .env
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# Business region -> representative city
# ---------------------------------------------------------

REGION_TO_CITY = {
    "North": "Delhi,IN",
    "South": "Chennai,IN",
    "East": "Kolkata,IN",
    "West": "Mumbai,IN",
    "Central": "Nagpur,IN",
}


# ---------------------------------------------------------
# OpenWeatherMap endpoint
# ---------------------------------------------------------

OPENWEATHER_BASE_URL = (
    "https://api.openweathermap.org/data/2.5/forecast"
)


# ---------------------------------------------------------
# Deterministic normalization rules
# ---------------------------------------------------------
#
# OpenWeatherMap uses categories such as:
#
#   Clear
#   Clouds
#   Rain
#   Drizzle
#   Thunderstorm
#   Mist
#
# Our historical training data uses:
#
#   Clear
#   Cloudy
#   Cold
#   Heatwave
#   Heavy Rain
#   Partly Cloudy
#   Rainy
#   Sunny
#   Thunderstorm
#
# We therefore normalize OpenWeatherMap output into the
# vocabulary used during model training.
#
# These thresholds are POC business rules.
# They are NOT learned by XGBoost.
# ---------------------------------------------------------

HEATWAVE_TEMP_C = 38.0
COLD_TEMP_C = 15.0
HEAVY_RAIN_MM = 20.0


def map_owm_condition_to_trained(
    owm_main: str,
    temperature: float,
    rainfall: float,
) -> str:
    """
    Convert an OpenWeatherMap condition into one of the
    weather categories used during Inventra model training.

    Args:
        owm_main:
            OpenWeatherMap's main weather label.

        temperature:
            Average temperature in Celsius.

        rainfall:
            Total rainfall in millimeters for the selected day.

    Returns:
        A training-compatible weather condition.
    """

    # Temperature-based business rules come first.
    if temperature >= HEATWAVE_TEMP_C:
        return "Heatwave"

    if temperature <= COLD_TEMP_C:
        return "Cold"

    condition = (owm_main or "").strip().lower()

    if condition == "thunderstorm":
        return "Thunderstorm"

    if condition in ("rain", "drizzle"):
        if rainfall >= HEAVY_RAIN_MM:
            return "Heavy Rain"

        return "Rainy"

    if condition == "clouds":
        return "Partly Cloudy"

    if condition == "clear":
        return "Sunny"

    # OpenWeatherMap conditions such as:
    # Mist, Fog, Haze, Dust, Smoke, Snow, Squall, etc.
    #
    # The historical training data does not have dedicated
    # categories for these conditions. For this classroom POC
    # we map them to the closest neutral category.
    return "Cloudy"


class WeatherService:
    """
    Fetch and normalize weather forecasts for Inventra regions.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
    ) -> None:
        """
        Load the API key either from the supplied argument or
        from the OPENWEATHER_API_KEY environment variable.
        """

        self.api_key = (
            api_key
            or os.getenv("OPENWEATHER_API_KEY")
        )

    def get_weather_forecast(
        self,
        region: str,
        date: Optional[str] = None,
    ) -> dict:
        """
        Get a real weather forecast for an Inventra business region.

        Args:
            region:
                One of:
                    North
                    South
                    East
                    West
                    Central

            date:
                Date in YYYY-MM-DD format.

                If omitted, tomorrow is used.

                OpenWeatherMap's free 5-day/3-hour endpoint only
                provides forecasts for approximately the next 5 days.

        Returns:
            Dictionary containing:
                region
                city_used
                date
                temperature
                rainfall
                humidity
                weather_condition
                raw_openweather_condition

            Returns an "error" key when:
                - API key is missing
                - region is invalid
                - date is malformed
                - requested date is outside available forecast data
                - OpenWeatherMap request fails
        """

        # -------------------------------------------------
        # Validate API key
        # -------------------------------------------------

        if not self.api_key:
            return {
                "error": (
                    "OPENWEATHER_API_KEY is not set. "
                    "Add it to your .env file."
                )
            }

        # -------------------------------------------------
        # Validate business region
        # -------------------------------------------------

        if region not in REGION_TO_CITY:
            return {
                "error": (
                    f"Unknown region '{region}'. "
                    f"Valid regions: "
                    f"{list(REGION_TO_CITY.keys())}"
                )
            }

        # -------------------------------------------------
        # Resolve target date
        # -------------------------------------------------

        if date is None:
            target_date = (
                datetime.utcnow()
                + timedelta(days=1)
            ).strftime("%Y-%m-%d")

        else:
            try:
                parsed_date = datetime.strptime(
                    date,
                    "%Y-%m-%d",
                )

                target_date = parsed_date.strftime(
                    "%Y-%m-%d"
                )

            except ValueError:
                return {
                    "error": (
                        f"Invalid date '{date}'. "
                        "Use YYYY-MM-DD format."
                    )
                }

        city = REGION_TO_CITY[region]

        # -------------------------------------------------
        # Call OpenWeatherMap
        # -------------------------------------------------

        try:
            response = requests.get(
                OPENWEATHER_BASE_URL,
                params={
                    "q": city,
                    "appid": self.api_key,
                    "units": "metric",
                },
                timeout=10,
            )

            response.raise_for_status()

            data = response.json()

        except requests.exceptions.RequestException as exc:
            return {
                "error": (
                    f"Weather API request failed: {exc}"
                )
            }

        # -------------------------------------------------
        # Select forecast entries for requested date
        # -------------------------------------------------

        all_entries = data.get("list", [])

        if not all_entries:
            return {
                "error": (
                    "OpenWeatherMap returned no forecast data."
                )
            }

        entries_for_date = [
            entry
            for entry in all_entries
            if entry.get("dt_txt", "").startswith(
                target_date
            )
        ]

        # -------------------------------------------------
        # IMPORTANT:
        #
        # Do NOT silently substitute another date.
        #
        # If the requested date is outside the API's
        # available forecast horizon, return a clear error.
        # -------------------------------------------------

        if not entries_for_date:
            first_available_date = (
                all_entries[0]["dt_txt"][:10]
            )

            last_available_date = (
                all_entries[-1]["dt_txt"][:10]
            )

            return {
                "error": (
                    f"No weather forecast is available "
                    f"for {target_date}. "
                    f"Available forecast window is approximately "
                    f"{first_available_date} to "
                    f"{last_available_date}."
                ),
                "requested_date": target_date,
                "first_available_date": (
                    first_available_date
                ),
                "last_available_date": (
                    last_available_date
                ),
            }

        # -------------------------------------------------
        # Aggregate 3-hour forecasts into daily values
        # -------------------------------------------------

        temperatures = [
            entry["main"]["temp"]
            for entry in entries_for_date
        ]

        humidities = [
            entry["main"]["humidity"]
            for entry in entries_for_date
        ]

        rainfall_total = sum(
            entry
            .get("rain", {})
            .get("3h", 0.0)
            for entry in entries_for_date
        )

        conditions = [
            entry["weather"][0]["main"]
            for entry in entries_for_date
            if entry.get("weather")
        ]

        if not conditions:
            return {
                "error": (
                    "Weather API returned forecast entries "
                    "without weather condition labels."
                )
            }

        # Most frequently occurring condition during the day.
        dominant_condition_raw = (
            Counter(conditions)
            .most_common(1)[0][0]
        )

        avg_temperature = round(
            sum(temperatures)
            / len(temperatures),
            1,
        )

        avg_humidity = round(
            sum(humidities)
            / len(humidities),
            1,
        )

        rainfall_total = round(
            rainfall_total,
            1,
        )

        # -------------------------------------------------
        # Normalize weather vocabulary
        # -------------------------------------------------

        mapped_condition = (
            map_owm_condition_to_trained(
                owm_main=dominant_condition_raw,
                temperature=avg_temperature,
                rainfall=rainfall_total,
            )
        )

        # -------------------------------------------------
        # Structured result
        # -------------------------------------------------

        return {
            "region": region,
            "city_used": city,
            "date": target_date,

            "temperature": avg_temperature,

            "rainfall": rainfall_total,

            "humidity": avg_humidity,

            # Safe vocabulary for ForecastService
            "weather_condition": (
                mapped_condition
            ),

            # Keep raw value for transparency/debugging.
            "raw_openweather_condition": (
                dominant_condition_raw
            ),

            "source": "OpenWeatherMap",
        }


# ---------------------------------------------------------
# Singleton service accessor
# ---------------------------------------------------------

_weather_service_instance: Optional[
    WeatherService
] = None


def get_weather_service() -> WeatherService:
    """
    Return one shared WeatherService instance.
    """

    global _weather_service_instance

    if _weather_service_instance is None:
        _weather_service_instance = (
            WeatherService()
        )

    return _weather_service_instance
