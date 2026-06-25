"""
Standalone terminal entry point for the agent — same pipeline the
Streamlit app uses, run from the command line.

The API key is never hardcoded: it's read from the OPENWEATHER_API_KEY
environment variable, or typed in at the prompt if that's not set.
"""

import os

from weather_service import fetch_weather, process_weather_data, decision_engine
from recommendation_engine import generate_smart_recommendations, score_label
from evaluator import evaluate_recommendations


def run_agent(city: str, api_key: str, category: str = "Outdoor Sports") -> dict:
    print(f"\n{'=' * 50}")
    print(f"  WEATHER AGENT — {city.upper()}")
    print(f"{'=' * 50}")

    print("\n[1/4] Fetching weather data…")
    raw, error = fetch_weather(city, api_key)
    if error:
        print(f"[ERROR] {error}")
        return {"error": error}

    print("[2/4] Normalizing data…")
    weather = process_weather_data(raw)

    print("[3/4] Running decision engine…")
    decisions = decision_engine(weather)

    print("[4/4] Generating recommendations…")
    score, recommendations, effective_label = generate_smart_recommendations(weather, category)
    match_score = evaluate_recommendations(weather, recommendations)

    print(f"\nLocation     : {weather['city']}")
    print(f"Temperature  : {weather['temperature']}°C (feels like {weather['feels_like']}°C)")
    print(f"Condition    : {weather['condition']} ({weather['description']})")
    print(f"Wind         : {weather['wind_speed']} m/s")
    print(f"Humidity     : {weather['humidity']}%")

    print(f"\nAgent trace:")
    for entry in decisions["trace"]:
        print(f"   [{entry['level'].upper():7}] {entry['tag']}: {entry['message']}")

    print(f"\nWeather score: {score}% ({score_label(score)})")
    print(f"Match score  : {match_score}%")

    print(f"\nRecommended activities ({effective_label}):")
    for act in recommendations:
        print(f"   {act['icon']} {act['name']}: {act['desc']}")

    return {
        "weather": weather,
        "decisions": decisions,
        "weather_score": score,
        "match_score": match_score,
        "recommendations": recommendations,
    }


if __name__ == "__main__":
    key = os.environ.get("OPENWEATHER_API_KEY", "").strip()
    if not key:
        key = input("Enter your OpenWeatherMap API key: ").strip()

    city_input = input("Enter a city (e.g. Istanbul): ").strip() or "Istanbul"
    run_agent(city_input, key)