from weather_api import get_weather_data
from datetime import datetime, timezone
from llm_brain import get_ai_response

def main():
    print("\n--- SASSY WEATHER SYSTEM ONLINE ---")

    while True:
        city = input("\nEnter city (or type exit): ").strip()

        if city.lower() ==  "exit":
            print("\n" + "=" *46)
            print("DON'T LET THE APP HIT YOUR ARSE ON THE WAY OUT")
            print("=" *46)
            break

    # We 'call' the tool we made in the weather_api
        data = get_weather_data(city)
        

        if data:
            choose_persona = input("\nWhich personality do you prefer? 1.Sassy, 2.Classy, or 3.Noob Photographer? : ")
            offset = data.get("timezone", 0)
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            wind_gust = data['wind'].get('gust')
            sunrise_ts = data['sys']['sunrise'] + offset
            sunset_ts = data['sys']['sunset'] + offset
            sunrise = datetime.fromtimestamp(sunrise_ts, timezone.utc).strftime('%H:%M')
            sunset = datetime.fromtimestamp(sunset_ts, timezone.utc).strftime('%H:%M')

            print(f"\n--- Weather in {city.title()} ---")
            print(f"\nTemperature: {temp} °Celcius")
            print(f"Condition: {desc.capitalize()}")
            print(f"Humidity: {humidity}%")
            print(f"Wind Speed: {wind_speed} meters")
            print(f"Wind gust: {(wind_gust if wind_gust else ' None')} meters")        
            print(f"Sunrise: {sunrise} am")
            print(f"Sunset: {sunset} pm")
            timestamp = datetime.now().strftime("%y-%m-%d-%H:%M")

            # Get the AI's take on the weather
            ai_commentary = get_ai_response(choose_persona, city, temp, desc, wind_speed, sunset)
            print("\n" + "="*20)
            print(f"AI SAYS: {ai_commentary}")
            print("="*20)
            
        else:
            #print("Something went wrong with the weather fetch.")
            print("I couldn't find that city, are you making it up?")

if __name__ == "__main__":
    main()
