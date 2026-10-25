import requests
import pandas as pd
import streamlit as st

from datetime import datetime


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Weather App",
    page_icon="🌤️",
    layout="wide"
)

# ---------------- APP DESIGN ----------------

st.title("🌤️ Weather App")
st.write("Check current weather and a 7-day forecast.")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a, #334155);
        color: white;
    }

    h1 {
        color: #facc15;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------- API URLS ----------------

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


# ---------------- WEATHER CODES ----------------

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
    61: "Light Rain 🌦️",
    63: "Rain 🌧️",
    65: "Heavy Rain 🌧️",
    71: "Light Snow ❄️",
    73: "Snow ❄️",
    75: "Heavy Snow ❄️",
    80: "Rain Showers 🌦️",
    81: "Heavy Showers 🌧️",
    82: "Violent Showers ⛈️",
    95: "Thunderstorm ⛈️",
    96: "Thunderstorm with Hail ⛈️",
    99: "Severe Thunderstorm ⛈️"
}


# ---------------- GEOCODING ----------------

@st.cache_data(ttl=3600)
def geocode(city: str):

    response = requests.get(
        GEO_URL,
        params={
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        },
        timeout=20
    )

    response.raise_for_status()

    results = response.json().get("results", [])

    if not results:
        return None

    return results[0]


# ---------------- WEATHER DATA ----------------

@st.cache_data(ttl=1800)
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
                "precipitation_probability_max"
            ),
            "forecast_days": 7,
            "timezone": "auto"
        },
        timeout=20
    )

    response.raise_for_status()

    return response.json()


# ---------------- CITY INPUT ----------------

with st.form("weather_search_form"):

    city = st.text_input(
        "📍 Enter a city",
        value="Nellore",
        placeholder="Example: Nellore"
    )

    search_button = st.form_submit_button(
        "🔍 Get Weather"
    )


# ---------------- DISPLAY WEATHER ----------------

if search_button:

    if not city.strip():

        st.warning("Please enter a city name.")

    else:

        try:

            with st.spinner("Getting weather information..."):

                location = geocode(city.strip())

                if location is None:

                    st.error(
                        "City not found. Please check the city name."
                    )

                else:

                    latitude = location["latitude"]
                    longitude = location["longitude"]

                    weather = get_weather(
                        latitude,
                        longitude
                    )

                    current = weather["current"]
                    daily = weather["daily"]

                    city_name = location["name"]

                    country = location.get(
                        "country",
                        ""
                    )

                    st.success(
                        f"Weather for {city_name}, {country}"
                    )

                    st.caption(
                        f"Latitude: {latitude} | "
                        f"Longitude: {longitude}"
                    )

                    # Current weather

                    st.subheader("🌡️ Current Weather")

                    weather_code = int(
                        current["weather_code"]
                    )

                    condition = WEATHER_CODES.get(
                        weather_code,
                        "Weather information unavailable"
                    )

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Temperature",
                        f"{current['temperature_2m']} °C"
                    )

                    col2.metric(
                        "Feels Like",
                        f"{current['apparent_temperature']} °C"
                    )

                    col3.metric(
                        "Humidity",
                        f"{current['relative_humidity_2m']}%"
                    )

                    col4, col5, col6 = st.columns(3)

                    col4.metric(
                        "Wind Speed",
                        f"{current['wind_speed_10m']} km/h"
                    )

                    col5.metric(
                        "Precipitation",
                        f"{current['precipitation']} mm"
                    )

                    col6.write("**Condition**")

                    col6.write(condition)

                    st.caption(
                        f"Last weather data time: "
                        f"{current['time']}"
                    )

                    # Seven-day forecast

                    st.divider()

                    st.subheader("📅 7-Day Forecast")

                    forecast_df = pd.DataFrame({
                        "Date": daily["time"],
                        "Condition": [
                            WEATHER_CODES.get(
                                int(code),
                                "Unknown"
                            )
                            for code in daily["weather_code"]
                        ],
                        "Max Temperature (°C)": (
                            daily["temperature_2m_max"]
                        ),
                        "Min Temperature (°C)": (
                            daily["temperature_2m_min"]
                        ),
                        "Rain Probability (%)": (
                            daily[
                                "precipitation_probability_max"
                            ]
                        )
                    })

                    forecast_df["Date"] = pd.to_datetime(
                        forecast_df["Date"]
                    ).dt.strftime("%d-%m-%Y")

                    st.dataframe(
                        forecast_df,
                        use_container_width=True,
                        hide_index=True
                    )

                    st.success(
                        "Weather information loaded successfully! ✅"
                    )

        except requests.HTTPError as error:

            response = error.response

            if response is not None and response.status_code == 429:

                st.error(
                    "The weather service has temporarily "
                    "limited requests. Please wait a while "
                    "before trying again."
                )

            else:

                st.error(
                    f"Weather API error: {error}"
                )

        except requests.RequestException:

            st.error(
                "Unable to connect to the weather service. "
                "Please check your internet connection "
                "and try again later."
            )

        except (KeyError, ValueError, TypeError):

            st.error(
                "Weather data could not be processed. "
                "Please try again later."
            )


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "Weather data provided by Open-Meteo."
)
