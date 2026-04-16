# =================================================================
# SASSY WEATHER AI - LLM_BRAIN CONTROL SUITE
# =================================================================
import ollama
import os

# =================================================================
# AI_Model
# =================================================================
LLM_MODEL = 'gemma4:26b-a4b-it-q4_K_M'

# =================================================================
# THE TEXT LOADER AKA R.A.G.
# =================================================================
def load_text_file(folder, filename):
    """Safely reads text files from the personas directory"""
    filepath = os.path.join(folder, filename)
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read().strip()
        else:
            print(f"Warning: {filename} not found at {filepath}")
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return ""

# =================================================================
# LOCATION lOGIC
# =================================================================
def extract_city_from_text(user_input, last_city=None):
    """
    Identifies the city in the user's message. 
    Uses last_city as a 'Sticky Note' for follow-up questions.
    """
    extraction_prompt = f"""
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
    """

    try:
        # =================================================================
        # AI CONFIG
        # =================================================================
        response = ollama.chat(LLM_MODEL, messages=[
            {'role': 'system', 'content': extraction_prompt},
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
        return last_city
    
# ===================
# AI PERSONAS VIA RAG
# ===================
def get_ai_response(persona_name, city_name, weather_summary, sunset_time, user_query, actual_temp):
    """
    MODULAR RAG-LITE PIPELINE:
    1. Retrieve 'The Vibe' (persona.txt)
    2. Retrieve 'The Rules' (rules.txt - includes Thermal Logic)
    3. Augment with Weather Data
    4. Generate Response
    """

    # 1. Retrieval
    safe_persona_name = persona_name.lower().replace(" ", "_")
    persona_bio = load_text_file("personas", f"{safe_persona_name}.txt")
    global_rules = load_text_file("personas", "rules.txt")

    # 2. Augmentation
    system_message = f"{persona_bio}\n\nGLOBAL CONSTRAINTS & THERMAL LOGIC:\n{global_rules}"

# 2. Augmentation
    system_message = f"{persona_bio}\n\nGLOBAL CONSTRAINTS & THERMAL LOGIC:\n{global_rules}"

    user_context = (
        f"USER ASKED: {user_query}\n"
        f"LOCATION: {city_name}\n"
        f"TEMP: {actual_temp}°C\n"
        f"FORECAST: {weather_summary}\n"
        f"SUNSET: {sunset_time}"
    )

    try:
        response = ollama.chat(LLM_MODEL, messages=[
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': user_context}
        ])
        
        clean_text = response['message']['content'].replace("*", "").replace("(", "").replace(")", "").strip()
        return clean_text, None

    except Exception as e:
        return f"Ugh, my brain fried. Just look out the window for goodness sake. Error: {e}"
    
# =================================================================
# USER CITY INPUT ERROR CATCH
# =================================================================
user_text_error = [
        "I don't speak moron. Give me a real destination.",
        "Is that even a language? Try typing an actual city.",
        "Your brain must be broken. Use your words... and a map.",
        "You must be on drugs. Please input a location."
    ]