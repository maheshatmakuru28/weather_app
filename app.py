
import requests
import pandas as pd
import streamlit as st

# ==========================================
# PROFESSIONAL WORLDWIDE WEATHER APP
# ==========================================

st.set_page_config(
    page_title="World Weather",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# ==========================================
# PROFESSIONAL DESIGN
# ==========================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #071426, #142b45);
    color: #ffffff;
}

h1, h2, h3 {
    color: #7dd3fc !important;
}

[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.07);
    padding: 18px;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.12);
}

.stButton > button {
    border-radius: 10px;
    font-weight: bold;
    min-height: 44px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# WEATHER CONDITIONS
# ==========================================

WEATHER_CODES = {
    0: "Clear Sky ☀️",
    1: "Mainly Clear 🌤️",
    2: "Partly Cloudy ⛅",
    3: "Overcast ☁️",
    45: "Fog 🌫️",
    48: "Rime Fog 🌫️",
    51: "Light Drizzle 🌦️",
    53: "Drizzle 🌦️",
    55: "Heavy Drizzle 🌧️",
    56: "Freezing Drizzle",
    57: "Heavy Freezing Drizzle",
    61: "Light Rain 🌧️",
    63: "Rain 🌧️",
    65: "Heavy Rain ⛈️",
    66: "Freezing Rain",
    67: "Heavy Freezing Rain",
    71: "Light Snow ❄️",
    73: "Snow ❄️",
    75: "Heavy Snow ❄️",
    77: "Snow Grains ❄️",
    80: "Rain Showers 🌦️",
    81: "Heavy Rain Showers 🌧️",
    82: "Violent Rain Showers ⛈️",
    85: "Snow Showers ❄️",
    86: "Heavy Snow Showers ❄️",
    95: "Thunderstorm ⛈️",
    96: "Thunderstorm with Hail ⛈️",
    99: "Severe Thunderstorm ⛈️"
}

# ==========================================
# INITIALIZE SESSION STATE
# ==========================================

if "locations" not in st.session_state:
    st.session_state.locations = []

if "weather_data" not in st.session_state:
    st.session_state.weather_data = None

if "selected_location" not in st.session_state:
    st.session_state.selected_location = None

if "search_message" not in st.session_state:
    st.session_state.search_message = ""

# ==========================================
# SEARCH WORLDWIDE LOCATIONS
# ==========================================

@st.cache_data(ttl=3600, show_spinner=False)
def search_locations(place_name):

    response = requests.get(
        GEO_URL,
        params={
            "name": place_name,
            "count": 10,
            "language": "en",
            "format": "json"
        },
        timeout=20
    )

    response.raise_for_status()

    return response.json().get("results", [])

# ==========================================
# FETCH WEATHER DATA
# ==========================================

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_weather(latitude, longitude):

    response = requests.get(
        WEATHER_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "is_day,"
                "precipitation,"
                "weather_code,"
                "wind_speed_10m"
            ),
            "daily": (
                "weather_code,"
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_probability_max"
            ),
            "forecast_days": 7,
            "timezone": "auto"
        },
        timeout=25
    )

    response.raise_for_status()

    return response.json()

# ==========================================
# LOCATION LABEL
# ==========================================

def get_location_label(location):

    parts = [
        location.get("name"),
        location.get("admin3"),
        location.get("admin2"),
        location.get("admin1"),
        location.get("country")
    ]

    unique_parts = []

    for part in parts:
        if part and part not in unique_parts:
            unique_parts.append(part)

    return ", ".join(unique_parts)

# ==========================================
# APP HEADER
# ==========================================

st.title("🌍 World Weather")
st.write(
    "Discover current weather and 7-day forecasts "
    "for locations around the world."
)

st.caption(
    "Search by village, town, city, or other available "
    "location names."
)

# ==========================================
# LOCATION SEARCH FORM
# ==========================================

with st.form("worldwide_location_search"):

    place_name = st.text_input(
        "📍 Enter a location",
        placeholder="Example: Nellore, London, New York"
    )

    search_button = st.form_submit_button(
        "🔎 Search Location",
        use_container_width=True
    )

if search_button:

    if len(place_name.strip()) < 2:

        st.warning(
            "Please enter at least two characters."
        )

    else:

        # Clear old results before a new search.

        st.session_state.locations = []
        st.session_state.weather_data = None
        st.session_state.selected_location = None
        st.session_state.search_message = ""

        try:

            with st.spinner("Searching worldwide locations..."):

                results = search_locations(
                    place_name.strip()
                )

            st.session_state.locations = results

            if not results:

                st.session_state.search_message = (
                    "No matching locations were found. "
                    "Check the spelling or try a nearby town or city."
                )

        except requests.HTTPError as error:

            status = (
                error.response.status_code
                if error.response is not None
                else None
            )

            if status == 429:

                st.session_state.search_message = (
                    "Too many requests. Please wait before "
                    "searching again."
                )

            else:

               
