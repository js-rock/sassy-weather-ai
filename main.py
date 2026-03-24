
#1.Follow up context loops back to the original prompt when typing gibberish <-------------- mostly fixed, just returns a roast when following up with a legit question.

#2.Need to redefine prompts as AI took instructions too literally, i.e. reads both 24hour time and 12 hour time together.
#3.Sometimes it titles 'roast' before doing the 'roast user about chosen city' prompt.
#4.Get voice working but need a mic first




from weather_api import get_weather_data
from datetime import datetime, timezone
from llm_brain import get_ai_response, extract_city_from_text
import asyncio
from voice_engine import say_text
import random

def get_valid_city(user_input, last_city):
    #created because second 'gibberish' prompt kept looping 'last city' results
    extracted = extract_city_from_text(user_input)

    # Scenario A: User types in nonsense
    if not extracted or "none" in extracted.lower():
        return None
    return extracted

def main():

    ROASTS = [
        "I don't speak moron. Give me a real destination.",
        "Is that even a language? Try typing an actual city.",
        "My circuits are hurting. Use your words... and a map.",
        "404: Your brain malfunctioned. Please input a location."
        ]
        
    last_city = None

    voice_to_use = "en-US-AvaNeural"

    print("\n--- SASSY WEATHER SYSTEM ONLINE ---")

    choose_persona = input("\nWhich personality do you prefer? 1.Sassy, 2.Classy, or 3.Noob Photographer? : ")
    
    while True:
        user_text = input("\nHurry up and ask your weather question (or type exit): ").strip()

        if user_text.lower() ==  "exit":
            print("\n" + "=" *46)
            print("DON'T LET THE APP HIT YOUR ARSE ON THE WAY OUT")
            print("=" *46)
            break
        # Ask the AI to find the city in the sentence
        current_city = get_valid_city(user_text, last_city)
        
        #contextual memory added to add questions to existing city
               
        if not current_city:
            # If it's None, we know it's roast time
            roast = random.choice(ROASTS)
            asyncio.run(say_text(roast, voice_to_use))
            continue
        
        last_city = current_city

    # We 'call' the tool we made in the weather_api
        data = get_weather_data(last_city)
        

        if data:        
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

            print(f"\n--- Weather in {last_city.title()} ---")
            print(f"\nTemperature: {temp} °Celcius")
            print(f"Condition: {desc.capitalize()}")
            print(f"Humidity: {humidity}%")
            print(f"Wind Speed: {wind_speed} meters")
            print(f"Wind gust: {(wind_gust if wind_gust else ' None')} meters")        
            print(f"Sunrise: {sunrise} am")
            print(f"Sunset: {sunset} pm")
            timestamp = datetime.now().strftime("%y-%m-%d-%H:%M")

            # Get the AI's take on the weather
            ai_commentary, voice_to_use = get_ai_response(
                choose_persona, last_city, temp, desc, wind_speed, sunset
            )
            print(f"\nWeather Report: \n{ai_commentary}")
           
            asyncio.run(say_text(ai_commentary, voice_to_use))
            
        else:
            print("I couldn't find that city, are you making it up?")

if __name__ == "__main__":
    main()
