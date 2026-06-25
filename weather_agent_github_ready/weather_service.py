"""
Weather data layer: fetches from OpenWeatherMap, normalizes the payload,
and runs a small rule-based decision engine over the result.

No API key is stored in this file. The key is supplied by the caller
(the UI's sidebar field, or an environment variable for the CLI).
"""

import requests
from datetime import datetime

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_weather(city: str, api_key: str):
    """
    Calls the OpenWeatherMap API for a given city.
    Returns (data, error_message). On success error_message is None.
    On failure data is None and error_message describes what went wrong.
    """
    city = (city or "").strip()
    if not city:
        return None, "Enter a city name."
    if not (api_key or "").strip():
        return None, "Add an OpenWeatherMap API key first."

    params = {"q": city, "appid": api_key.strip(), "units": "metric", "lang": "en"}

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
    except requests.exceptions.ConnectionError:
        return None, "No network connection to the weather service."
    except requests.exceptions.Timeout:
        return None, "The weather service timed out. Try again."
    except requests.exceptions.RequestException as exc:
        return None, f"Request failed: {exc}"

    if response.status_code == 404:
        return None, f"\u201c{city}\u201d wasn\u2019t found. Check the spelling."
    if response.status_code == 401:
        return None, "That API key was rejected. Check it and try again."
    if not response.ok:
        return None, f"Weather service returned an error ({response.status_code})."

    return response.json(), None


def process_weather_data(raw: dict) -> dict:
    """Extracts and normalizes the fields the app actually needs."""
    return {
        "city": f"{raw['name']}, {raw['sys']['country']}",
        "temperature": round(raw["main"]["temp"], 1),
        "feels_like": round(raw["main"]["feels_like"], 1),
        "condition": raw["weather"][0]["main"],
        "description": raw["weather"][0]["description"].capitalize(),
        "wind_speed": round(raw["wind"]["speed"], 1),
        "humidity": raw["main"]["humidity"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def decision_engine(weather: dict) -> dict:
    """
    Rule-based evaluation of current conditions. Produces a readable trace
    (used to render the agent's reasoning) rather than a flat tag list.
    """
    temp = weather["temperature"]
    condition = weather["condition"]
    wind = weather["wind_speed"]
    humidity = weather["humidity"]

    is_rainy = condition in ("Rain", "Drizzle", "Thunderstorm")
    is_snowy = condition == "Snow"
    is_cold = temp < 5
    is_hot = temp > 30
    is_mild = 15 <= temp <= 25
    is_windy = wind > 8
    is_humid = humidity > 80

    outdoor_suitable = True
    trace = []

    if is_rainy:
        outdoor_suitable = False
        trace.append({"tag": "PRECIPITATION", "level": "warning",
                       "message": "Rain detected \u2014 indoor activities are favored."})
    if is_snowy:
        outdoor_suitable = False
        trace.append({"tag": "SNOW", "level": "warning",
                       "message": "Snow on the ground \u2014 outdoor movement needs care."})
    if is_cold:
        outdoor_suitable = False
        trace.append({"tag": "LOW_TEMP", "level": "warning",
                       "message": f"{temp}\u00b0C is below the 5\u00b0C outdoor threshold."})
    if is_hot:
        trace.append({"tag": "HIGH_TEMP", "level": "caution",
                       "message": f"{temp}\u00b0C \u2014 favor shaded or cooler hours."})
    if is_windy:
        trace.append({"tag": "HIGH_WIND", "level": "caution",
                       "message": f"Wind at {wind} m/s \u2014 sport activities are deprioritized."})
    if is_mild and not is_rainy and not is_windy:
        outdoor_suitable = True
        trace.append({"tag": "MILD_RANGE", "level": "ok",
                       "message": f"{temp}\u00b0C falls in the ideal 15\u201325\u00b0C outdoor range."})
    if is_humid:
        trace.append({"tag": "HIGH_HUMIDITY", "level": "caution",
                       "message": f"Humidity at {humidity}% \u2014 stay hydrated."})

    if not trace:
        trace.append({"tag": "BASELINE", "level": "ok",
                       "message": "No constraining conditions detected."})

    return {
        "outdoor_suitable": outdoor_suitable,
        "trace": trace,
        "conditions_summary": {
            "is_rainy": is_rainy, "is_snowy": is_snowy,
            "is_cold": is_cold, "is_hot": is_hot,
            "is_mild": is_mild, "is_windy": is_windy,
        },
    }