from flask import Flask, render_template_string, request
import requests
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SkyCast Weather</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: 'Segoe UI', Arial, sans-serif;
            color: white;
            background: linear-gradient(135deg, #101b46, #2855a6, #20b8c5);
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 25px;
        }

        .container {
            width: 100%;
            max-width: 520px;
            text-align: center;
        }

        .brand {
            font-size: 30px;
            font-weight: 800;
            margin-bottom: 8px;
            letter-spacing: 1px;
        }

        .subtitle {
            color: #dbeafe;
            margin-bottom: 28px;
        }

        .card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 28px;
            padding: 30px 24px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
        }

        form {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
        }

        input {
            flex: 1;
            min-width: 0;
            padding: 14px;
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.5);
            outline: none;
            font-size: 16px;
        }

        button {
            padding: 14px 18px;
            border: none;
            border-radius: 14px;
            background: #ffe082;
            color: #172554;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
        }

        button:hover {
            background: #ffffff;
            transform: translateY(-2px);
        }

        .city {
            font-size: 27px;
            font-weight: 700;
            margin: 10px 0;
        }

        .weather-icon {
            font-size: 70px;
            margin: 12px 0;
        }

        .temperature {
            font-size: 58px;
            font-weight: 800;
            margin: 5px 0;
        }

        .label {
            color: #e0f2fe;
            margin-bottom: 25px;
        }

        .details {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }

        .detail {
            background: rgba(255, 255, 255, 0.13);
            padding: 16px 6px;
            border-radius: 17px;
            overflow-wrap: anywhere;
        }

        .detail-icon {
            font-size: 25px;
            margin-bottom: 8px;
        }

        .detail-name {
            font-size: 12px;
            color: #dbeafe;
        }

        .detail-value {
            font-size: 16px;
            font-weight: 700;
            margin-top: 7px;
        }

        .error {
            background: rgba(127, 29, 29, 0.5);
            border-radius: 12px;
            padding: 12px;
        }

        footer {
            margin-top: 22px;
            font-size: 12px;
            color: #dbeafe;
        }

        @media (max-width: 420px) {
            .card {
                padding: 22px 14px;
            }

            form {
                flex-direction: column;
            }

            .temperature {
                font-size: 48px;
            }

            .detail-value {
                font-size: 14px;
            }
        }
    </style>
</head>

<body>
    <main class="container">
        <div class="brand">🌤️ SkyCast</div>
        <div class="subtitle">Your personal weather dashboard</div>

        <section class="card">
            <form method="get">
                <input
                    type="text"
                    name="city"
                    placeholder="Enter city name..."
                    value="{{ city }}"
                    required
                >
                <button type="submit">Search 🔍</button>
            </form>

            {% if weather %}
                <div class="city">📍 {{ city }}</div>
                <div class="weather-icon">🌤️</div>
                <div class="temperature">
                    {{ weather.temperature }}°C
                </div>
                <div class="label">Current Temperature</div>

                <div class="details">
                    <div class="detail">
                        <div class="detail-icon">💧</div>
                        <div class="detail-name">Humidity</div>
                        <div class="detail-value">
                            {{ weather.humidity }}%
                        </div>
                    </div>

                    <div class="detail">
                        <div class="detail-icon">🌡️</div>
                        <div class="detail-name">Feels Like</div>
                        <div class="detail-value">
                            {{ weather.feels_like }}°C
                        </div>
                    </div>

                    <div class="detail">
                        <div class="detail-icon">💨</div>
                        <div class="detail-name">Wind Speed</div>
                        <div class="detail-value">
                            {{ weather.wind }} km/h
                        </div>
                    </div>
                </div>
            {% endif %}

            {% if error %}
                <p class="error">{{ error }}</p>
            {% endif %}
        </section>

        <footer>
            Made with ❤️ using Python & Flask
        </footer>
    </main>
</body>
</html>
"""   
@app.route("/")
def home():
    city = request.args.get("city", "Nellore")
    weather = None
    error = None

    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
            timeout=10
        ).json()

        if not geo.get("results"):
            error = "City not found. Try another city."
        else:
            place = geo["results"][0]
            data = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": place["latitude"],
                    "longitude": place["longitude"],
                    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m"
                },
                timeout=10
            ).json()["current"]

            weather = {
                "temperature": data["temperature_2m"],
                "humidity": data["relative_humidity_2m"],
                "feels_like": data["apparent_temperature"],
                "wind": data["wind_speed_10m"]
            }
    except Exception:
        error = "Weather data could not be loaded. Please try again."

    return render_template_string(
        HTML, city=city, weather=weather, error=error
    )

if __name__ == "__main__":
    app.run(debug=True)