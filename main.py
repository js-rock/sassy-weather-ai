#1. Test mic / voice commands
#2. Revisit other personalities as they've been neglected to focus on 'sassy'

# =================================================================
# SASSY WEATHER AI - MAIN CONTROL SUITE
# =================================================================
from weather_api import get_weather_data
from datetime import datetime, timezone, timedelta
from llm_brain import get_ai_response, extract_city_from_text
import asyncio
from voice_engine import say_text
import random

# -------------------------------------------------------------
    # CONFIG & MEMORY
    # -------------------------------------------------------------
def main():
    ROASTS = [
        "I don't speak moron. Give me a real destination.",
        "Is that even a language? Try typing an actual city.",
        "My circuits are hurting. Use your words... and a map.",
        "You must be on drugs. Please input a location."
    ]
        
    last_city = None
    voice_to_use = "en-US-AvaNeural" # Default voice

    # -------------------------------------------------------------
    # SYSTEM STARTUP
    # -------------------------------------------------------------
    print("\n--- SASSY WEATHER SYSTEM ONLINE ---")
    choose_persona = input("\nWhich personality? 1.Sassy, 2.Classy, 3.Noob Photographer: ").strip()

        
    while True:
        # ---------------------------------------------------------
        # USER INPUT & COMMAND PROCESSING
        # ---------------------------------------------------------
        user_text = input("\nJust ask me about the weather already (or type exit): ").strip()

        # Exit Logic
        if user_text.lower() == "exit":
            print("\n" + "=" * 46 + "\nDON'T LET THE APP HIT YOUR ARSE ON THE WAY OUT\n" + "=" * 46)
            break

                   
        # ---------------------------------------------------------
        # ENTITY EXTRACTION & DATA FETCHING
        # ---------------------------------------------------------    
        # THE HEART: Extract city using memory
        current_city = extract_city_from_text(user_text, last_city)

        # THE FORK: Valid City vs. Gibberish
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
            # -----------------------------------------------------
            # DATA NORMALIZATION & SYNC
            # -----------------------------------------------------      
            from weather_utils import get_daily_maxes, format_sassy_summary

            # Process the data ONCE
            max_data = get_daily_maxes(data) # Syncing the Print Box with the AI's forecast extraction
            all_dates = list(max_data.keys())
            
            # Set the defaults
            display_date = all_dates[0] 
            target_day = "Today"

            # Logic to match user-requested day to forecast data
            if "tomorrow" in user_text.lower():
                target_day = "Tomorrow"
                # If today is Friday (index 0), tomorrow is index 1
                if len(all_dates) > 1:
                    display_date = all_dates[1]

            else:
                for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
                    if day.lower() in user_text.lower():
                        target_day = day
                        # Match the day name to the actual date in our data
                        for date in all_dates:
                            day_name = datetime.strptime(date, '%Y-%m-%d').strftime('%A')
                            if day_name.lower() == day.lower():
                                display_date = date
                                break
                        break

            # Pull the stats for the chosen day
            stats = max_data[display_date]
            clean_summary = format_sassy_summary(max_data)

            # Extract specific display info (Wind/Sunset stays current)
            offset_seconds = data['city'].get('timezone', 0)
            wind_speed = data['list'][0]['wind']['speed']
            utc_sunset = datetime.fromtimestamp(data['city']['sunset'], timezone.utc)
            local_sunset = utc_sunset + timedelta(seconds=offset_seconds)
            sunset = local_sunset.strftime('%H:%M')

            # -----------------------------------------------------
            # UI: WEATHER DASHBOARD
            # -----------------------------------------------------
            print(f"\n" + "="*30)
            print(f"📍 LOCATION:  {last_city.title()}")
            print(f"📅 DAY:       {target_day.upper()}")  
            print(f"🌡️  HIGH:       {round(stats['temp'], 1)}°C") # Matches Sassy!
            print(f"🥵 HUMIDITY:  {stats['humidity']}%")
            print(f"☁️  SKY:        {stats['condition'].capitalize()}")
            print(f"💨 WIND:      {wind_speed} m/s")
            print(f"🌅 SUNSET:    {sunset}")
            print("="*30)

       
            # -----------------------------------------------------
            # AI INTERFERENCE & VOICE OUTPUT
            # -----------------------------------------------------
            ai_commentary, voice_to_use = get_ai_response(
                choose_persona, 
                last_city, 
                clean_summary,
                sunset,
                user_text
            )
            
            print(f"\n--- Weather in {last_city.title()} ---")
            print(f"Report: {ai_commentary}")
           
            asyncio.run(say_text(ai_commentary, voice_to_use))
            
        else:
            print(f"I couldn't find {last_city}. Are you making up places now?")

if __name__ == "__main__":
    main()
