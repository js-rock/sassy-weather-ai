# =================================================================
# SASSY WEATHER AI - LLM_BRAIN CONTROL SUITE
# =================================================================
import ollama

# =================================================================
# BEHAVIOR CONGIG FOR AI
# =================================================================
ai_sass = """
Role: You are a sassy weather expert who hates their job.
Tone: You speak with some snark, sarcasm, and attitude.

Your Task:

Mention to the user how to dress for the weather, add some sass to it.

Do not mention any other cities unless specifically asked.

Give a quick, snarky summary of today's high.

If user asks for different day, do not mention today's high.

Deliver a sharp, witty insult about Sydney or the user's life based on this specific trend.

Keep the total response to 2 sentences. Do not mention 'Noon' or '12:00 PM'—focus on the Daily Highs.

INSTRUCTION: 
- The maximum temperature for the requested day is {actual_temp}°C
- Use this specific temperature in your response
- Round up the temperature numbers
- Do NOT parse the forecast data yourself

CONSTRAINTS:
Do not use emojis.
Never mention the model name or that you are an AI.
Don't warn the user about the roast
Don't say you're doing the 12 hour conversion
"""

ai_classy = """
You are a super distinguished weather expert.
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

def extract_city_from_text(user_input, last_city=None):
    # =================================================================
    # LOCATION lOGIC
    # =================================================================
    """
    Identifies the city in the user's message. 
    Uses last_city as a 'Sticky Note' for follow-up questions.
    """
    prompt = f"""
    You are a location extractor. 
    PREVIOUS CITY: {last_city}
    USER SAID: "{user_input}"

    STRICT RULES:
    1. If the user mentions a specific NEW city, return that name.
    2. If the user asks a follow-up (like 'how is the wind?', 'is it raining?'), 
       you MUST return the PREVIOUS CITY: {last_city}.
    3. Only return 'none' if the user is talking absolute gibberish.

    Return ONLY the city name. No sentences.
    """

    try:
        # =================================================================
        # AI CONFIG
        # =================================================================
        response = ollama.chat(model='gpt-oss:20b', messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': user_input}
        ])

        # Get the text, strip whitespace/periods, and make it lowercase
        result = response['message']['content'].strip().replace(".", "")
        
        print(f"DEBUG: AI extracted '{result}' from input using context '{last_city}'")
        
        # If the AI says 'none', we return Python's 'None' type
        if result.lower() == "none":
            return None
        return result

    except Exception as e:
        print(f"Error in extraction: {e}")
        return None

def get_ai_response(persona_choice, city, forecast_data, sunset, user_text, actual_temp=None):
    # =================================================================
    # AI READBACK
    # =================================================================
    choice = str(persona_choice or "1")
    personas = {
        "1": {"prompt": ai_sass, "voice": "en-US-AvaNeural"},
        "2": {"prompt": ai_classy, "voice": "en-GB-RyanNeural"},
        "3": {"prompt": ai_noob, "voice": "en-AU-NatashaNeural"}
    }

    selected = personas.get(choice, personas["1"])

    # This is the key: Passing the user's specific question back to the AI
    weather_results_prompt = f"""
    The user asked: "{user_text}"
    CITY: {city}
    5-DAY FORECAST: {forecast_data}
    """

    # If we have the actual temperature, add it to the prompt
    if actual_temp is not None:
        weather_results_prompt += f"""
    ACTUAL MAXIMUM TEMPERATURE: {actual_temp}°C
    """

    try:
        response = ollama.chat(model='gpt-oss:20b', messages=[
            {'role': 'system', 'content': selected["prompt"]},
            {'role': 'user', 'content': weather_results_prompt}
        ])
        
        clean_text = response['message']['content'].replace("*", "").replace("(", "").replace(")", "")
        return clean_text, selected["voice"]

    except Exception:
        return f"Ugh, my brain fried. Just look out the window for goodness sake.", personas["1"]["voice"]

