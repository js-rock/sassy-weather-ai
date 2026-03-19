import requests
from dotenv import load_dotenv
import os

# This looks for the .env file in your folder
load_dotenv()
# This grabs the specific 'secret' from that file
api_key = os.getenv("openweather_api_key")
url = "https://api.openweathermap.org/data/2.5/weather"

def get_weather_data(city):
    # We build the full URL with the city and key here
    # OpenWeatherMap uses 'q' for city and 'appid' for the key
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
        }
    try:
        response = requests.get(url, params=params)
        # In Python, we check response.status_code
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error on API: {response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
