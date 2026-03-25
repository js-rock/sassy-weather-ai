#1. Change weather_api to 5 day / 3 hour
#2. Test mic / voice

from weather_api import get_weather_data
from datetime import datetime, timezone
from llm_brain import get_ai_response, extract_city_from_text
import asyncio
from voice_engine import say_text
import random

def main():
    ROASTS = [
        "I don't speak moron. Give me a real destination.",
        "Is that even a language? Try typing an actual city.",
        "My circuits are hurting. Use your words... and a map.",
        "You must be on drugs. Please input a location."
    ]
        
    last_city = None
    voice_to_use = "en-US-AvaNeural" # Default voice

    print("\n--- SASSY WEATHER SYSTEM ONLINE ---")
    choose_persona = input("\nWhich personality? 1.Sassy, 2.Classy, 3.Noob: ").strip()
    
    while True:
        user_text = input("\nHurry up and ask (or type exit/reset): ").strip()

        # 1. Exit Logic
        if user_text.lower() == "exit":
            print("\n" + "=" * 46 + "\nDON'T LET THE APP HIT YOUR ARSE ON THE WAY OUT\n" + "=" * 46)
            break

        # 2. Reset Logic
        if user_text.lower() in ["reset", "clear"]:
            last_city = None
            print("Sassy: Memory wiped. Who are you again?")
            continue

        # 3. THE HEART: Extract city using memory
        current_city = extract_city_from_text(user_text, last_city)

        # 4. THE FORK: Valid City vs. Gibberish
        if not current_city or current_city.lower() == "none":
            roast = random.choice(ROASTS)
            print(f"Sassy: {roast}")
            asyncio.run(say_text(roast, voice_to_use))
            continue # Skip the rest of the loop and ask again
        
        # We have a valid city! Save it to memory
        last_city = current_city

        # 5. FETCH DATA
        data = get_weather_data(last_city)

        if data:        
            offset = data.get("timezone", 0)
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            wind_speed = data['wind']['speed']
            sunset_ts = data['sys']['sunset'] + offset
            sunset = datetime.fromtimestamp(sunset_ts, timezone.utc).strftime('%H:%M')

            # 6. GET AI RESPONSE (Personality + Follow-up logic)
            ai_commentary, voice_to_use = get_ai_response(
                choose_persona, last_city, temp, desc, wind_speed, sunset, user_text
            )
            
            print(f"\n--- Weather in {last_city.title()} ---")
            print(f"Report: {ai_commentary}")
           
            asyncio.run(say_text(ai_commentary, voice_to_use))
            
        else:
            print(f"Sassy: I couldn't find {last_city}. Are you making up places now?")

if __name__ == "__main__":
    main()
