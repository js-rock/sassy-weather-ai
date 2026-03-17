#Breakdown notes
#mark01 is 1-7 -- python only setup -- 20260304 


#1 start with this:
import requests
from datetime import datetime #8 this was added later!
from dotenv import load_dotenv
import os
load_dotenv()

#2 list your permanents:

api_key = os.getenv("openweather_api_key")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


#7 Loop <------ take note this was a later step!
while True:
    city = input("Enter city (or type exit): ")
    if city.lower() == 'exit':
        print("bye bye!")
        break 
    
    #3 Ask user for city <----- Replaced in #7

                      
    #4 parameters. Or rules needed for API calls etc:
    parameters = {
        "q": city,
        "appid": api_key,
        "units": "metric"
        }

    #5 Call API
    #9 <----- take note this is a later step! Trying a TRY BLOCK (for testing the code)
    try:    
        response = requests.get(BASE_URL, params=parameters )
        weather_data = response.json()

    #6 Test! The output print("Setup is done!")

        if weather_data.get("cod") == 200:
            temp = weather_data['main']['temp']
            desc = weather_data['weather'][0]['description']
            humidity = weather_data['main']['humidity']
            print(f"--- Weather in {city.title()} ---")
            print(f"Temperature: {temp} °Celcius")
            print(f"Condition: {desc.capitalize()}")
            print(f"Humidity: {humidity}%")
            timestamp = datetime.now().strftime("%y-%m-%d-%H:%M")
            

            with open("weather_history.txt", "a") as file:
                file.write (f"[{timestamp}] City: {city} | Temp: {temp}°C\n")
                print ("Result saved to history log")

        else:
            print (f"Error: {weather_data.get('message', 'unknown error')}")

           
    except Exception as e:
            # This runs if the user types a fake city or the internet cuts out
            print(f"Error: Could not find '{city}'. Please check your spelling or connection.")
            
                    

input("\nPress any key to close this window")
