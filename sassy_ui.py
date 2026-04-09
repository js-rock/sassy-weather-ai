import streamlit as st
import random
import asyncio
import os
import json
import requests
import base64
from dotenv import load_dotenv
from datetime import datetime

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

# ============
# UI CONFIG
# ============
st.set_page_config(page_title="Sassy Weather", page_icon="🌤️", layout="centered")

# --- VIDEO ASSET PATHS (ComfyUI Renders) ---
VIDEO_ASSETS = {
    "hot": "assets/tabby_hot.mp4",
    "rain": "assets/tabby_rain.mp4",
    "default": "assets/tabby_idle.mp4"
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
            
            /* Unified Weather Card Styling */
            .weather-card {
                position: relative;
                overflow: hidden;
                background: rgba(0, 0, 0, 0.4);
                padding: 24px;
                border-radius: 24px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                margin-top: 10px;
                z-index: 1;
                color: white;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
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
            }

            .header-section {
                margin-bottom: 20px;
            }

            /* Custom Grid for Metrics inside the Card */
            .metrics-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-bottom: 20px;
            }

            .metric-box {
                background: rgba(255, 255, 255, 0.1);
                padding: 12px;
                border-radius: 12px;
                backdrop-filter: blur(4px);
                border: 1px solid rgba(255, 255, 255, 0.05);
            }

            .metric-label {
                font-size: 0.7rem;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
                opacity: 0.8;
                margin-bottom: 4px;
            }

            .metric-value {
                font-size: 1.5rem;
                font-weight: 800;
                color: #00ffcc;
                text-shadow: 1px 1px 2px black;
            }

            .dashboard-info-flat {
                background: rgba(0, 0, 0, 0.3);
                padding: 15px;
                border-radius: 15px;
                font-family: 'Courier New', Courier, monospace;
                border-left: 4px solid #00ffcc;
                font-size: 0.9rem;
                color: #f0f0f0;
                line-height: 1.6;
                text-shadow: 1px 1px 2px black;
            }
            </style>
            """, unsafe_allow_html=True)

def render_tabby_video(state="default"):
    """Helper to render the ComfyUI video background."""
    video_path = VIDEO_ASSETS.get(state, VIDEO_ASSETS["default"])
    if os.path.exists(video_path):
        with open(video_path, "rb") as f:
            video_bytes = f.read()
            video_b64 = base64.b64encode(video_bytes).decode()
        return f'<video class="video-bg" autoplay loop muted playsinline><source src="data:video/mp4;base64,{video_b64}" type="video/mp4"></video>'
    return ""

with st.sidebar:
    st.header("⚙️ Settings")
    
    persona_options = ["Sassy", "Classy", "Noob Photographer"]
    
    active_persona = st.selectbox(
        "AI Persona", 
        persona_options,
        index=persona_options.index(st.session_state.current_persona)
    )
    
    if active_persona != st.session_state.current_persona:
        st.session_state.current_persona = active_persona
        st.session_state.messages = [] 
        st.rerun()

    voice_map = {
        "Sassy": "en-US-AvaNeural",
        "Classy": "en-GB-RyanNeural",
        "Noob Photographer": "en-AU-WilliamNeural"
    }
    target_voice = voice_map.get(active_persona)

    if st.button("Clear All"):
        st.session_state.last_city = None
        st.session_state.messages = []
        st.rerun()

st.title("💅 Sassy Weather")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about the weather..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Consulting the clouds..."):
        current_city = extract_city_from_text(prompt, st.session_state.last_city)
        validated_city = sanitize_city(current_city) or sanitize_city(prompt.strip())

        if validated_city:
            st.session_state.last_city = validated_city
            raw_response = get_weather_data(validated_city)

            if isinstance(raw_response, dict) and 'list' in raw_response:
                city_data = raw_response.get('city', {})
                live_wind_speed = round(float(raw_response['list'][0]['wind']['speed']), 1)
                live_wind_deg = raw_response['list'][0]['wind'].get('deg', 0)
                
                sunset_time = datetime.fromtimestamp(city_data.get('sunset', 0)).strftime('%I:%M %p')
                
                processed_daily_data = get_daily_maxes(raw_response)
                display_date_str, target_day = determine_target_date(prompt, list(processed_daily_data.keys()))
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

                    is_raining = rain_chance > 20 or "rain" in sky_condition.lower()
                    mood = "rain" if is_raining else ("hot" if temp_val > 28 else "default")
                    wind_chill_context = calculate_wind_chill(temp_val, live_wind_speed, live_wind_deg)

                    # THE FULLY CONSOLIDATED WINDOW
                    # We build the entire card as ONE string to ensure it renders inside one HTML frame
                    full_card_html = f'''
                    <div class="weather-card">
                        {render_tabby_video(mood)}
                        
                        <div style="position: relative; z-index: 2;">
                            <div class="header-section">
                                <h2 style="margin:0; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">📍 {validated_city.upper()}</h2>
                                <p style="margin:0; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); opacity: 0.9;">📅 {target_day.upper()} ({formatted_date})</p>
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
                        ai_text, _ = get_ai_response(
                            active_persona,
                            validated_city,
                            f"Max {temp_val}C, Rain {rain_chance}%, Sky {sky_condition}, Wind {live_wind_speed} {wind_chill_context}",
                            sunset_time,
                            prompt,
                            temp_val
                        )
                        st.write(ai_text)
                        
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        audio_b64 = loop.run_until_complete(generate_speech_as_b64(ai_text, target_voice))
                        st.markdown(get_sassy_voice_html(audio_b64), unsafe_allow_html=True)

                    st.session_state.messages.append({"role": "assistant", "content": ai_text})
            else:
                st.error("City not found, genius.")
        else:
            st.error(random.choice(user_text_error))