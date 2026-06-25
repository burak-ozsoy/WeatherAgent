"""
Filters the activity catalog against the live weather before suggesting
anything. An activity only appears if it's actually realistic to do right
now — temperature, wind, and condition are all checked per activity,
instead of sampling from a static bucket that only loosely tracked an
overall score band.
"""

import random

from activities import ACTIVITIES
from suitability import activity_fits_weather


def calculate_weather_score(weather: dict) -> int:
    score = 100
    if weather["condition"] in ("Rain", "Drizzle", "Thunderstorm"):
        score -= 40
    if weather["condition"] == "Snow":
        score -= 25
    if weather["wind_speed"] > 8:
        score -= 20
    if weather["temperature"] > 30:
        score -= 15
    if weather["temperature"] < 5:
        score -= 15
    if weather["humidity"] > 85:
        score -= 10
    return max(score, 0)


def score_label(score: int) -> str:
    if score < 40:
        return "Poor"
    if score < 70:
        return "Fair"
    return "Good"


def _eligible(category: str, weather: dict) -> list:
    return [a for a in ACTIVITIES if a["category"] == category and activity_fits_weather(a, weather)]


def _render(activity: dict, weather: dict) -> dict:
    fmt = {**weather, "description": weather["description"].lower()}
    return {
        "name": activity["name"],
        "icon": activity["icon"],
        "desc": activity["desc_template"].format(**fmt),
    }


def generate_smart_recommendations(weather: dict, user_type: str):
    """
    Returns (weather_score, recommendations, effective_label).

    user_type is one of "Outdoor Sports", "Culture", "Indoor" — matching
    the selectbox in the UI. The catalog tags activities "Outdoor",
    "Culture", or "Indoor", so the UI label is mapped onto that.

    effective_label reflects what's actually being shown: if the person
    picked Outdoor Sports but conditions rule almost all of it out, the
    label says so instead of silently swapping in indoor picks under the
    original heading.
    """
    score = calculate_weather_score(weather)
    category = "Outdoor" if user_type == "Outdoor Sports" else user_type
    TARGET = 5

    if category == "Outdoor":
        outdoor_pool = _eligible("Outdoor", weather)
        random.shuffle(outdoor_pool)
        pool = list(outdoor_pool)

        if len(pool) < TARGET:
            backfill = _eligible("Indoor", weather) + _eligible("Culture", weather)
            random.shuffle(backfill)
            pool = pool + backfill[: TARGET - len(pool)]

        if not outdoor_pool:
            effective_label = "Indoor & Culture (weather ruled out outdoor today)"
        elif len(outdoor_pool) < len(pool):
            effective_label = "Outdoor Sports + a few weather-safe backups"
        else:
            effective_label = "Outdoor Sports"

    else:
        pool = _eligible(category, weather)
        effective_label = user_type
        if score >= 70:
            # Great weather — toss in a couple of outdoor options as a bonus,
            # but only ones that genuinely fit right now.
            bonus = _eligible("Outdoor", weather)
            random.shuffle(bonus)
            if bonus:
                pool = pool + bonus[:2]
                effective_label = f"{user_type} + outdoor bonus picks"

    random.shuffle(pool)
    chosen = pool[:TARGET]
    recommendations = [_render(a, weather) for a in chosen]

    return score, recommendations, effective_label