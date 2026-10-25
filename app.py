import streamlit as st
import requests
from datetime import datetime

# ==================================================
# WEATHER PRO - WORLDWIDE WEATHER APPLICATION
# Python + Streamlit + Open-Meteo API
# ==================================================

st.set_page_config(
    page_title="Weather Pro | Worldwide Weather",
    page_icon="🌍",
    layout="wide",
)

# ==================================================
# API CONFIGURATION
# ==================================================

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: ("Clear Sky", "☀️"),
    1: ("Mainly Clear", "🌤️"),
    2: ("Partly Cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Rime Fog", "🌫️"),
    51: ("Light Drizzle", "🌦️"),
    53: ("Moderate Drizzle", "🌦️"),
    55: ("Heavy Drizzle", "🌧️"),
    56: ("Freezing Drizzle", "🌧️"),
    57: ("Heavy Freezing Drizzle", "🌧️"),
    61: ("Light Rain", "🌦️"),
    63: ("Moderate Rain", "🌧️"),
    65: ("Heavy Rain", "🌧️"),
    66: ("Freezing Rain", "🌧️"),
    67: ("Heavy Freezing Rain", "🌧️"),
    71: ("Light Snow", "🌨️"),
    73: ("Moderate Snow", "❄️"),
    75: ("Heavy Snow", "❄️"),
    77: ("Snow Grains", "🌨️"),
    80: ("Rain Showers", "🌦️"),
    81: ("Moderate Rain Showers", "🌧️"),
    82: ("Heavy Rain Showers", "⛈️"),
    85: ("Snow Showers", "🌨️"),
    86: ("Heavy Snow Showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with Hail", "⛈️"),
    99: ("Severe Thunderstorm", "⛈️"),
}


def get_condition(code):
    return WEATHER_CODES.get(
        code,
        ("Weather information unavailable", "🌍")
    )


# ==================================================
# API REQUEST HELPER
# ==================================================

def api_get(url, params):
    response = requests.get(
        url,
        params=params,
        timeout=25,
        headers={
            "User-Agent": "WeatherProApp/1.0"
        },
    )

    if not response.ok:
        details = response.text[:500]
        raise RuntimeError(
            f"HTTP {response.status_code}: {details}"
        )

    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError(
            "The weather service returned invalid JSON."
        ) from exc


# ==================================================
# LOCATION SEARCH
# ==================================================

@st.cache_data(ttl=600, show_spinner=False)
def search_locations(location):
    data = api_get(
        GEOCODING_URL,
        {
            "name": location,
            "count": 10,
            "language": "en",
            "format": "json",
        },
    )

    return data.get("results", [])


# ==================================================
# GET WEATHER AND FORECAST
# ==================================================

@st.cache_data(ttl=600, show_spinner=False)
def get_weather(latitude, longitude):
    params = {
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
    }

    return api_get(WEATHER_URL, params)


# ==================================================
# PROFESSIONAL USER INTERFACE
# ==================================================

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            135deg,
            #07152e,
            #103b60,
            #087e91
        );
    }

    h1, h2, h3, p, label {
        color: white !important;
    }

    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.10);
        padding: 18px;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.15);
    }

    [data-testid="stMetricValue"] {
        color: #8be9ff;
    }

    .weather-card {
        background: rgba(255,255,255,0.10);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.18);
        margin-bottom: 18px;
    }

    .weather-icon {
        font-size: 60px;
    }

    .temperature {
        font-size: 48px;
        font-weight: bold;
        color: #8be9ff;
    }

    .subtitle {
        color: #e1f4ff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌍 Weather Pro")
st.markdown(
    '<p class="subtitle">'
    'Worldwide Weather Forecast | Cities, Towns & Villages'
    '</p>',
    unsafe_allow_html=True,
)

st.divider()


# ==================================================
# SIDEBAR SEARCH
# ==================================================

with st.sidebar:
    st.title("🔎 Location Search")

    location_input = st.text_input(
        "Enter village, town or city",
        placeholder="Example: Vakadu, India",
    )

    search_button = st.button(
        "🌍 Search Weather",
        type="primary",
        use_container_width=True,
    )

    st.caption(
        "Search locations available through Open-Meteo."
    )

    st.caption(
        "Weather information is provided by Open-Meteo."
    )


# ==================================================
# SESSION STATE
# ==================================================

if "locations" not in st.session_state:
    st.session_state.locations = []

if "last_search" not in st.session_state:
    st.session_state.last_search = ""


# ==================================================
# SEARCH HANDLER
# ==================================================

if search_button:
    query = location_input.strip()

    if len(query) < 2:
        st.warning(
            "Please enter a location name."
        )

    else:
        try:
            with st.spinner(
                f"Searching for {query}..."
            ):
                results = search_locations(query)

            st.session_state.locations = results
            st.session_state.last_search = query

            if not results:
                st.warning(
                    "Location not found. Check the spelling "
                    "or try a nearby town or city."
                )

        except requests.RequestException as exc:
            st.error(
                f"Location API connection failed: {exc}"
            )

        except RuntimeError as exc:
            st.error(
                f"Location service error: {exc}"
            )

        except (ValueError, TypeError) as exc:
            st.error(
                f"Unable to process location data: {exc}"
            )


# ==================================================
# DISPLAY LOCATION RESULTS
# ==================================================

locations = st.session_state.locations

if not locations:
    st.markdown(
        """
        <div class="weather-card">
            <div class="weather-icon">🌍</div>
            <h2>Explore Weather Around the World</h2>
            <p>
                Search for a location to view current
                temperature, humidity, wind speed,
                sunrise, sunset and a 7-day forecast.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    st.subheader("📍 Select Your Location")

    def format_location(place):
        parts = [
            place.get("name"),
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
        format_func=lambda index: format_location(
            locations[index]
        ),
    )

    selected = locations[selected_index]

    latitude = selected.get("latitude")
    longitude = selected.get("longitude")

    st.caption(
        f"Coordinates: {latitude}, {longitude}"
    )

    # ==================================================
    # WEATHER DISPLAY
    # ==================================================

    try:
        with st.spinner(
            "Loading current weather and forecast..."
        ):
            weather = get_weather(
                float(latitude),
                float(longitude),
            )

        current = weather.get("current", {})
        daily = weather.get("daily", {})

        if not current:
            st.error(
                "The weather service did not return "
                "current weather data."
            )

        else:
            temperature = current.get(
                "temperature_2m"
            )

            humidity = current.get(
                "relative_humidity_2m"
            )

            feels_like = current.get(
                "apparent_temperature"
            )

            wind_speed = current.get(
                "wind_speed_10m"
            )

            precipitation = current.get(
                "precipitation"
            )

            weather_code = current.get(
                "weather_code"
            )

            description, icon = get_condition(
                weather_code
            )

            st.divider()

            st.subheader(
                f"📍 {format_location(selected)}"
            )

            # CURRENT WEATHER CARD

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
                    <p>Current weather conditions</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # WEATHER METRICS

            st.subheader("🌡️ Weather Details")

            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)

            col1.metric(
                "🌡️ Feels Like",
                (
                    f"{feels_like} °C"
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

            # SUNRISE AND SUNSET

            st.divider()
            st.subheader("🌅 Sunrise & Sunset")

            sunrise_list = daily.get("sunrise", [])
            sunset_list = daily.get("sunset", [])

            sunrise_col, sunset_col = st.columns(2)

            if sunrise_list:
                sunrise_col.metric(
                    "🌅 Sunrise",
                    sunrise_list[0].split("T")[-1],
                )
            else:
                sunrise_col.metric(
                    "🌅 Sunrise", "N/A"
                )

            if sunset_list:
                sunset_col.metric(
                    "🌇 Sunset",
                    sunset_list[0].split("T")[-1],
                )
            else:
                sunset_col.metric(
                    "🌇 Sunset", "N/A"
                )

            # SEVEN-DAY FORECAST

            st.divider()
            st.subheader("📅 7-Day Forecast")

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

            for index, date_value in enumerate(dates):
                code = (
                    codes[index]
                    if index < len(codes)
                    else None
                )

                forecast_description, forecast_icon = (
                    get_condition(code)
                )

                try:
                    formatted_date = datetime.strptime(
                        date_value, "%Y-%m-%d"
                    ).strftime("%A, %d %b")
                except ValueError:
                    formatted_date = date_value

                minimum = (
                    min_temps[index]
                    if index < len(min_temps)
                    else None
                )

                maximum = (
                    max_temps[index]
                    if index < len(max_temps)
                    else None
                )

                rain = (
                    rain_chances[index]
                    if index < len(rain_chances)
                    else None
                )

                with st.container(border=True):
                    st.markdown(
                        f"### {forecast_icon} {formatted_date}"
                    )

                    st.write(forecast_description)

                    forecast_col1, forecast_col2 = (
                        st.columns(2)
                    )

                    if (
                        minimum is not None
                        and maximum is not None
                    ):
                        forecast_col1.metric(
                            "Minimum",
                            f"{minimum} °C",
                        )

                        forecast_col2.metric(
                            "Maximum",
                            f"{maximum} °C",
                        )

                    if rain is not None:
                        st.caption(
                            f"🌧️ Maximum precipitation "
                            f"probability: {rain}%"
                        )

            st.divider()

            st.caption(
                "Weather data: Open-Meteo. "
                "Forecast information may change."
            )

    # ==================================================
    # DETAILED ERROR HANDLING
    # ==================================================

    except requests.RequestException as exc:
        st.error(
            "Unable to connect to the weather service."
        )

        st.code(str(exc))

        st.info(
            "Check your internet connection and try again."
        )

    except RuntimeError as exc:
        st.error(
            "The weather API returned an error."
        )

        st.code(str(exc))

        st.info(
            "The error details above can help identify "
            "the exact API problem."
        )

    except (ValueError, TypeError, KeyError) as exc:
        st.error(
            "Unable to process the weather information."
        )

        st.code(str(exc))

st.divider()

st.caption(
    "Weather Pro | Powered by Python, Streamlit and Open-Meteo"
)
