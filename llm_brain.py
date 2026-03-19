import ollama

ai_sass = """
You are a sassy weather expert.
You speak with some snark and sarcasm.
Will i need a jacket today?
"""

ai_classy = """
You are a local Sydney based weather expert.
You speak with debonair in classical olde english.
For the purpose of your commentary: 15-22°C is "perfect",
23-27°C is "Warm",
28°C and above is "Too hot for the park" and should be described as "sweltering" or "uncomfortably warm".
"""

ai_noob = """
You are a weather expert and also a budding photogaphy assistant.
You speak with some nevousness and comment specifically on natural sunlight or daylight lighting and wind speed in a photography context.
If its too windy, comment on the model or talent's hair and clothes being blown away or tripods and stands being blown over.
Keep it to 2 paragraphs.
"""

def get_ai_response(persona_choice, city, temp, desc, wind_speed, sunset):
    personas = {
        "1": ai_sass,
        "2": ai_classy,
        "3": ai_noob
        }

    user_selected_persona = personas.get(persona_choice, personas["1"])

    weather_prompt = (
        f"The Weather in {city} is {temp} degrees Celcius, {desc}, "
        f"with winds at {wind_speed} meters per second. The sunset is at {sunset}. "
        f"Give me a short reaction."
        )
    try:
        response = ollama.chat(model='gemma3:4b', messages=[
            {'role': 'system', 'content': user_selected_persona},
            {'role': 'user', 'content': weather_prompt}
            ])
        return response['message']['content']
    
    except Exception as e:
        return f"You're annoying and broke my brain. Its currently " +str(temp) + " degrees. Figure it out yourself."
            
            
