import streamlit as st

from weather_service import fetch_weather, process_weather_data, decision_engine
from recommendation_engine import generate_smart_recommendations, score_label
from evaluator import evaluate_recommendations

# ============================================================
# Page configuration
# ============================================================
st.set_page_config(
    page_title="Weather Activity Agent",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# Condition -> visual theme mapping
# ============================================================
CONDITION_THEME = {
    "Clear":        {"accent": "#C97A2B", "icon": "☀"},
    "Clouds":       {"accent": "#5C6B78", "icon": "☁"},
    "Rain":         {"accent": "#1F5C6B", "icon": "☂"},
    "Drizzle":      {"accent": "#1F5C6B", "icon": "☂"},
    "Thunderstorm": {"accent": "#4B3F5E", "icon": "⛈"},
    "Snow":         {"accent": "#4C90A3", "icon": "❄"},
    "Mist":         {"accent": "#8B97A3", "icon": "○"},
    "Fog":          {"accent": "#8B97A3", "icon": "○"},
    "Haze":         {"accent": "#8B97A3", "icon": "○"},
}
DEFAULT_THEME = {"accent": "#1F5C6B", "icon": "○"}
LEVEL_COLOR = {"warning": "#B5562B", "caution": "#B68A2E", "ok": "#3F7A5E"}


def get_condition_theme(condition: str) -> dict:
    return CONDITION_THEME.get(condition, DEFAULT_THEME)


def get_score_color(score: int) -> str:
    if score < 40:
        return "#B5562B"
    if score < 70:
        return "#B68A2E"
    return "#3F7A5E"


def md(html: str) -> None:
    """Render a flat (single-line, no stray indentation) HTML string.

    Streamlit's markdown renderer treats a line that is indented by four or
    more spaces as a code block. Building HTML with Python's normal nested
    indentation can accidentally produce such lines (especially right after
    an inserted multi-line fragment), which prints the tags as literal text
    instead of rendering them. Routing everything through this helper keeps
    every fragment on one physical line, which sidesteps that entirely.
    """
    st.markdown(" ".join(html.split()), unsafe_allow_html=True)


# ============================================================
# Fonts + stylesheet
# ============================================================
st.markdown(
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>

    :root{
        --ink:#12161C;
        --ink-soft:#262C34;
        --paper:#F1F4F6;
        --paper-raised:#FFFFFF;
        --slate:#57626E;
        --slate-light:#8B97A3;
        --hairline:#D7DEE3;
        --petrol:#1F5C6B;
        --warn:#B5562B;
        --caution:#B68A2E;
        --ok:#3F7A5E;
    }

    html, body, [class*="css"]{
        font-family:'Inter',sans-serif;
    }

    #MainMenu{visibility:hidden;}
    footer{visibility:hidden;}
    [data-testid="collapsedControl"]{display:block !important;}

    /* Streamlit's own top bar (hamburger / Deploy button) floats over the
       page with a transparent background by default, which is what was
       overlapping the masthead text. Giving it a solid, matching
       background plus a touch of top padding on the content below fixes
       the overlap instead of fighting Streamlit's layout. */
    header[data-testid="stHeader"]{
        background:var(--paper);
    }

    .stApp{ background:var(--paper); }
    .block-container{ max-width:1180px; padding-top:3.2rem; padding-bottom:3rem; }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"]{
        width:280px !important;
        background:var(--ink);
        border-right:1px solid var(--hairline);
    }
    section[data-testid="stSidebar"] *{ color:#E7EAED; }
    section[data-testid="stSidebar"] .side-eyebrow{
        font-family:'IBM Plex Mono',monospace;
        font-size:11px; letter-spacing:.12em; text-transform:uppercase;
        color:#8FA0AC; margin-bottom:2px;
    }
    section[data-testid="stSidebar"] .side-title{
        font-family:'Fraunces',serif; font-weight:600; font-size:22px;
        color:#FFFFFF; margin-bottom:14px;
    }
    section[data-testid="stSidebar"] .side-text{
        font-size:13.5px; line-height:1.55; color:#B7C0C8; margin-bottom:14px;
    }
    section[data-testid="stSidebar"] .side-note{
        font-size:12px; line-height:1.5; color:#8FA0AC; margin-top:8px;
    }
    section[data-testid="stSidebar"] .side-note a{ color:#7FB6C7; }
    section[data-testid="stSidebar"] hr{ border-color:rgba(255,255,255,.12); margin:16px 0; }
    .pipeline-row{
        display:flex; align-items:baseline; gap:10px; margin-bottom:9px;
        font-family:'IBM Plex Mono',monospace; font-size:12.5px; color:#C7CFD6;
    }
    .pipeline-row .pn{ color:#5B96A8; font-weight:600; }
    section[data-testid="stSidebar"] [data-testid="stTextInput"] input{
        background:#1B2129; border:1px solid rgba(255,255,255,.18); color:#F2F4F6 !important;
        border-radius:8px; font-family:'IBM Plex Mono',monospace; font-size:13px;
    }
    section[data-testid="stSidebar"] [data-testid="stTextInput"] input::placeholder{
        color:#7E8C97 !important; opacity:1;
    }
    section[data-testid="stSidebar"] label{ font-size:12.5px !important; color:#9FACB6 !important; }

    /* ---------- Masthead ---------- */
    .eyebrow{
        font-family:'IBM Plex Mono',monospace; font-size:12px; letter-spacing:.14em;
        text-transform:uppercase; color:var(--petrol); margin-bottom:6px;
    }
    .editorial-title{
        font-family:'Fraunces',serif; font-weight:600; font-size:42px;
        color:var(--ink); margin:0; line-height:1.08;
    }
    .editorial-sub{
        font-size:15.5px; color:var(--slate); margin-top:8px; margin-bottom:22px;
    }
    .hairline{ border:none; border-top:1px solid var(--hairline); margin:0 0 26px 0; }

    /* ---------- Console / search bar ---------- */
    .console-label{
        font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.1em;
        text-transform:uppercase; color:var(--slate-light); margin-bottom:6px;
    }
    div[data-testid="stTextInput"] input{
        border-radius:9px; border:1px solid var(--hairline); background:var(--paper-raised);
        font-size:14.5px;
    }
    div[data-testid="stTextInput"] input:focus{ border-color:var(--petrol); box-shadow:0 0 0 1px var(--petrol); }
    div[data-testid="stSelectbox"] > div{ border-radius:9px; }
    div[data-testid="stButton"] button{
        background:var(--ink); color:#fff; border:none; border-radius:9px;
        font-weight:600; font-size:14px; padding:0.55rem 0; transition:.15s; width:100%;
    }
    div[data-testid="stButton"] button:hover{ background:var(--petrol); color:#fff; }

    /* Empty-label widgets still reserve a small label row in some Streamlit
       versions; collapse it instead of relying on the label_visibility
       parameter, which isn't available on older Streamlit releases. */
    div[data-testid="stTextInput"] label,
    div[data-testid="stSelectbox"] label{
        display:none;
        height:0;
        margin:0;
        padding:0;
    }

    /* ---------- Empty / error state ---------- */
    .state-card{
        background:var(--paper-raised); border:1px solid var(--hairline); border-radius:14px;
        padding:28px 30px; margin-top:6px;
    }
    .state-card.error{ border-left:4px solid var(--warn); }
    .state-title{ font-family:'Fraunces',serif; font-size:19px; font-weight:600; color:var(--ink); margin-bottom:6px; }
    .state-text{ font-size:14px; color:var(--slate); line-height:1.6; }

    /* ---------- Readout panel ---------- */
    .readout-card{
        background:var(--ink); border-radius:16px; padding:0; overflow:hidden;
        box-shadow:0 10px 28px rgba(18,22,28,.18);
    }
    .readout-accent{ height:4px; width:100%; }
    .readout-body{ padding:24px 26px 22px 26px; }
    .readout-eyebrow{
        font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.12em;
        text-transform:uppercase; color:#7E8E99; margin-bottom:4px;
    }
    .readout-city{ font-family:'Fraunces',serif; font-size:21px; color:#F2F4F6; font-weight:500; }
    .readout-temp{
        font-family:'IBM Plex Mono',monospace; font-weight:600; font-size:68px;
        color:#FFFFFF; line-height:1; margin:14px 0 2px 0;
    }
    .readout-condition{ font-size:15.5px; color:#D6DCE1; }
    .readout-desc{ font-size:13px; color:#8FA0AC; margin-top:2px; }
    .readout-divider{ border:none; border-top:1px solid rgba(255,255,255,.12); margin:20px 0 16px 0; }
    .readout-stats{ display:flex; gap:22px; }
    .stat-block{ flex:1; }
    .stat-label{
        font-family:'IBM Plex Mono',monospace; font-size:10.5px; letter-spacing:.1em;
        text-transform:uppercase; color:#7E8E99; margin-bottom:4px;
    }
    .stat-value{ font-family:'IBM Plex Mono',monospace; font-size:18px; color:#F2F4F6; font-weight:600; }
    .readout-timestamp{
        font-family:'IBM Plex Mono',monospace; font-size:11px; color:#5F6F7A; margin-top:18px;
    }

    /* ---------- Trace panel ---------- */
    .trace-card{
        background:var(--paper-raised); border:1px solid var(--hairline); border-radius:16px;
        padding:22px 24px; height:100%;
    }
    .trace-eyebrow{
        font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.12em;
        text-transform:uppercase; color:var(--slate-light); margin-bottom:2px;
    }
    .trace-title{ font-family:'Fraunces',serif; font-size:19px; color:var(--ink); font-weight:600; margin-bottom:14px; }
    .trace-row{ display:flex; align-items:flex-start; gap:10px; margin-bottom:11px; }
    .trace-dot{ width:7px; height:7px; border-radius:50%; margin-top:6px; flex-shrink:0; }
    .trace-tag{
        font-family:'IBM Plex Mono',monospace; font-size:11px; font-weight:600;
        color:var(--ink-soft); white-space:nowrap; padding-top:1px;
    }
    .trace-message{ font-size:13px; color:var(--slate); line-height:1.5; }
    .trace-divider{ border:none; border-top:1px solid var(--hairline); margin:18px 0 16px 0; }

    /* ---------- Gauges ---------- */
    .gauge{ margin-bottom:14px; }
    .gauge-top{ display:flex; justify-content:space-between; align-items:baseline; margin-bottom:6px; }
    .gauge-label{
        font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.08em;
        text-transform:uppercase; color:var(--slate);
    }
    .gauge-value{ font-family:'IBM Plex Mono',monospace; font-size:13px; font-weight:600; color:var(--ink); }
    .gauge-track{ height:6px; background:var(--hairline); border-radius:4px; overflow:hidden; }
    .gauge-fill{ height:100%; border-radius:4px; }

    /* ---------- Results header ---------- */
    .results-eyebrow{
        font-family:'IBM Plex Mono',monospace; font-size:12px; letter-spacing:.1em;
        text-transform:uppercase; color:var(--petrol); margin-top:34px; margin-bottom:4px;
    }
    .results-title{ font-family:'Fraunces',serif; font-size:26px; font-weight:600; color:var(--ink); margin-bottom:18px; }

    /* ---------- Activity cards ---------- */
    .activity-card{
        background:var(--paper-raised); border:1px solid var(--hairline); border-radius:14px;
        padding:18px 18px 16px 18px; margin-bottom:16px; transition:.15s; height:148px;
        display:flex; flex-direction:column;
    }
    .activity-card:hover{ transform:translateY(-2px); box-shadow:0 8px 18px rgba(18,22,28,.08); border-color:var(--petrol); }
    .activity-index{
        font-family:'IBM Plex Mono',monospace; font-size:11px; color:var(--slate-light); margin-bottom:8px;
    }
    .activity-name{ font-family:'Fraunces',serif; font-size:16.5px; font-weight:600; color:var(--ink); margin-bottom:6px; }
    .activity-desc{ font-size:12.5px; color:var(--slate); line-height:1.5; }

    /* ---------- Expander ---------- */
    .streamlit-expanderHeader{ font-weight:600; font-size:13.5px; }

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    md('<div class="side-eyebrow">Course Project</div>')
    md('<div class="side-title">Weather Agent</div>')
    md(
        '<div class="side-text">Reads live conditions for a city and runs them through a '
        "rule-based decision engine before sampling activity recommendations matched to "
        "the current weather.</div>"
    )
    st.markdown("---")
    md('<div class="side-eyebrow">Pipeline</div>')
    pipeline_steps = ["Fetch weather data", "Normalize fields", "Run decision engine", "Sample recommendations"]
    for i, step in enumerate(pipeline_steps, start=1):
        md(f'<div class="pipeline-row"><span class="pn">{i:02d}</span><span>{step}</span></div>')
    st.markdown("---")
    md('<div class="side-eyebrow">OpenWeatherMap API Key</div>')
    api_key_input = st.text_input(
        "",
        value="",
        type="password",
        placeholder="Paste your API key",
    )
    md(
        '<div class="side-note">No key ships with this app. Get a free one at '
        '<a href="https://openweathermap.org/api" target="_blank">openweathermap.org/api</a> '
        "and paste it above — it's kept only for this session, never written to disk.</div>"
    )
    active_api_key = api_key_input.strip()

# ============================================================
# Masthead
# ============================================================
md('<div class="eyebrow">Field Agent · Weather-Aware Recommendations</div>')
md('<h1 class="editorial-title">Weather Activity Agent</h1>')
md(
    '<p class="editorial-sub">Enter a city to read live conditions and get activity '
    "recommendations matched to the weather.</p>"
)
md('<hr class="hairline">')

# ============================================================
# Search console
# ============================================================
c1, c2, c3 = st.columns([1.1, 2.2, 0.9])

with c1:
    md('<div class="console-label">Category</div>')
    user_type = st.selectbox("", ["Outdoor Sports", "Culture", "Indoor"])

with c2:
    md('<div class="console-label">Location</div>')
    city = st.text_input("", placeholder="e.g. Istanbul")

with c3:
    md('<div class="console-label">&nbsp;</div>')
    analyze_btn = st.button("Analyze Weather")

# ============================================================
# Results
# ============================================================
if analyze_btn and not city.strip():
    md(
        '<div class="state-card error">'
        '<div class="state-title">No city entered</div>'
        '<div class="state-text">Type a city name into the location field, then run the analysis again.</div>'
        "</div>"
    )

elif analyze_btn and not active_api_key:
    md(
        '<div class="state-card error">'
        '<div class="state-title">No API key</div>'
        '<div class="state-text">Paste an OpenWeatherMap API key into the sidebar field first, '
        "then run the analysis again.</div>"
        "</div>"
    )

elif analyze_btn:

    with st.spinner("Reading conditions and scoring recommendations…"):
        raw, error = fetch_weather(city, api_key=active_api_key)

    if error:
        md(
            '<div class="state-card error">'
            '<div class="state-title">Couldn\'t complete the request</div>'
            f'<div class="state-text">{error}</div>'
            "</div>"
        )

    else:
        weather = process_weather_data(raw)
        decisions = decision_engine(weather)
        weather_score, recommendations, effective_label = generate_smart_recommendations(weather, user_type)
        match_score = evaluate_recommendations(weather, recommendations)
        theme = get_condition_theme(weather["condition"])

        left, right = st.columns([1, 1.15])

        # ---- Weather readout ----
        with left:
            stats_html = "".join(
                f'<div class="stat-block"><div class="stat-label">{label}</div>'
                f'<div class="stat-value">{value}</div></div>'
                for label, value in [
                    ("Wind", f"{weather['wind_speed']} m/s"),
                    ("Humidity", f"{weather['humidity']}%"),
                    ("Feels Like", f"{weather['feels_like']}°C"),
                ]
            )
            md(
                '<div class="readout-card">'
                f'<div class="readout-accent" style="background:{theme["accent"]}"></div>'
                '<div class="readout-body">'
                '<div class="readout-eyebrow">Station Readout</div>'
                f'<div class="readout-city">{theme["icon"]} {weather["city"]}</div>'
                f'<div class="readout-temp">{weather["temperature"]}°</div>'
                f'<div class="readout-condition">{weather["condition"]}</div>'
                f'<div class="readout-desc">{weather["description"]}</div>'
                '<hr class="readout-divider">'
                f'<div class="readout-stats">{stats_html}</div>'
                f'<div class="readout-timestamp">Updated {weather["timestamp"]}</div>'
                "</div></div>"
            )

        # ---- Agent trace + gauges ----
        with right:
            trace_html = "".join(
                '<div class="trace-row">'
                f'<span class="trace-dot" style="background:{LEVEL_COLOR.get(entry["level"], "#999")}"></span>'
                f'<span class="trace-tag">{entry["tag"]}</span>'
                f'<span class="trace-message">{entry["message"]}</span>'
                "</div>"
                for entry in decisions["trace"]
            )

            weather_color = get_score_color(weather_score)
            match_color = get_score_color(match_score)

            md(
                '<div class="trace-card">'
                '<div class="trace-eyebrow">Agent Trace</div>'
                '<div class="trace-title">Decision Engine</div>'
                f"{trace_html}"
                '<hr class="trace-divider">'
                '<div class="gauge">'
                '<div class="gauge-top">'
                f'<span class="gauge-label">Weather Score · {score_label(weather_score)}</span>'
                f'<span class="gauge-value">{weather_score}%</span>'
                "</div>"
                '<div class="gauge-track">'
                f'<div class="gauge-fill" style="width:{weather_score}%;background:{weather_color}"></div>'
                "</div></div>"
                '<div class="gauge">'
                '<div class="gauge-top">'
                '<span class="gauge-label">Match Score</span>'
                f'<span class="gauge-value">{match_score}%</span>'
                "</div>"
                '<div class="gauge-track">'
                f'<div class="gauge-fill" style="width:{match_score}%;background:{match_color}"></div>'
                "</div></div>"
                "</div>"
            )

        # ---- Recommendations ----
        md(
            f'<div class="results-eyebrow">{len(recommendations)} Results · {effective_label} · '
            f'{score_label(weather_score)} conditions</div>'
        )
        md('<div class="results-title">Recommended Activities</div>')

        cols = st.columns(min(5, len(recommendations)) or 1)
        for i, activity in enumerate(recommendations):
            with cols[i % len(cols)]:
                md(
                    '<div class="activity-card">'
                    f'<div class="activity-index">{i + 1:02d}</div>'
                    f'<div class="activity-name">{activity["icon"]} {activity["name"]}</div>'
                    f'<div class="activity-desc">{activity["desc"]}</div>'
                    "</div>"
                )

        with st.expander("Technical details"):
            st.json(
                {
                    "weather": weather,
                    "decisions": decisions,
                    "weather_score": weather_score,
                    "match_score": match_score,
                    "recommendations": recommendations,
                }
            )

else:
    md(
        '<div class="state-card">'
        '<div class="state-title">Waiting on a location</div>'
        '<div class="state-text">Add an OpenWeatherMap API key in the sidebar, enter a city above, '
        "and choose a category — the agent will pull current conditions, run them through the "
        "decision engine, and surface matching activities.</div>"
        "</div>"
    )