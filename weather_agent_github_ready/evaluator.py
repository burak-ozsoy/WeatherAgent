"""
Independently checks whether the recommendations that came back are
actually sensible for the current weather. Re-derives suitability from
the same rules the engine uses (shared via suitability.py), rather than
trusting the engine's own output or a separate hardcoded name list.
"""

from activities import ACTIVITIES
from suitability import activity_fits_weather

_BY_NAME = {a["name"]: a for a in ACTIVITIES}


def evaluate_recommendations(weather: dict, recommendations: list) -> float:
    if not recommendations:
        return 0.0

    matches = 0
    for item in recommendations:
        activity = _BY_NAME.get(item["name"])
        if activity is None or activity_fits_weather(activity, weather):
            matches += 1

    return round(matches / len(recommendations) * 100, 2)