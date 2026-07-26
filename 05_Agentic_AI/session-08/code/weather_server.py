import os
from openai import base_url
import requests
import logging
from mcp.server.fastmcp import FastMCP

OPENWEATHERMAP_API_KEY = ""

mcp = FastMCP("WeatherAssistant")

@mcp.tool()
def get_weather(locations: str) -> dict:
        """
        Fetches the current weather for a specified location using the OpenWeatherMap API.

        Args:
            location: The city name and optional country code (e.g., "London,uk").

        Returns:
            A dictionary containing weather information or an error message.
        """
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": locations,
            "appid": OPENWEATHERMAP_API_KEY,
            "units": "metric"
        }
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
            # extracting relevent weather informntions
            weather_description = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]

            return {
                "location": data["name"],
                "weather": weather_description,
                "temperature_celsius": f"{temperature}°C",
                "feels_like_celsius": f"{feels_like}°C",
                "humidity": f"{humidity}%",
                "wind_speed_mps": f"{wind_speed} m/s"
            }
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching weather data: {e}")
            return {"error": "Unable to fetch weather data. Please try again later."}
        

@mcp.tool()
def get_forecast(location: str, days: int = 3) -> dict:
    """
    Fetches a multi-day weather forecast for a specified location.

    Args:
        location: The city name and optional country code (e.g., "Mumbai,in").
        days: Number of days to forecast (1-5, default 3).

    Returns:
        A dictionary with a list of forecast entries or an error message.
    """
    days = max(1, min(days, 5))
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {"q": location, "appid": OPENWEATHERMAP_API_KEY, "units": "metric"}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        # OWM returns data in 3-hour steps; take the midday entry for each requested day
        daily = []
        seen_dates = set()
        for entry in data["list"]:
            date_str = entry["dt_txt"].split(" ")[0]
            time_str = entry["dt_txt"].split(" ")[1]
            if date_str not in seen_dates and time_str == "12:00:00":
                seen_dates.add(date_str)
                daily.append({
                    "date": date_str,
                    "temperature_celsius": f"{entry['main']['temp']}°C",
                    "weather": entry["weather"][0]["description"]
                })
            if len(daily) >= days:
                break

        return {"location": data["city"]["name"], "forecast": daily}
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            return {"error": f"Could not find forecast data for '{location}'."}
        return {"error": f"An HTTP error occurred: {http_err}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

@mcp.tool()
def news_today():
    return "Today's news: Global markets are showing signs of recovery, with tech stocks leading the way. In other news, a major breakthrough in renewable energy technology has been announced, promising a greener future."


@mcp.prompt()
def compare_weather_prompt(location_a: str, location_b: str) -> str:
    """
    Generates a clear, comparative summary of the weather between two specified locations.
    This is the best choice when a user asks to compare, contrast, or see the difference in weather between two places.
    
    Args:
        location_a: The first city for comparison (e.g., "London").
        location_b: The second city for comparison (e.g., "Paris").
    """
    return f"""
    You are acting as a helpful weather analyst. Your goal is to provide a clear and easy-to-read comparison of the weather in two different locations for a user.

    The user wants to compare the weather between "{location_a}" and "{location_b}".

    To accomplish this, follow these steps:
    1.  First, gather the necessary weather data for both "{location_a}" and "{location_b}".
    2.  Once you have the weather data for both locations, DO NOT simply list the raw results.
    3.  Instead, synthesize the information into a concise summary. Your final response should highlight the key differences, focusing on temperature, the general conditions (e.g., 'sunny' vs 'rainy'), and wind speed.
    4.  Present the comparison in a structured format, like a markdown table or a clear bulleted list, to make it easy for the user to understand at a glance.
    """



if __name__ == "__main__":
    mcp.run(transport="stdio")