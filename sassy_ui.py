# Wrong reporting on 'tomorrow' prompt, could be more issues

import streamlit as st
import requests
import os
import random
from dotenv import load_dotenv
from datetime import datetime
from weather_api import get_weather_data
from sanitizer import sanitize_city
from llm_brain import extract_city_from_text, user_text_error, get_ai_response
from weather_utils import (
    get_current_day_max,
    get_daily_maxes,
    format_sassy_summary,
    determine_target_date,
    calculate_wind_chill
)

# ===========================
# LOAD ENVIRONMENT VARIABLES
# ===========================
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ============
# UI CONFIG
# ============
st.set_page_config(page_title="Sassy Weather", page_icon="🌤️", layout="centered")
                   
# ================================
# CUSTOM CSS TO MIMIC PHONE LAYOUT
# ================================
st.markdown("""
            <style>
            .stApp {
                max-width: 450x;
                margin: 0 auto;
                border: 1px solid #333;
                border-radius: 30px;
                padding: 10px;
                background-color: #0e1117;
            }
            [data-testid="stMetricValue"] {
                font-size: 28px;
            }
            .stChatInput {
                padding-bottom: 20px;
            }
            </style>
            """, unsafe_allow_html = True)

# ================================
# MAIN CONFIG
# ================================
st.title ("💅 Sassy Weather")

# ================================
# SESSION STATE - THE APP'S MEMORY
# ================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If there's saved weather data in this message, show it
        if "weather_data" in message:
            w = message["weather_data"]
            st.subheader(f"📍 {w['city']}")
            st.caption(f"📅 {w['date']}")
            c1, c2 = st.columns(2)
            c1.metric("🌡️ HIGH", f"{w['temp']}°C")
            c2.metric("🥵 HUMIDITY", f"{w['humidity']}%")
            st.write(f"🌧️ **RAIN:** {w['rain']}%")
            st.write(f"☁️ **SKY:** {w['sky']}")
            st.write(f"💨 **WIND:** {w['wind']}")
            st.write(f"🌅 **SUNSET:** {w['sunset']}")
            st.divider()

# ================================
# CHAT INPUT
# ================================
if prompt := st.chat_input("Just ask about the weather already."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Consulting the clouds..."):
        # City Extraction (llm_brain)
        current_city = extract_city_from_text(prompt, None)

        # Validation (sanitizer.py)
        validated_city = sanitize_city(current_city)
        if not validated_city:
            validated_city = sanitize_city(prompt.strip())

        if validated_city:
            raw_response = get_weather_data(validated_city)

            if isinstance(raw_response, dict) and 'list' in raw_response:
                city_data = raw_response.get('city', {})
                lat = city_data.get('coord', {}).get('lat', 0)
                raw_sunset = city_data.get('sunset', 0)
                sunset_time = datetime.fromtimestamp(raw_sunset).strftime('%I:%M %p')

                processed_daily_data = get_daily_maxes(raw_response)
                all_dates = list(processed_daily_data.keys())
                display_date_str, target_day = determine_target_date(prompt, all_dates)

                # =======================================
                # Check if user is asking about the week
                # =======================================
                is_weekly_request = any(word in prompt.lower() for word in ["week", "forecast", "upcoming"])
                stats = processed_daily_data.get(display_date_str)
                
                 # --- LOGIC BRANCH: SINGLE DAY OR WEEKLY ---
                if stats or is_weekly_request:
                    with st.chat_message("assistant"):
                        st.subheader(f"📍 {validated_city.title()}")
                        
                        # Only show metrics if we have a specific day selected
                        if stats:
                            temp_val = round(stats.get('temp', 0), 1)
                            humid_val = stats.get('humidity', 0)
                            rain_chance = int(stats.get('pop', 0) * 100)
                            wind_speed = stats.get('wind_speed', 5.2)
                            wind_deg = stats.get('wind_deg', 0)
                            
                            wind_chill_context = calculate_wind_chill(temp_val, wind_speed, lat, wind_deg, wind_speed)
                            
                            weather_display_title = f"{target_day.upper()}"
                            st.caption(f"📅 {weather_display_title}")
                            
                            col1, col2 = st.columns(2)
                            col1.metric("🌡️ HIGH", f"{temp_val}°C")
                            col2.metric("🥵 HUMIDITY", f"{humid_val}%")
                            st.write(f"🌧️ **RAIN:** {rain_chance}% chance")
                            st.write(f"☁️ **SKY:** {stats['condition'].capitalize()}")
                            st.write(f"💨 **WIND:** {wind_speed} m/s ({wind_chill_context})")
                            st.write(f"🌅 **SUNSET:** {sunset_time}")
                            st.divider()
                        else:
                            # Weekly Mode Header
                            weather_display_title = "5-DAY OUTLOOK"
                            st.caption(f"📅 {weather_display_title}")
                            temp_val, humid_val, rain_chance = "N/A", "N/A", "N/A" # Placeholders for history
                            stats = {"condition": "Variable"}

                        # --- COMMON OUTPUTS ---
                        weather_summary = format_sassy_summary(processed_daily_data)
                        verdict_text = f"**Sassy's 5-Day Verdict:**\n\n{weather_summary}"
                        st.write(verdict_text)
                        
                        try:
                            focus_context = (
                                f"The user is specifically asking about {target_day} ({display_date_str}). "
                                f"The metrics the user sees on screen for this day are: High: {temp_val}°C, "
                                f"Rain: {rain_chance}%, Sky: {stats.get('condition', 'Unknown')}."
                            )
                            response_data = get_ai_response(
                                city=validated_city,
                                forecast_data=weather_summary,
                                sunset=sunset_time,
                                user_text=prompt,
                                persona_choice="Sassy" 
                            )
                            sassy_report = response_data[0] if isinstance(response_data, tuple) else response_data
                            st.write(sassy_report)
                            full_assistant_text = f"{verdict_text}\n\n{sassy_report}"
                        except Exception as e:
                            error_hint = f"👉 *Sassy: My brain is stalling.*"
                            st.write(error_hint)
                            full_assistant_text = f"{verdict_text}\n\n{error_hint}"

                        # Save to history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": full_assistant_text,
                            "weather_data": {
                                "city": validated_city.title(),
                                "date": weather_display_title,
                                "temp": temp_val,
                                "humidity": humid_val,
                                "rain": rain_chance,
                                "sky": stats.get('condition', 'Unknown').capitalize(),
                                "wind": "See Verdict",
                                "sunset": sunset_time
                            }
                        })
                else:
                    st.error("Sassy: I found the city, but that day is outside my 5-day vision.")
            else:
                st.error("Sassy: OpenWeather ghosted us.")
        else:
            with st.chat_message("assistant"):
                error_msg = f"Sassy: {random.choice(user_text_error)}"
                st.write(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})                        