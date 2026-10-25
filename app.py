import requests
import pandas as pd
import streamlit as st

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="India Weather App",
    page_icon="🌦️",
    layout="wide"
)

# ---------------- DESIGN ----------------

st.title("🇮🇳 India Weather App")
st.write(
    "Check weather for villages, towns and cities across India."
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #334155);
    color: white;
}
h1 {
    color: #facc15;
}
</style>
""", unsafe_allow_html=True)

# ---------------- API URLS ----------------

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# ---------------- WEATHER CONDITIONS ----------------

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
    61: "Light Rain 🌧️",
    63: "Rain 🌧️",
    65: "Heavy Rain ⛈️",
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

# ---------------- SEARCH LOCATIONS ----------------

@st.cache_data(ttl=3600, show_spinner=False)
def search_locations(place_name):

    response = requests.get(
        GEO_URL,
        params={
            "name": place_name,
            "count": 10,
            "language": "en",
            "format": "json",
            "countryCode": "IN"
        },
        timeout=20
    )

    response.raise_for_status()

    return response.json().get("results", [])


# ---------------- GET WEATHER ----------------

@st.cache_data(ttl=1800, show_spinner=False)
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


# ---------------- USER INPUT ----------------

with st.form("location_search"):

    place_name = st.text_input(
        "📍 Enter village, town or city name",
        placeholder="Example: Nellore, Kavali, Hyderabad"
    )

    submitted = st.form_submit_button(
        "🔍 Search Weather",
        use_container_width=True
    )


# ---------------- SEARCH AND DISPLAY ----------------

if submitted:

    if not place_name.strip():
        st.warning("Please enter a village or city name.")

    else:

        try:

            with st.spinner("Searching for your location..."):

                locations = search_locations(
                    place_name.strip()
                )

            if not locations:

                st.error(
                    "Location not found in the database. "
                    "Check the spelling or try a nearby town."
                )

            else:

                # Let the user select the correct location.

                def location_label(location):

                    parts = [
                        location.get("name", "Unknown"),
                        location.get("admin3"),
                        location.get("admin2"),
                        location.get("admin1"),
                        location.get("country", "India")
                    ]

                    unique_parts = []
                    for part in parts:
                        if part and part not in unique_parts:
                            unique_parts.append(part)

                    return " - ".join(unique_parts)

                selected_location = st.selectbox(
                    "📌 Select the correct location",
                    locations,
                    format_func=location_label
                )

                st.info(
                    "Select the correct village or town, "
                    "then click the button below."
                )

                if st.button("🌤️ Get Selected Location Weather"):

                    latitude = selected_location["latitude"]
                    longitude = selected_location["longitude"]

                    with st.spinner("Getting weather forecast..."):

                        weather = get_weather(
                            latitude,
                            longitude
                        )

                    current = weather["current"]
                    daily = weather["daily"]

                    st.success(
                        "Weather found for "
                        + location_label(selected_location)
                    )

                    st.caption(
                        f"Latitude: {latitude} | "
                        f"Longitude: {longitude}"
                    )

                    # Current weather

                    st.subheader("🌡️ Current Weather")

                    code = int(current["weather_code"])

                    condition = WEATHER_CODES.get(
                        code,
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

                    col6.write("**Weather Condition**")
                    col6.write(condition)

                    st.caption(
                        f"Weather data time: {current['time']}"
                    )

                    # Seven-day forecast

                    st.divider()
                    st.subheader("📅 7-Day Weather Forecast")

                    forecast_df = pd.DataFrame({
                        "Date": daily["time"],
                        "Condition": [
                            WEATHER_CODES.get(
                                int(item),
                                "Unknown"
                            )
                            for item in daily["weather_code"]
                        ],
                        "Maximum Temperature (°C)": (
                            daily["temperature_2m_max"]
                        ),
                        "Minimum Temperature (°C)": (
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

            status = (
                error.response.status_code
                if error.response is not None
                else None
            )

            if status == 429:
                st.error(
                    "Too many requests. Please wait a while "
                    "before trying again."
                )
            else:
                st.error(
                    f"Weather service error (HTTP {status}). "
                    "Please try again later."
                )

        except requests.RequestException:
            st.error(
                "Could not connect to the weather service. "
                "Check your internet connection and try again."
            )

        except (KeyError, ValueError, TypeError):
            st.error(
                "Weather data could not be processed. "
                "Please try again later."
            )

# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "Weather data: Open-Meteo | "
    "Location search: Open-Meteo Geocoding API"
)

