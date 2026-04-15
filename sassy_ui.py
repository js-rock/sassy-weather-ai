import streamlit as st
import random
import asyncio
import os
import json
import requests
import base64
import torch
import whisper
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from streamlit_mic_recorder import mic_recorder

# --- MASTER PIPELINE IMPORTS ---
from weather_api import get_weather_data
from sanitizer import sanitize_city
from llm_brain import extract_city_from_text, user_text_error, get_ai_response
from weather_utils import (
    get_daily_maxes,
    determine_target_date,
    calculate_wind_chill
)
from voice_utils import generate_speech_as_b64, get_sassy_voice_html

load_dotenv()

# ==========================================
# SESSION STATE - INITIALIZE
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_city" not in st.session_state:
    st.session_state.last_city = None
if "current_persona" not in st.session_state:
    st.session_state.current_persona = "Sassy"

# --- WHISPER INITIALIZATION (Optimized for RTX 3090) ---
if "whisper_model" not in st.session_state:
    with st.spinner("Waking up the 3090..."):
        # Corrected the typo: cuda.is_available()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # Using 'base' for speed, but your 3090 could easily handle 'medium' if you wanted
        st.session_state.whisper_model = whisper.load_model("base", device=device)

# ============
# UI CONFIG
# ============
st.set_page_config(page_title="Sassy Weather", page_icon="🌤️", layout="centered")

# --- VIDEO ASSET PATHS (ComfyUI Renders) ---
VIDEO_ASSETS = {
    "hot": "assets/tabby_hot.mp4",
    "rain": "assets/tabby_rain.mp4",
    "cold": "assets/tabby_cold.mp4",
    "windy": "assets/tabby_wind.mp4",
    "cloudy": "assets/tabby_cloudy.mp4", 
    "default": "assets/tabby_sun.mp4"    
}

st.markdown("""
            <style>
            .stApp { 
                max-width: 450px; 
                margin: 0 auto; 
                border: 1px solid #333; 
                border-radius: 30px; 
                padding: 10px; 
                background-color: #0e1117; 
            }
            
            /* KEYFRAMES FOR ANIMATION */
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes fadeOutOverlay {
                0% { opacity: 1; visibility: visible; }
                100% { opacity: 0; visibility: hidden; }
            }

            @keyframes slideInRight {
                from { 
                    opacity: 0; 
                    transform: translateX(100px); 
                }
                to { 
                    opacity: 1; 
                    transform: translateX(0); 
                }
            }

            @keyframes pulseMarker {
                0% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.7; transform: scale(1.1); }
                100% { opacity: 1; transform: scale(1); }
            }

            /* Video Loop Fade: 5s loop with black dip */
            @keyframes videoLoopFade {
                0% { opacity: 0; } 
                5% { opacity: 0; } 
                15% { opacity: 0.6; } 
                85% { opacity: 0.6; } 
                95% { opacity: 0; } 
                100% { opacity: 0; } 
            }

            .weather-card {
                position: relative;
                overflow: hidden;
                background: #000000; /* OLED-friendly true black fallback */
                padding: 24px;
                border-radius: 24px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                margin-top: 10px;
                z-index: 1;
                color: white;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
                animation: fadeIn 0.8s ease-in-out forwards;
            }

            .weather-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: #0e1117; 
                z-index: 10;
                pointer-events: none;
                animation: fadeOutOverlay 0.6s ease-out 0.2s forwards;
            }

            .dashboard-slide-layer {
                position: relative; 
                z-index: 2;
                opacity: 0; 
                animation: slideInRight 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) 0.8s forwards;
            }

            .video-bg {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
                z-index: -1;
                opacity: 0.6;
                border-radius: 24px;
                background-color: black;
                animation: videoLoopFade 5s infinite;
            }

            .header-section { 
                margin-bottom: 20px; 
                display: flex;
                flex-direction: column;
                gap: 8px;
            }

            .header-row {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            /* Improved fixed width wrapper with better centering */
            .icon-fixed-width {
                display: flex;
                justify-content: center;
                align-items: center;
                width: 32px; 
                height: 32px;
                flex-shrink: 0;
                font-size: 1.4rem; 
            }

            .location-marker { 
                animation: pulseMarker 2s infinite ease-in-out; 
            }

            .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
            
            .metric-box { 
                background: rgba(0, 0, 0, 0.3); /* Darkened opacity to match results */
                padding: 12px; 
                border-radius: 12px; 
                backdrop-filter: blur(4px); 
                border: 1px solid rgba(255, 255, 255, 0.05); 
                text-align: center; /* Centering content */
            }
            
            .metric-label { font-size: 0.85rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8; margin-bottom: 4px; }
            .metric-value { font-size: 1.7rem; font-weight: 800; color: #00ffcc; text-shadow: 1px 1px 2px black; }
            
            .dashboard-info-flat { 
                background: rgba(0, 0, 0, 0.3); 
                padding: 12px 15px; 
                border-radius: 15px; 
                font-family: 'Courier New', Courier, monospace; 
                border-left: 4px solid #00ffcc; 
                font-size: 0.82rem; /* Scaled down from 0.9rem to prevent wrapping */
                color: #f0f0f0; 
                line-height: 1.5; 
                text-shadow: 1px 1px 2px black; 
            }
            </style>
            """, unsafe_allow_html=True)

# ==============================
# INTRODUCING SASSY TABBY CAT
# ==============================
def render_tabby_video(state="default"):
    """Helper to render the ComfyUI video background."""
    video_path = VIDEO_ASSETS.get(state, VIDEO_ASSETS["default"])
    if os.path.exists(video_path):
        with open(video_path, "rb") as f:
            video_bytes = f.read()
            video_b64 = base64.b64encode(video_bytes).decode()
        return f'<video class="video-bg" autoplay loop muted playsinline><source src="data:video/mp4;base64,{video_b64}" type="video/mp4"></video>'
    return ""

# ==============================
# TRANSCRIBE VOICE INPUT
# ==============================
def transcribe_audio(audio_bytes):
    if not audio_bytes:
        return None
    
    ffmpeg_bin_path = r"C:\ffmpeg"
    if ffmpeg_bin_path not in os.environ["PATH"] :
        os.environ["PATH"] += os.pathsep + ffmpeg_bin_path
    
    temp_filename = f"temp_voice_{os.getpid()}.wav"
    
    try:
        with open (temp_filename, "wb") as f:
            f.write(audio_bytes)

        # Added "What shall I wear" and "outfit" to the prompt context.
        # This steers Whisper away from aggressive sounding hallucinations like "Watch your life where".
        weather_context_prompt = (
            "Sassy, weather forecast, city names, temperature, humidity, rain chance, "
            "tomorrow, Sunday, what shall I wear, outfit suggestions, jacket, umbrella."
        )

        use_fp16 = torch.cuda.is_available()
        with torch.inference_mode():
            result = st.session_state.whisper_model.transcribe(
                temp_filename,
                fp16=use_fp16,
                initial_prompt=weather_context_prompt
                )
        return result.get("text", "").strip()
    except Exception as e:
        st.error(f"Whisper error: {e}")
        return None
    finally:
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except Exception as cleanup_error:
                print(f"Failed to delete temp whisper file: {cleanup_error}")

# ==============================
# SIDEBAR FOR PERSONAS
# ==============================
with st.sidebar:
    st.header("⚙️ Settings")
    persona_options = ["Sassy", "Classy", "Noob Photographer"]
    active_persona = st.selectbox("AI Persona", persona_options, index=persona_options.index(st.session_state.current_persona))
    if active_persona != st.session_state.current_persona:
        st.session_state.current_persona = active_persona
        st.session_state.messages = [] 
        st.rerun()
    voice_map = {"Sassy": "en-US-AvaNeural", "Classy": "en-GB-RyanNeural", "Noob Photographer": "en-AU-WilliamNeural"}
    target_voice = voice_map.get(active_persona)
    if st.button("Clear All"):
        st.session_state.last_city = None
        st.session_state.messages = []
        st.rerun()

# =============
# MAIN LOGIC
# =============
st.title("💅 Sassy Weather")

# ========================
# --- MIC RECORDING UI ---
# ========================
st.markdown('<div class="mic-container">', unsafe_allow_html=True)
audio_data = mic_recorder(
    start_prompt="🎤 Start Talking",
    stop_prompt="🛑 Stop & Process",
    key='recorder'
)
st.markdown('</div>', unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ====================================
# --- HANDLE INPUT (Voice or Text) ---
# ====================================
prompt_text = st.chat_input("Ask about the weather...")
voice_text = None

if audio_data:
    with st.spinner("3090 is transcribing..."):
        voice_text = transcribe_audio(audio_data['bytes'])

# Combine logic: if voice exists, use it; otherwise use text input
final_prompt = voice_text or prompt_text

if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    with st.spinner("Consulting the clouds..."):
        current_city = extract_city_from_text(final_prompt, st.session_state.last_city)
        validated_city = sanitize_city(current_city) or sanitize_city(final_prompt.strip())

        if validated_city:
            st.session_state.last_city = validated_city
            data = get_weather_data(validated_city)

            if isinstance(data, dict) and 'list' in data:
                offset_seconds = data['city'].get('timezone', 0)
                city_data = data.get('city', {})
                live_wind_speed = round(float(data['list'][0]['wind']['speed']), 1)
                live_wind_deg = data['list'][0]['wind'].get('deg', 0)
                utc_sunset = datetime.fromtimestamp(data['city']['sunset'], timezone.utc)
                local_sunset = utc_sunset + timedelta(seconds=offset_seconds)
                sunset_time = local_sunset.strftime('%I:%M %p')
                processed_daily_data = get_daily_maxes(data)
                display_date_str, target_day = determine_target_date(final_prompt, list(processed_daily_data.keys()))
                stats = processed_daily_data.get(display_date_str)
                
                if stats:
                    temp_val = round(stats.get('temp', 0), 1)
                    rain_chance = int(stats.get('pop', 0) * 100)
                    humidity = stats.get('humidity', 0)
                    sky_condition = stats.get('condition', 'Unknown').capitalize()
                    
                    try:
                        date_obj = datetime.strptime(display_date_str, '%Y-%m-%d')
                        formatted_date = date_obj.strftime('%d/%m/%Y')
                    except:
                        formatted_date = display_date_str

                    # --- ENHANCED MOOD DETECTION (Priority Stack) ---
                    if rain_chance > 20 or "rain" in sky_condition.lower():
                        mood = "rain"
                    elif temp_val > 28:
                        mood = "hot"
                    elif temp_val < 13:
                        mood = "cold"
                    elif live_wind_speed > 8:
                        mood = "windy"
                    elif any(word in sky_condition.lower() for word in ["overcast", "cloud", "mist", "fog"]):
                        mood = "cloudy"
                    else:
                        mood = "default"
                    
                    wind_chill_context = calculate_wind_chill(temp_val, live_wind_speed, live_wind_deg)

                    full_card_html = f'''
                    <div class="weather-card">
                        <div class="weather-overlay"></div>
                        {render_tabby_video(mood)}
                        <div class="dashboard-slide-layer">
                            <div class="header-section">
                                <div class="header-row">
                                    <div class="icon-fixed-width location-marker">📍</div>
                                    <div style="font-size: 1.6rem; font-weight: 900; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.9); line-height: 1.1; letter-spacing: 0.5px;">
                                        {validated_city.upper()}
                                    </div>
                                </div>
                                <div class="header-row">
                                    <div class="icon-fixed-width">📅</div>
                                    <div style="font-size: 1.1rem; font-weight: 700; text-shadow: 1px 1px 3px rgba(0,0,0,0.9); color: #ddd; line-height: 1.1;">
                                        {target_day.upper()} ({formatted_date})
                                    </div>
                                </div>
                            </div>
                            <div class="metrics-grid">
                                <div class="metric-box">
                                    <div class="metric-label">🌡️ High</div>
                                    <div class="metric-value">{temp_val}°C</div>
                                </div>
                                <div class="metric-box">
                                    <div class="metric-label">🥵 Humidity</div>
                                    <div class="metric-value">{humidity}%</div>
                                </div>
                            </div>
                            <div class="dashboard-info-flat">
                                🌧️ <b>RAIN:</b> {rain_chance}% chance<br>
                                ☁️ <b>SKY:</b> {sky_condition}<br>
                                💨 <b>WIND:</b> {live_wind_speed} m/s ({wind_chill_context})<br>
                                🌅 <b>SUNSET:</b> {sunset_time}
                            </div>
                        </div>
                    </div>
                    '''
                    st.html(full_card_html)
                    st.divider()

                    with st.chat_message("assistant"):
                        ai_text, _ = get_ai_response(active_persona, validated_city, f"Max {temp_val}C, Rain {rain_chance}%, Sky {sky_condition}, Wind {live_wind_speed} {wind_chill_context}", sunset_time, final_prompt, temp_val)
                        st.write(ai_text)
                        audio_b64 = asyncio.run(generate_speech_as_b64(ai_text, target_voice))
                        st.markdown(get_sassy_voice_html(audio_b64), unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": ai_text})
            else:
                st.error("City not found, genius.")
        else:
            st.error(random.choice(user_text_error))