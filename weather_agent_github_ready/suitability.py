"""
Single source of truth for whether an activity actually fits the live
weather. Used by both the recommendation engine (to decide what to
suggest) and the evaluator (to independently re-check the result) — so
the two can never quietly disagree about what counts as a sensible match.
"""


def activity_fits_weather(activity: dict, weather: dict) -> bool:
    if activity["category"] != "Outdoor":
        return True  # Indoor / Culture picks are weather-independent by design

    condition = weather["condition"]
    temp = weather["temperature"]
    wind = weather["wind_speed"]

    if condition in activity.get("avoid_conditions", []):
        return False
    if not (activity["min_temp"] <= temp <= activity["max_temp"]):
        return False
    if wind > activity.get("max_wind", 999):
        return False
    return True