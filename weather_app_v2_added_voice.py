#Breakdown notes
#mark01 is 1-7 -- python only setup -- 20260304 
#mark02 is 7-13 -- added voice feedback -- 20260306

#1 start with this:
import requests
from datetime import datetime #8 this was added later!
from dotenv import load_dotenv
import os
load_dotenv()
#11 import pyttsx3 (make sure to pip insall pyttsx3 in cmd prior)
import pyttsx3

#12 Intialize voice engine (using built in OS voices and offline)
engine = pyttsx3.init()
engine.setProperty('rate', 180) #this sets the speaking speed

#2 list your permanents:

api_key = os.getenv("openweather_api_key")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

#7 Loop <------ take note this was a later step!
while True:
    city = input("\nEnter city (or type exit): ")
    if city.lower() == 'exit':
        print("\n" + "="*30)
        print("  SYSTEM SHUTDOWN COMPLETE  ")
        print("="*30)
        break
    
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

    #6 Test! The output print("Setup is done!")

        if weather_data.get("cod") == 200:
            temp = weather_data['main']['temp']
            desc = weather_data['weather'][0]['description']
            humidity = weather_data['main']['humidity']
            #9 Added wind (on my own) and sunset(had troublebecause of 24hour time)
            wind_speed = weather_data['wind']['speed']
            wind_gust = weather_data['wind'].get('gust')
            sunrise_ts = weather_data['sys']['sunrise']
            sunset_ts = weather_data['sys']['sunset']
            #10 Format Timestamps (The 24hr fix)
            sunrise = datetime.fromtimestamp(sunrise_ts).strftime('%H:%M')
            sunset = datetime.fromtimestamp(sunset_ts).strftime('%H:%M')
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
            #13 Output: Print and Speak
            print (f"\n--- {city.title()} ---")
            print(report)

            engine.say(report)
            engine.runAndWait() # This makes the code wait until the AI finishes talking

            with open("weather_history.txt", "a") as file:
                file.write (f"[{timestamp}] City: {city} | Temp: {temp}°C\n")
                print ("\nResult saved to history log")

        else:
            print (f"Error: {weather_data.get('message', 'unknown error')}")

           
    except Exception as e:
            # This runs if the user types a fake city or the internet cuts out
            print(f"Error: Could not find '{city}'. Please check your spelling or connection.")
            
                    

input("\nPress enter to close this window")
