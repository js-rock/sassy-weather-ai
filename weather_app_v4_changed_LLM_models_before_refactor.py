#=============================================================================
#PROJECT: WeatherApp | Version 04
#=============================================================================
#STATUS LOG:
#mark03.02 is 18- -- 
#[2026-03-11][PENDING] custom voices? maybe not worth it right now
#2023-03-14 changed AI model Deepseek-r1:8b to Gemma3:4b for quicker performance
#TO DO:
#Convert pyttsx3 to edge-tts for voice custmisation
#Use a microphone for verbal answers as well as typed
#Remove ollama as a needed server and use local LLM 
#=============================================================================

#1 start with this:
import requests
from datetime import datetime, timezone #<----- timezone added as part of #18
from dotenv import load_dotenv
import os
load_dotenv()

#11 import pyttsx3 (make sure to pip insall pyttsx3 in cmd prior)
import pyttsx3

#12 Intialize voice engine (using built in OS voices and offline)
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('rate', 180) #this sets the speaking speed

#2 list your permanents:

api_key = os.getenv("openweather_api_key")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

#16 Create the prompt for the AI behavior here / amended in v03.02. to be a variable
ai_sass = """
"You are a sassy weather expert."
"You speak with some snark and sarcasm".
"Will i need a jacket today?"
"""

ai_classy = """
"You are a local Sydney based weather expert."
"You speak with debonair in classical olde english."
"For the purpose of your commentary: 15-22°C is "perfect","
"23-27°C is "Warm","
"28°C and above is "Too hot for the park" and should be described as "sweltering" or "uncomfortably warm"."
"""

ai_noob = """
"You are a weather expert and also a budding photogaphy assistant."
"You speak with some nevousness and comment specifically on natural sunlight or daylight lighting and wind speed in a photography context."
"If its too windy, comment on the model or talent's hair and clothes being blown away or tripods and stands being blown over"
"Keep it to 2 paragraphs."
"""


personas = {
    "1":  ai_sass,
    "2":  ai_classy,
    "3":  ai_noob
    }
   

#7 Loop <------ take note this was a later step!
while True:
    city = input("\nEnter city (or type exit): ")
    if city.lower() == 'exit':
        print("\n" + "="*30)
        print("  SYSTEM SHUTDOWN COMPLETE  ")
        print("="*30)
        break
    choose_persona = input("\nWhich personality do you prefer? 1.Sassy, 2.Classy, or 3.Noob Photographer? Enter a number 1-3: ").lower()
    
    #3 Ask user for city <----- Replaced in #7

                      
    #4 parameters. Or rules needed for API calls etc:
    parameters = {
        "q": city,
        "appid": api_key,
        "units": "metric"
        }

    #5 Call API
    #8 <----- take note this is a later step! Trying a TRY BLOCK (for testing the code, formerly WHILE loop)
    try:    
        response = requests.get(BASE_URL, params=parameters )
        weather_data = response.json()
        #18 fix for timezone issues
        offset = weather_data.get("timezone", 0)

    #6 Test! The output print("Setup is done!")

        if weather_data.get("cod") == 200:
            temp = weather_data['main']['temp']
            desc = weather_data['weather'][0]['description']
            humidity = weather_data['main']['humidity']
            #9 Added wind (on my own) and sunset(had troublebecause of 24hour time)
            wind_speed = weather_data['wind']['speed']
            wind_gust = weather_data['wind'].get('gust')
            sunrise_ts = weather_data['sys']['sunrise'] + offset
            sunset_ts = weather_data['sys']['sunset'] + offset
            #10 Format Timestamps (The 24hr fix)
            sunrise = datetime.fromtimestamp(sunrise_ts, timezone.utc).strftime('%H:%M') #<----- updated in #18 as per API request changing standards
            sunset = datetime.fromtimestamp(sunset_ts, timezone.utc).strftime('%H:%M') #<----- updated in #18 as per API request changing standards
            #14 <--- added later --- prep prompt for AI LLM
            weather_prompt_for_ai_llm = (
                f"The Weather in {city.title()} is {temp} ºC, {desc}, with wind at {wind_speed} meters per second."
                f"IMPORTANT: Do not use abbreviations like 'm/s' or 'ºC' in your response, "
                f"write them out fully as 'meters per second' and 'degrees Celsius'."
                )
            #15 Call the " AI Persona" (wrap in a separate 'try' to keep it safe)
            try:
                import ollama
                user_selected_persona = personas.get(choose_persona.lower(), ai_sass)
                llm_response = ollama.chat(model='gemma3:4b', messages=[
                    {'role': 'system', 'content': user_selected_persona},
                    {'role': 'user', 'content': weather_prompt_for_ai_llm}
                    ])
                ai_persona = llm_response['message']['content']
            except Exception:
                ai_persona = "I couldn't reach my brain, but its currently " +str(temp) + " degrees."
            print(f"--- Weather in {city.title()} ---")
            print(f"Temperature: {temp} °Celcius")
            print(f"Condition: {desc.capitalize()}")
            print(f"Humidity: {humidity}%")
            print(f"Wind Speed: {wind_speed} meters")
            print(f"Wind gust: {(wind_gust if wind_gust else ' None')} meters")        
            #11 Format Timestamps to print
            print(f"Sunrise: {sunrise} am")
            print(f"Sunset: {sunset} pm")
            timestamp = datetime.now().strftime("%y-%m-%d-%H:%M")
          


            #12 Creeate the voice reporting
            #We build one long string for the AI to read naturally
            report = (
                f"Update for {city.title()}. "
                f"It is currently {int(temp)} degrees with {desc}. "
                f"Wind speed is {int(wind_speed)} meters per second. "
                f"Sunrise was at {sunrise} and sunset is at {sunset}. "
            )

                       
            #13 Output: Print and Speak UPDATE in #16, this has been disabled by adding ###. Can be deleted in professional context.
            #print (f"\n--- {city.title()} ---")
            #print(report)

            #engine.say(report)
            #engine.runAndWait() # This makes the code wait until the AI finishes talking

            #17 AI LLM Print and speak (only here)
            print (f"\n--- {city.title()} AI Report ---")
            print (ai_persona)

            engine.say(ai_persona)
            engine.runAndWait()

            with open("weather_history.txt", "a") as file:
                file.write (f"[{timestamp}] City: {city} | Temp: {temp}°C\n")
                print ("\nResult saved to history log")

        else:
            print (f"Error: {weather_data.get('message', 'unknown error')}")

           
    except Exception as e:
            # This runs if the user types a fake city or the internet cuts out
            print(f"Error: Could not find '{city}'. Please check your spelling or connection.")
            #print(f"Debug: The error is: {e}") #use this for debugging
            
                    

input("\nPress enter to close this window")
