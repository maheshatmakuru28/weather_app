import requests
import streamlit as st
from datetime import datetime

# ==========================================
# PROFESSIONAL WORLDWIDE WEATHER APP
# ==========================================

st.set_page_config(
    page_title="Weather Pro | Worldwide Weather",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: ("Clear Sky", "☀️"),
    1: ("Mainly Clear", "🌤️"),
    2: ("Partly Cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing Rime Fog", "🌫️"),
    51: ("Light Drizzle", "🌦️"),
    53: ("Moderate Drizzle", "🌦️"),
    55: ("Heavy Drizzle", "🌧️"),
    56: ("Light Freezing Drizzle", "🌧️"),
    57: ("Heavy Freezing Drizzle", "🌧️"),
    61: ("Light Rain", "🌧️"),
    63: ("Moderate Rain", "🌧️"),
    65: ("Heavy Rain", "🌧️"),
    66: ("Light Freezing Rain", "🌧️"),
    67: ("Heavy Freezing Rain", "🌧️"),
    71: ("Light Snow", "🌨️"),
    73: ("Moderate Snow", "❄️"),
    75: ("Heavy Snow", "❄️"),
    77: ("Snow Grains", "🌨️"),
    80: ("Light Rain Showers", "🌦️"),
    81: ("Moderate Rain Showers", "🌧️"),
    82: ("Heavy Rain Showers", "⛈️"),
    85: ("Snow Showers", "🌨️"),
    86: ("Heavy Snow Showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with Hail", "⛈️"),
    99: ("Severe Thunderstorm with Hail", "⛈️"),
}


def weather_description(code):
    return WEATHER_CODES.get(
        code, ("Unknown Conditions", "🌍")
    )


@st.cache_data(ttl=600, show_spinner=False)
def search_locations(name):
    response = requests.get(
        GEO_URL,
        params={
            "name": name,
            "count": 10,
            "language": "en",
            "format": "json",
        },
        timeout=15,
    )
    response.raise_for_status()

    data = response.json()
    return data.get("results", [])


@st.cache_data(ttl=600, show_spinner=False)
def get_weather(latitude, longitude):
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
                "precipitation_probability_max,"
                "sunrise,"
                "sunset"
            ),
            "timezone": "auto",
            "forecast_days": 7,
        },
        timeout=20,
    )
    response.raise_for_status()

    return response.json()


# ==========================================
# PROFESSIONAL DESIGN
# ==========================================

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            135deg, #07152e, #102e50, #174b68
        );
        color: white;
    }

    h1, h2, h3, p, label {
        color: white !important;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.09);
        padding: 18px;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.15);
    }

    div[data-testid="stMetricValue"] {
        color: #7ee7ff;
    }

    div[data-testid="stMetricLabel"] {
        color: white;
    }

    .weather-card {
        background: rgba(255,255,255,0.10);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.15);
        margin-bottom: 15px;
    }

    .weather-icon {
        font-size: 65px;
    }

    .temperature {
        font-size: 55px;
        font-weight: bold;
        color: #7ee7ff;
    }

    .small-text {
        color: #d7e8ff;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# APP HEADER
# ==========================================

st.title("🌍 Weather Pro")
st.caption(
    "Worldwide Weather Forecast | Search Cities, Towns and Villages"
)

st.divider()


# ==========================================
# LOCATION SEARCH
# ==========================================

with st.sidebar:
    st.header("🔎 Location Search")

    location_name = st.text_input(
        "Enter a location",
        placeholder="Example: Nellore, India",
        key="location_input",
    )

    search_button = st.button(
        "🌍 Search Weather",
        use_container_width=True,
        type="primary",
    )

    st.info(
        "Search for a village, town, city or other "
        "available location anywhere in the world."
    )

    st.caption("Weather data: Open-Meteo")


if "locations" not in st.session_state:
    st.session_state.locations = []

if "searched_name" not in st.session_state:
    st.session_state.searched_name = ""


if search_button:
    query = location_name.strip()

    if len(query) < 2:
        st.warning(
            "Please enter a location name with at least "
            "2 characters."
        )
    else:
        try:
            with st.spinner(
                f"Searching worldwide for {query}..."
            ):
                results = search_locations(query)

            st.session_state.locations = results
            st.session_state.searched_name = query

            if not results:
                st.warning(
                    "No matching locations found. "
                    "Check the spelling or try a nearby town."
                )

        except requests.RequestException:
            st.error(
                "Could not connect to the location service. "
                "Please check your internet connection and try again."
            )

        except (ValueError, TypeError):
            st.error(
                "The location service returned invalid data. "
                "Please try again."
            )


# ==========================================
# LOCATION SELECTION
# ==========================================

locations = st.session_state.locations

if locations:
    st.subheader("📍 Select Your Location")

    def location_label(place):
        parts = [
            place.get("name", "Unknown"),
            place.get("admin1"),
            place.get("country"),
        ]

        return ", ".join(
            str(part)
            for part in parts
            if part
        )

    selected_index = st.selectbox(
        "Available matching locations",
        options=list(range(len(locations))),
        format_func=lambda index: location_label(
            locations[index]
        ),
        key="selected_location",
    )

    selected_location = locations[selected_index]

    latitude = selected_location.get("latitude")
    longitude = selected_location.get("longitude")

    if latitude is not None and longitude is not None:

        st.caption(
            f"Coordinates: {latitude:.4f}, {longitude:.4f}"
        )

        # ==========================================
        # FETCH WEATHER
        # ==========================================

        try:
            with st.spinner("Getting live weather data..."):
                weather_data = get_weather(
                    float(latitude),
                    float(longitude),
                )

            current = weather_data.get("current", {})
            daily = weather_data.get("daily", {})

            if not current:
                st.error(
                    "Current weather information is unavailable "
                    "for this location."
                )
            else:
                code = current.get("weather_code", 0)
                description, icon = weather_description(code)

                temperature = current.get("temperature_2m")
                humidity = current.get("relative_humidity_2m")
                feels_like = current.get("apparent_temperature")
                wind_speed = current.get("wind_speed_10m")
                precipitation = current.get("precipitation")

                # ==========================================
                # CURRENT WEATHER CARD
                # ==========================================

                st.divider()

                st.subheader(
                    f"📍 Weather in {location_label(selected_location)}"
                )

                st.markdown(
                    f"""
                    <div class="weather-card">
                        <div class="weather-icon">{icon}</div>
                        <div class="temperature">
                            {
                                f"{temperature:.1f} °C"
                                if temperature is not None
                                else "N/A"
                            }
                        </div>
                        <h3>{description}</h3>
                        <div class="small-text">
                            Current weather conditions
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # ==========================================
                # WEATHER METRICS
                # ==========================================

                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "🌡️ Feels Like",
                    (
                        f"{feels_like:.1f} °C"
                        if feels_like is not None
                        else "N/A"
                    ),
                )

                col2.metric(
                    "💧 Humidity",
                    (
                        f"{humidity}%"
                        if humidity is not None
                        else "N/A"
                    ),
                )

                col3.metric(
                    "🌬️ Wind Speed",
                    (
                        f"{wind_speed} km/h"
                        if wind_speed is not None
                        else "N/A"
                    ),
                )

                col4.metric(
                    "🌧️ Precipitation",
                    (
                        f"{precipitation} mm"
                        if precipitation is not None
                        else "N/A"
                    ),
                )

                # ==========================================
                # SUNRISE AND SUNSET
                # ==========================================

                st.subheader("🌅 Sunrise & Sunset")

                sunrise_data = daily.get("sunrise", [])
                sunset_data = daily.get("sunset", [])

                sun_col1, sun_col2 = st.columns(2)

                if sunrise_data:
                    sun_col1.metric(
                        "🌅 Sunrise",
                        sunrise_data[0].split("T")[-1],
                    )

                if sunset_data:
                    sun_col2.metric(
                        "🌇 Sunset",
                        sunset_data[0].split("T")[-1],
                    )

                # ==========================================
                # SEVEN-DAY FORECAST
                # ==========================================

                st.divider()
                st.subheader("📅 7-Day Weather Forecast")

                dates = daily.get("time", [])
                max_temps = daily.get(
                    "temperature_2m_max", []
                )
                min_temps = daily.get(
                    "temperature_2m_min", []
                )
                codes = daily.get("weather_code", [])
                rain_chances = daily.get(
                    "precipitation_probability_max", []
                )

                for i, date_string in enumerate(dates):
                    forecast_code = (
                        codes[i] if i < len(codes) else 0
                    )

                    forecast_description, forecast_icon = (
                        weather_description(forecast_code)
                    )

                    try:
                        formatted_date = datetime.strptime(
                            date_string, "%Y-%m-%d"
                        ).strftime("%A, %d %b")
                    except ValueError:
                        formatted_date = date_string

                    max_temp = (
                        max_temps[i]
                        if i < len(max_temps)
                        else None
                    )

                    min_temp = (
                        min_temps[i]
                        if i < len(min_temps)
                        else None
                    )

                    rain_chance = (
                        rain_chances[i]
                        if i < len(rain_chances)
                        else None
                    )

                    with st.container(border=True):
                        forecast_col1, forecast_col2, forecast_col3 = (
                            st.columns([2, 1, 2])
                        )

                        forecast_col1.write(
                            f"**{formatted_date}**"
                        )

                        forecast_col2.write(
                            f"{forecast_icon} {forecast_description}"
                        )

                        if (
                            max_temp is not None
                            and min_temp is not None
                        ):
                            forecast_col3.write(
                                f"🌡️ {min_temp}°C – {max_temp}°C"
                            )
                        else:
                            forecast_col3.write(
                                "Temperature unavailable"
                            )

                        if rain_chance is not None:
                            st.caption(
                                f"🌧️ Maximum precipitation probability: "
                                f"{rain_chance}%"
                            )

                st.divider()

                st.caption(
                    "Weather data provided by Open-Meteo. "
                    "Forecasts are estimates and may change."
                )

        except requests.RequestException:
            st.error(
                "Unable to retrieve weather data. "
                "Please try again later."
            )

        except (ValueError, TypeError, KeyError):
            st.error(
                "The weather service returned unexpected data. "
                "Please search again."
            )

else:
    st.markdown(
        """
        <div class="weather-card">
            <div class="weather-icon">🌍</div>
            <h2>Explore Weather Around the World</h2>
            <p>
                Search for a location using the search box
                in the sidebar to view current weather,
                humidity, wind speed, sunrise, sunset
                and a 7-day forecast.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "👈 Enter a location in the sidebar and click "
        "'Search Weather' to get started."
    )
