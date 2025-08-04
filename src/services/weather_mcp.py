from mcp.server.fastmcp import FastMCP
from mcp.server.auth.provider import TokenVerifier
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
import os
import logging
import json
from pathlib import Path
from ..lib.auth import verify_token
import httpx
from typing import Any, Dict

DOMAIN = os.getenv("domain")
NWS_API_BASE = "https://api.weather.gov"
CITY_DATA = Path(__file__).parents[1] / "static" / "city_coords.json"

logger = logging.getLogger(__name__)
city_coords = json.loads(CITY_DATA.read_text())
tmp_names = list(city.rsplit(", ")[0] for city in city_coords.keys())
city_names = set(tmp_names)
unique_names = set(name for name in city_names if tmp_names.count(name) == 1)


class APIKeyValidation(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            payload = verify_token(token)
        except AssertionError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None

        return AccessToken(
            token=token,
            client_id=payload["sub"],
            scopes=payload.get("scope").split(),
        )


weather_mcp = FastMCP(
    "Weather MCP",
    token_verifier=APIKeyValidation(),
    auth=AuthSettings(
        issuer_url=f"https://{DOMAIN}",
        resource_server_url=f"https://{DOMAIN}/mcp",
        required_scopes=["mcp:full_access"],
    ),
)


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": "weather-app/1.0",
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


@weather_mcp.tool()
async def get_forcast(city_string: str) -> Dict[str, Any]:
    """Get the weather forecast for a city.

    Args:
        city: City name (can include state for disambiguation, e.g. "New York, NY")
    """

    if ", " not in city_string and city_string not in unique_names:
        return f"The city is not unique within the US. Please add the state for disambiguation."
    elif city_string in unique_names:
        city_string = [key for key in city_coords.keys() if key.startswith(city_string)][0]

    city, state = city_string.rsplit(", ", 1)
    if city not in city_names:
        return f"City '{city}' not found. Is this city in the US?"
 
    # Get the weather forecast
    latitude, longitude, state_code = city_coords[city_string].values()
    logger.info(f"Fetching weather for {city_string} at {latitude}, {longitude} in {state_code}")
        
    points_data = await make_nws_request(f"{NWS_API_BASE}/points/{latitude},{longitude}")
    forecast_data = await make_nws_request(points_data["properties"]["forecast"])
    period = forecast_data["properties"]["periods"][0]
    forecast = {
        "temperature": str(period["temperature"])+"°"+period["temperatureUnit"],
        "wind": period["windSpeed"]+" "+period["windDirection"],
        "forecast": period["detailedForecast"]
    }
    
    alerts_data = await make_nws_request(f"{NWS_API_BASE}/alerts/active/area/{state_code}")
    if alerts_data and "features" in alerts_data and alerts_data["features"]:
        alerts = [{
            "event": feature["properties"].get('event', 'Unknown'),
            "area": feature["properties"].get('areaDesc', 'Unknown'),
            "severity": feature["properties"].get('severity', 'Unknown'),
            "description": feature["properties"].get('description', 'No description available'),
            "instructions": feature["properties"].get('instruction', 'No specific instructions provided')
        } for feature in alerts_data["features"]]
        forecast["alerts"] = alerts

    return forecast
