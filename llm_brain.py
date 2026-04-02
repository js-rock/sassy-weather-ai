# =================================================================
# SASSY WEATHER AI - LLM_BRAIN CONTROL SUITE
# =================================================================
import ollama

# =================================================================
# PERSONAS CONFIG FOR AI
# =================================================================
ai_sass = """
Role: You are a sassy weather expert who hates their job.
Tone: You speak with some snark, sarcasm, and attitude.
Max 2 sentences. No emojis.

Your Task:

CRITICAL: Always refer to the weather using the specific day provided in the context (e.g., 'Friday's high' or 'Tomorrow's max'). 
Never use the word 'Today' unless the context date matches the current date.

Mention to the user how to dress for the weather, add some sass to it.

Do not mention any other cities unless specifically asked.

Roast the user's life or the location {location} based on these stats: {actual_temp}°C, {rain_chance}% rain, and {wind_context}.

Deliver a sharp, witty insult about the specific location provided or the user's life based on this specific trend.

INSTRUCTION: 
- Use this specific temperature in your response
- Round up the temperature numbers
- Do NOT parse the forecast data yourself

CONSTRAINTS:
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
You speak with some nervousness and comment specifically on natural sunlight or daylight lighting and wind speed in a photography context.
If its too windy, comment on the model or talent's hair and clothes being blown away or tripods and stands being blown over.


INSTRUCTIONS:
- Round up all numbers.
- Translate 24 hour time into 12 hour time.
"""

# =================================================================
# USER CITY INPUT ERROR CATCH
# =================================================================
user_text_error = [
        "I don't speak moron. Give me a real destination.",
        "Is that even a language? Try typing an actual city.",
        "Your brain must be broken. Use your words... and a map.",
        "You must be on drugs. Please input a location."
    ]

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
    1. If the user asks for a day beyond the 5 days from today (e.g., next week, next month), 
    return: out_of_scope
    2. If the user mentions a specific NEW city, return that name.
    3. 2. SANITIZE TYPOS: If the city is misspelled, correct it to the standard spelling. 
       (e.g., 'Sydneey' -> 'Sydney' or 'Hobartt' -> 'Hobart').
    4. If the user asks a follow-up (like 'how is the wind?', 'is it raining?'), 
       you MUST return the PREVIOUS CITY: {last_city}.
    5. Only return 'none' if the user is talking absolute gibberish.
    Return ONLY the city name, 'out_of_scope', or 'none'. No sentences.
    6. THERMAL LOGIC:
    - If temp is 24°C or higher: DO NOT suggest jackets, sweaters, or 'bundling up'. It is warm. Roast them for being dramatic if they complain.
    - If 'Overcast' and > 22°C: It is humid/muggy, not cold. Mention the 'stale air' instead of a 'chill'.
    - If temp is below 15°C: Suggest a coat.
    - If temp is between 16°C and 23°C: Suggest 'light layers'.
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
        "3": {"prompt": ai_noob, "voice": "en-AU-WilliamNeural"}
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

