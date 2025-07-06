from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import logging

# Initialize FastMCP server
mcp = FastMCP("weathermcp")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Constants
OPENMETEO_API_BASE = "https://api.open-meteo.com/v1"
USER_AGENT = "weather-app/1.0"

# Helper function to make a request to the Open-Meteo API with proper error handling and logging
async def make_openmeteo_request(url: str) -> dict[str, Any] | None:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    logging.info(f"[make_openmeteo_request] URL: {url}")
    logging.debug(f"[make_openmeteo_request] Headers: {headers}")
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            logging.info(f"[make_openmeteo_request] Response status: {response.status_code}")
            logging.debug(f"[make_openmeteo_request] Response text: {response.text}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logging.error(f"[make_openmeteo_request] HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logging.error(f"[make_openmeteo_request] Exception: {e}")
            return None

@mcp.tool()
async def get_current_weather(latitude: float, longitude: float) -> str:
    """Get current weather for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """

    logging.info(f"get_current_weather called with latitude={latitude}, longitude={longitude}")
    url = (
        f"{OPENMETEO_API_BASE}/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&current=temperature_2m,is_day,showers,cloud_cover,wind_speed_10m,"
        f"wind_direction_10m,pressure_msl,snowfall,precipitation,"
        f"relative_humidity_2m,apparent_temperature,rain,weather_code,"
        f"surface_pressure,wind_gusts_10m"
    )
    logging.info(f"Requesting weather data from URL: {url}")
    data = await make_openmeteo_request(url)

    if not data or "current" not in data:
        logging.error("Unable to fetch current weather data for this location.")
        return "Unable to fetch current weather data for this location."

    current = data["current"]
    summary = (
        f"Temperature: {current.get('temperature_2m', 'N/A')}°C\n"
        f"Feels Like: {current.get('apparent_temperature', 'N/A')}°C\n"
        f"Humidity: {current.get('relative_humidity_2m', 'N/A')}%\n"
        f"Cloud Cover: {current.get('cloud_cover', 'N/A')}%\n"
        f"Wind: {current.get('wind_speed_10m', 'N/A')} km/h "
        f"from {current.get('wind_direction_10m', 'N/A')}°\n"
        f"Rain: {current.get('rain', 'N/A')} mm\n"
        f"Pressure: {current.get('surface_pressure', 'N/A')} hPa"
    )
    logging.info(f"Weather summary: {summary}")
    return summary

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')

