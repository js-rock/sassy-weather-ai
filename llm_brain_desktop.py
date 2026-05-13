# =================================================================
# SASSY WEATHER AI - LLM_BRAIN CONTROL SUITE
# =================================================================
import os
import sys
from llama_cpp import Llama  # Note: Capital 'L' for Llama class

# 1. Model Path
MODEL_PATH = os.path.join("assets", "models", "Llama-3.2-3B-Instruct-Q4_K_M.gguf")

# =================================================================
# AI_Model - Configured for Desktop (RTX 3090)
# =================================================================
# Initialize the Brain
# CPU ONLY (Universal/Cross-Platform)
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_gpu_layers=0,  # Set to 0 for CPU, or -1 for all layers on GPU
    verbose=False
)

# =================================================================
# THE TEXT LOADER AKA R.A.G.
# =================================================================
def load_text_file(folder, filename):
    """RAG: Safely reads text files from the personas directory"""
    filepath = os.path.join(folder, filename)
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read().strip()
    except Exception as e:
        print(f"Error loading {filename}: {e}")
    return ""

# =================================================================
# LOCATION LOGIC
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
    1. If the user asks for a day beyond the 5 days from today, return: out_of_scope
    2. If the user mentions a specific NEW city, return that name.
    3. SANITIZE TYPOS: (e.g., 'Sydneey' -> 'Sydney').
    4. If the user asks a follow-up (like 'is it raining?'), you MUST return PREVIOUS CITY: {last_city}.
    5. Return ONLY the city name, 'out_of_scope', or 'none'. No sentences.
    """

    # Build Llama 3.2 Prompt Format
    full_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{extraction_prompt}<|eot_id|>"
    full_prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{user_input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"

    try:
        response = llm(
            full_prompt,
            max_tokens=20,
            stop=["<|eot_id|>"],
            echo=False
        )
        
        result = response['choices'][0]['text'].strip().replace(".", "")
        print(f"DEBUG: AI extracted '{result}' from input using context '{last_city}'")
        
        if result.lower() == "none" or not result:
            return last_city
        return result

    except Exception as e:
        print(f"Error in extraction: {e}")
        return last_city

# =================== 
# AI PERSONAS VIA RAG
# ===================
def get_ai_response(persona_name, city_name, weather_summary, sunset_time, user_query, actual_temp):
    # 1. Retrieval
    safe_persona_name = persona_name.lower().replace(" ", "_")
    persona_bio = load_text_file("personas", f"{safe_persona_name}.txt")
    global_rules = load_text_file("personas", "rules.txt")

    # 2. Build the Prompt
    system_message = f"{persona_bio}\n\nGLOBAL RULES:\n{global_rules}"
    
    full_prompt = f"<|start_header_id|>system<|end_header_id|>\n\n{system_message}<|eot_id|>"
    full_prompt += f"<|start_header_id|>user<|end_header_id|>\n\n"
    full_prompt += f"CONTEXT: {city_name}, {actual_temp}°C, {weather_summary}, Sunset: {sunset_time}\n"
    full_prompt += f"USER QUERY: {user_query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"

    try:
        response = llm(
            full_prompt,
            max_tokens=128,
            stop=["<|eot_id|>", "USER:"],
            echo=False
        )
        
        clean_text = response['choices'][0]['text'].strip()
        clean_text = clean_text.replace("*", "").replace("(", "").replace(")", "")
        return clean_text, None

    except Exception as e:
        return f"Ugh, my brain fried. Just look out the window. Error: {e}", None

# =================================================================
# USER CITY INPUT ERROR CATCH
# =================================================================
user_text_error = [
    "I don't speak moron. Give me a real destination.",
    "Is that even a language? Try typing an actual city.",
    "Your brain must be broken. Use your words... and a map.",
    "You must be on drugs. Please input a location."
]
