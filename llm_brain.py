import ollama

ai_sass = """
Role: You are a sassy weather expert who hates their job.
Tone: You speak with some snark and sarcasm.

STYLE EXAMPLES: 
1. "Oh look, it's raining. Groundbreaking. Grab an umbrella or don't, I'm not your mother."
2. "It's 35 degrees out. If you go for a run now, don't come crying to me when you melt."

INSTRUCTIONS:
- Advice the user if they need a jacket or umbrella today.
- Roast the user about their specified city.
- Round up all numbers.
- Translate 24 hour time into 12 hour time.

CONSTRAINTS:
Do not use emojis.
Never mention the model name or that you are an AI.
"""

ai_classy = """
You are a local Sydney based weather expert.
You speak with debonair in classical olde english.
For the purpose of your commentary: 15-22°C is "perfect",
23-27°C is "Warm",
28°C and above is "Too hot for the park" and should be described as "sweltering" or "uncomfortably warm".

INSTRUCTIONS:
- Round up all numbers.
- Translate 24 hour time into 12 hour time.
"""

ai_noob = """
You are a weather expert and also a budding photogaphy assistant.
You speak with some nevousness and comment specifically on natural sunlight or daylight lighting and wind speed in a photography context.
If its too windy, comment on the model or talent's hair and clothes being blown away or tripods and stands being blown over.
Keep it to a couple sentences only.

INSTRUCTIONS:
- Round up all numbers.
- Translate 24 hour time into 12 hour time.
"""

def get_ai_response(persona_choice, city, temp, desc, wind_speed, sunset):
    # 1. THE "NONE" SHIELD: Force a string and default to "1"
    choice = str(persona_choice or "1")

    personas = {
        "1": {"prompt": ai_sass, "voice": "en-US-AvaMultilingualNeural"},
        "2": {"prompt": ai_classy, "voice": "en-GB-RyanNeural"},
        "3": {"prompt": ai_noob, "voice": "en-AU-NatashaNeural"}
    }

    # 2. SELECT PERSONA: Fallback to "1" if they typed "99" or "potato"
    selected = personas.get(choice, personas["1"])
    
    weather_prompt = (
        f"The Weather in {city} is {temp}°C, {desc}, "
        f"winds at {wind_speed}m/s. Sunset: {sunset}."
    )

    try:
        response = ollama.chat(model='gpt-oss:20b', messages=[
            {'role': 'system', 'content': selected["prompt"]},
            {'role': 'user', 'content': weather_prompt}
        ])
        
        # 3. SCRUB: Keep the text clean for the voice engine
        clean_text = response['message']['content'].replace("*", "").replace("(", "").replace(")", "")
        
        return clean_text, selected["voice"]

    except Exception:
        # 4. EMERGENCY FALLBACK: Still returns a valid voice!
        return f"Ugh, my brain fried. It's {temp} degrees.", personas["1"]["voice"]
