"""
Activity catalog with the real-world conditions each one actually needs.

Indoor and Culture entries have no weather constraints — they work
regardless of conditions, by nature. Outdoor entries are matched against
the live weather (temperature, wind, condition) before they are ever
suggested, so "go for a run" never gets recommended during a thunderstorm
just because some unrelated score happened to land in a certain band.

desc_template fields come from the weather dict produced by
weather_service.process_weather_data() — temperature, wind_speed,
humidity, description — plus "description" is lowercased before
formatting so it reads naturally mid-sentence.
"""

ACTIVITIES = [
    # ---------------- Outdoor (weather-gated) ----------------
    {
        "name": "Running", "icon": "🏃", "category": "Outdoor",
        "min_temp": 2, "max_temp": 27, "max_wind": 9,
        "avoid_conditions": ["Rain", "Drizzle", "Thunderstorm", "Snow"],
        "desc_template": "{temperature}°C with {wind_speed} m/s wind — solid footing for a run.",
    },
    {
        "name": "Cycling", "icon": "🚴", "category": "Outdoor",
        "min_temp": 5, "max_temp": 30, "max_wind": 7,
        "avoid_conditions": ["Rain", "Drizzle", "Thunderstorm", "Snow"],
        "desc_template": "{wind_speed} m/s wind keeps a bike steady — a clean {temperature}°C ride.",
    },
    {
        "name": "Hiking", "icon": "🥾", "category": "Outdoor",
        "min_temp": 0, "max_temp": 28, "max_wind": 12,
        "avoid_conditions": ["Rain", "Drizzle", "Thunderstorm", "Snow"],
        "desc_template": "{description}, {temperature}°C — good visibility on the trail.",
    },
    {
        "name": "Picnic", "icon": "🧺", "category": "Outdoor",
        "min_temp": 16, "max_temp": 29, "max_wind": 6,
        "avoid_conditions": ["Rain", "Drizzle", "Thunderstorm", "Snow"],
        "desc_template": "{temperature}°C and calm air — comfortable enough to sit outside and eat.",
    },
    {
        "name": "Photography", "icon": "📸", "category": "Outdoor",
        "min_temp": -10, "max_temp": 36, "max_wind": 14,
        "avoid_conditions": ["Thunderstorm"],
        "desc_template": "{description} at {temperature}°C — worth shooting outdoors.",
    },
    {
        "name": "Swimming", "icon": "🏊", "category": "Outdoor",
        "min_temp": 24, "max_temp": 42, "max_wind": 99,
        "avoid_conditions": ["Rain", "Drizzle", "Thunderstorm", "Snow"],
        "desc_template": "{temperature}°C is warm enough to actually cool off in the water.",
    },
    {
        "name": "Beach Walk", "icon": "🏖️", "category": "Outdoor",
        "min_temp": 20, "max_temp": 40, "max_wind": 10,
        "avoid_conditions": ["Rain", "Drizzle", "Thunderstorm", "Snow"],
        "desc_template": "{temperature}°C — pleasant enough for a shoreline walk.",
    },

    # ---------------- Culture (weather-independent) ----------------
    {"name": "Museum Visit", "icon": "🏛️", "category": "Culture",
     "desc_template": "An unhurried walk through a museum, regardless of the weather."},
    {"name": "Art Gallery", "icon": "🎨", "category": "Culture",
     "desc_template": "Quiet and climate-controlled — always a safe pick."},
    {"name": "Theater", "icon": "🎭", "category": "Culture",
     "desc_template": "A scheduled performance makes good use of the evening."},
    {"name": "Bookstore", "icon": "📚", "category": "Culture",
     "desc_template": "Slow browsing, no weather dependency at all."},

    # ---------------- Indoor (weather-independent) ----------------
    {"name": "Gym", "icon": "🏋️", "category": "Indoor",
     "desc_template": "A reliable session, independent of the forecast."},
    {"name": "Movie", "icon": "🎬", "category": "Indoor",
     "desc_template": "Good cover for whenever you'd rather not be outside."},
    {"name": "Reading", "icon": "📖", "category": "Indoor",
     "desc_template": "A still afternoon suited to focused reading."},
    {"name": "Cooking", "icon": "👨‍🍳", "category": "Indoor",
     "desc_template": "Time to try a recipe that needs attention."},
    {"name": "Gaming", "icon": "🎮", "category": "Indoor",
     "desc_template": "A straightforward indoor option for the day."},
    {"name": "Yoga", "icon": "🧘", "category": "Indoor",
     "desc_template": "Low-impact and calm — works in any weather."},
]