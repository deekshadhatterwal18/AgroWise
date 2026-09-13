import requests


# Open-Meteo APIs — free, no API key needed.
# 1st API: convert location name -> latitude/longitude (geocoding)
# 2nd API: use latitude/longitude -> get weather data (forecast)
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


# Open-Meteo returns weather as a numeric "code" (WMO standard).
# This dictionary converts that code into human-readable text + emoji.
# Reference: https://open-meteo.com/en/docs
WEATHER_CODE_MAP = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    61: ("Slight rain", "🌦️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    71: ("Slight snow fall", "🌨️"),
    73: ("Moderate snow fall", "🌨️"),
    75: ("Heavy snow fall", "🌨️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"),
}


def describe_weather_code(code):
    """Turn a numeric weather code into (text, emoji). Default = Unknown."""
    return WEATHER_CODE_MAP.get(code, ("Unknown", "❓"))


def geocode_location(location_name):
    """
    Step 1: Convert a place name typed by the farmer (e.g. "Faridabad")
    into latitude/longitude, because the forecast API needs coordinates,
    not a city name.

    Returns a dict {name, admin1, country, latitude, longitude}
    or None if the place wasn't found / request failed.
    """

    if not location_name or not location_name.strip():
        return None

    try:
        # Call the geocoding API with the location name
        response = requests.get(
            GEOCODING_URL,
            params={"name": location_name.strip(), "count": 1},
            timeout=10
        )
        response.raise_for_status()  # raises error if API call failed

        data = response.json()
        results = data.get("results")

        if not results:
            return None  # place not found

        top = results[0]  # take the best/first match

        return {
            "name": top.get("name"),
            "admin1": top.get("admin1", ""),   # state/district
            "country": top.get("country", ""),
            "latitude": top.get("latitude"),
            "longitude": top.get("longitude")
        }

    except requests.RequestException as e:
        print("Geocoding error:", repr(e))
        return None


def get_weather_forecast(latitude, longitude):
    """
    Step 2: Given coordinates, fetch current weather + 7-day forecast.
    Returns a dict {current, forecast} or None on failure.
    """

    try:
        response = requests.get(
            FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                # what we want for "right now"
                "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
                # what we want for each of the next 7 days
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
                "timezone": "auto",
                "forecast_days": 7
            },
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        current = data.get("current", {})
        daily = data.get("daily", {})

        # --- Build "current weather" dict ---
        desc, icon = describe_weather_code(current.get("weather_code"))

        current_weather = {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "wind_speed": current.get("wind_speed_10m"),
            "description": desc,
            "icon": icon
        }

        # --- Build "7-day forecast" list ---
        # Open-Meteo returns each field as a separate list (same length,
        # same order = same day), so we loop by index and zip them together.
        dates = daily.get("time", [])
        forecast_days = []

        for i in range(len(dates)):
            day_desc, day_icon = describe_weather_code(
                daily.get("weather_code", [])[i]
                if i < len(daily.get("weather_code", [])) else None
            )

            forecast_days.append({
                "date": dates[i],
                "description": day_desc,
                "icon": day_icon,
                "temp_max": daily.get("temperature_2m_max", [None]*7)[i],
                "temp_min": daily.get("temperature_2m_min", [None]*7)[i],
                "rain_mm": daily.get("precipitation_sum", [None]*7)[i],
                "rain_probability": daily.get("precipitation_probability_max", [None]*7)[i],
                "wind_speed": daily.get("wind_speed_10m_max", [None]*7)[i]
            })

        return {
            "current": current_weather,
            "forecast": forecast_days
        }

    except requests.RequestException as e:
        print("Weather forecast error:", repr(e))
        return None


def generate_farming_advisory(weather_data):
    """
    Simple rule-based tips (if-else logic, not ML) based on the
    weather data — e.g. "rain expected -> delay fertilizer".
    Easy to explain: it's just plain conditional checks.
    """

    tips = []

    if not weather_data:
        return tips

    current = weather_data.get("current", {})
    forecast = weather_data.get("forecast", [])

    temp = current.get("temperature")
    humidity = current.get("humidity")

    # Rule 1: very hot -> suggest irrigation timing
    if temp is not None and temp >= 38:
        tips.append(
            "High temperature today — irrigate early morning or evening "
            "to reduce water loss and heat stress on crops."
        )

    # Rule 2: high humidity -> fungal disease risk
    if humidity is not None and humidity >= 85:
        tips.append(
            "High humidity increases fungal disease risk — "
            "monitor crops and ensure good field drainage."
        )

    # Rule 3: rain likely in next 3 days -> delay fertilizer
    upcoming_days = forecast[1:4]  # skip today, look at next 3 days

    rain_likely = any(
        (day.get("rain_probability") or 0) >= 60
        for day in upcoming_days
    )

    if rain_likely:
        tips.append(
            "Rain is likely in the next few days — consider delaying "
            "fertilizer application to avoid nutrient runoff."
        )
    else:
        tips.append(
            "No significant rain expected soon — plan irrigation "
            "accordingly."
        )

    # Rule 4: strong wind -> avoid spraying pesticide
    max_wind = max(
        (day.get("wind_speed") or 0 for day in forecast),
        default=0
    )

    if max_wind >= 40:
        tips.append(
            "Strong winds expected this week — avoid spraying "
            "pesticides/fertilizers on windy days."
        )

    return tips
