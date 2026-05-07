### TO DO LIST ###
# 1. [DONE] make temp not show decimal
# 2. [DONE] Fixed Video border_radius TypeError by using Container clipping
# 3. [DONE] Fixed DeprecationWarning: ft.app() -> ft.run()
# 4. [DONE] Fixed AttributeError: Alignment constants
# 5. [DONE] Fixed DeprecationWarning: ft.border.all -> ft.Border.all (Flet 0.80+)
# 6. [DONE] Fixed DeprecationWarning: ft.margin.only -> ft.Margin.only (Flet 0.80+)
# 7. [FIXED] Video black screen: Use relative paths (no 'assets/') + REQUIRES VLC 64-bit
# 8. [DONE] Added VLC Path Auto-Injection for Windows
# 9. [FIXED] VLC Temp Folder Access: Using Absolute Path resolver for media
# 10. [DONE] Added Video Looping (fv.PlaylistMode.LOOP)
# 11. [DONE] Fixed RuntimeWarning: Awaited tabby_visual.play()
# 12. [DONE] Fixed Video Update Timeout: Optimized update/play sequence
# 13. [DONE] Hardened Video Loading: Added source-check and delayed play to stop TimeoutException
# 14. [DONE] Quieted Terminal: Silenced non-fatal VLC timing logs
# 15. [SKIPPED] Video Fade: User will handle via Post-Production assets instead of UI hacks
# 16. [DONE] UI Polish: Fixed alignment inconsistencies and visual hierarchy
# 17. [FIXED] AttributeError: Moved letter_spacing to ft.TextStyle
# 18. [FIXED] UI: Fixed disappearing Temp/Humid icons by using Stack for metric boxes
# 19. [FIXED] AttributeError: Replaced problematic alignment constants with ft.Alignment(x,y)
# 20. [DONE] UI: Scaled up labels and icons for better readability
# 21. [DONE] LOGIC: Implemented Follow-up memory (state["last_city"])
# 22. [DONE] VOICE: Restored Threaded TTS (Voice logic)
# 23. [DONE] fix broken wind logic
# 24. [PENDING ]fix video not updating correctly on followup -- Seems to be a FLET limitation
# 25. add mic input 
# 26. [DONE] Sunset fix

import flet as ft
import flet_video as fv
import asyncio
import os
import sys
import pyttsx3
import threading
from datetime import datetime, timezone, timedelta

# --- VLC DLL INJECTION (FOR WINDOWS) ---
def init_vlc_env():
    if sys.platform == "win32":
        vlc_paths = [
            r"C:\Program Files\VideoLAN\VLC",
            r"C:\Program Files (x86)\VideoLAN\VLC"
        ]
        for path in vlc_paths:
            if os.path.isdir(path):
                os.environ["PATH"] = path + os.pathsep + os.environ["PATH"]
                os.environ["PYTHON_VLC_LIB_PATH"] = path
                return True
    return False

init_vlc_env()

# --- THREADED TTS LOGIC ---
def speak_text_worker(text):
    """Worker function to handle speech in a separate thread to prevent blocking the UI loop."""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
        engine.stop() 
    except Exception as e:
        print(f"TTS Thread Error: {e}")

def say_sass(text):
    """Triggers the voice output without blocking the main app logic or state updates."""
    threading.Thread(target=speak_text_worker, args=(text,), daemon=True).start()

# --- ASSET PATH RESOLVER ---
def get_media_path(filename):
    base_path = os.path.dirname(os.path.abspath(__file__))
    asset_path = os.path.join(base_path, "assets", filename)
    if os.path.exists(asset_path):
        return asset_path
    return filename 

# --- MASTER PIPELINE IMPORTS ---
from weather_api import get_weather_data
from sanitizer import sanitize_city
from llm_brain import extract_city_from_text, get_ai_response
from weather_utils import get_daily_maxes, determine_target_date

# --- APP STATE ---
state = {
    "last_city": None,
    "is_thinking": False,
    "current_video_path": None
}

async def main(page: ft.Page):
    # 1. PAGE CONFIG
    page.title = "Sassy Weather Mobile"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0e1117"
    page.vertical_alignment = ft.MainAxisAlignment.START 
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO 

    # 2. UI COMPONENTS
    location_display = ft.Text(
        value="LOCATION", 
        size=26, 
        weight=ft.FontWeight.W_900, 
        color="#00ffcc",
        style=ft.TextStyle(letter_spacing=1.2)
    )
    
    date_display = ft.Text(value="DATE: PENDING...", size=14, weight=ft.FontWeight.BOLD, color="#888888")
    temp_value = ft.Text(value="--°C", size=40, weight=ft.FontWeight.W_900, color="white")
    humidity_value = ft.Text(value="--%", size=40, weight=ft.FontWeight.W_900, color="white")
    
    rain_val = ft.Text(value="RAIN: --", size=14, weight=ft.FontWeight.W_500, color="white")
    sky_val = ft.Text(value="SKY: --", size=14, weight=ft.FontWeight.W_500, color="white")
    wind_val = ft.Text(value="WIND: --", size=14, weight=ft.FontWeight.W_500, color="white")
    sunset_val = ft.Text(value="SUNSET: --", size=14, weight=ft.FontWeight.W_500, color="white")
    
    ai_response_display = ft.Text(value="", size=15, italic=True, color="#00ffcc", text_align=ft.TextAlign.CENTER)
    status_text = ft.Text("Ready for Sass...", color="#444", size=12, italic=True)

    # 3. VIDEO COMPONENT
    initial_video = get_media_path("tabby_sun.mp4")
    state["current_video_path"] = initial_video
    
    tabby_visual = fv.Video(
        expand=True,
        fit=ft.BoxFit.COVER,
        autoplay=True,
        muted=True, 
        playlist=[fv.VideoMedia(initial_video)],
        playlist_mode=fv.PlaylistMode.LOOP
    )

    def on_video_error(e):
        if "timeout" not in str(e.data).lower():
            print(f"VIDEO ERROR: {e.data}")
            status_text.value = f"VLC Error: {e.data}"
            page.update()

    tabby_visual.on_error = on_video_error

    # 4. LAYOUT STRUCTURE
    response_card = ft.Container(
        padding=25,
        bgcolor="#161925",
        border_radius=25,
        border=ft.Border.all(1, "#2a2d3d"),
        width=380, 
        visible=False,
        shadow=ft.BoxShadow(blur_radius=20, color="#000000"),
        content=ft.Column([
            # Video Header
            ft.Container(
                content=tabby_visual, 
                height=220, 
                alignment=ft.Alignment.CENTER,
                border_radius=ft.BorderRadius.all(15),
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS, 
                margin=ft.Margin.only(bottom=15),
                border=ft.Border.all(1, "#333")
            ),
            
            # Location & Date
            ft.Column([
                location_display,
                date_display,
            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.START),
            
            ft.Divider(color="#2a2d3d", height=40),

            # Main Metrics Row
            ft.Row([
                # TEMP Box
                ft.Container(
                    expand=1,
                    height=130,
                    bgcolor="#1e2130",
                    padding=15,
                    border_radius=20,
                    border=ft.Border.all(1, "#333"),
                    content=ft.Column([
                        ft.Text("🌡️ TEMP", size=13, color="#00ffcc", weight=ft.FontWeight.BOLD, style=ft.TextStyle(letter_spacing=1)),
                        ft.Container(height=8),
                        temp_value,
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ),

                # HUMIDITY Box
                ft.Container(
                    expand=1,
                    height=130,
                    bgcolor="#1e2130",
                    padding=15,
                    border_radius=20,
                    border=ft.Border.all(1, "#333"),
                    content=ft.Column([
                        ft.Text("🥵 HUMIDITY", size=13, color="#00ffcc", weight=ft.FontWeight.BOLD, style=ft.TextStyle(letter_spacing=1)),
                        ft.Container(height=8),
                        humidity_value,
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),

            # Detailed List
            ft.Container(
                margin=ft.Margin.only(top=25, bottom=10),
                padding=ft.Padding(20, 15, 20, 15),
                bgcolor="#1e2130",
                border_radius=15,
                content=ft.Column([
                    ft.Row([ft.Text("🌧️", size=18), rain_val], spacing=15),
                    ft.Row([ft.Text("☁️", size=18), sky_val], spacing=15),
                    ft.Row([ft.Text("💨", size=18), wind_val], spacing=15),
                    ft.Row([ft.Text("🌅", size=18), sunset_val], spacing=15),
                ], spacing=15)
            ),

            ft.Divider(color="#2a2d3d", height=40),
            
            # AI Sass Area
            ft.Container(
                padding=10,
                content=ai_response_display
            )
        ], spacing=0)
    )

    async def on_process_click(e):
        if state["is_thinking"]:
            return

        user_input = city_input.value.strip()
        if not user_input:
            status_text.value = "Input something, I'm not a mind reader."
            page.update()
            return

        state["is_thinking"] = True
        status_text.value = "🔍 Analyzing Atmosphere..."
        status_text.color = "#00ffcc"
        process_btn.disabled = True
        page.update()

        try:
            # Brain extraction with memory
            extracted_city = await asyncio.to_thread(extract_city_from_text, user_input, state["last_city"])
            validated_city = sanitize_city(extracted_city)

            if not validated_city:
                status_text.value = "Not a real place. Try again."
                status_text.color = "#ff4444"
            else:
                state["last_city"] = validated_city
                weather_raw = await asyncio.to_thread(get_weather_data, validated_city)
                
                if weather_raw:
                    daily_data = get_daily_maxes(weather_raw)
                    all_dates = list(daily_data.keys())
                    
                    # Logic to find which day the user is asking about
                    res = determine_target_date(user_input, all_dates)
                    t_date = res[0] if isinstance(res, (list, tuple)) and len(res) > 0 else res
                    if not t_date or t_date not in daily_data:
                        t_date = all_dates[0]
                    
                    metrics = daily_data.get(t_date)
                    
                    display_temp = round(float(metrics.get('temp', 0))) 
                    # Corrected wind logic lookup
                    raw_wind = 0.0
                    try:
                        if isinstance(weather_raw, dict) and 'list' in weather_raw and len(weather_raw['list']) > 0:
                            raw_wind = float(weather_raw['list'][0]['wind']['speed'])
                    except (ValueError, TypeError, KeyError):
                        raw_wind = 0.0

                    
                    raw_hum = float(metrics.get('humidity', 0))
                    raw_pop = float(metrics.get('pop', 0))

                    # Video Mapping
                    condition = metrics['condition'].lower()
                    visual_file = "tabby_sun.mp4"

                    # Check conditions in order of priority
                    # Get temperature properly
                    display_temp = round(float(metrics.get('temp', 0))) 

                    # Check conditions in order of priority (most specific first)
                    if "rain" in condition or "drizzle" in condition: 
                        visual_file = "tabby_rain.mp4"
                    elif display_temp < 10:  # Cold condition
                        visual_file = "tabby_cold.mp4"
                    elif raw_wind > 7:  # Wind condition
                        visual_file = "tabby_wind.mp4"
                    elif "cloud" in condition: 
                        visual_file = "tabby_cloudy.mp4"
                    elif "clear" in condition or "sun" in condition:
                        visual_file = "tabby_sun.mp4"



                    print(f"Wind speed: {raw_wind} m/s")
                    print(f"Condition: {condition}")
                    print(f"Selected video: {visual_file}")

                    abs_visual_path = get_media_path(visual_file)

                    # Simple update - just set the playlist and hope it works
                    if abs_visual_path != state["current_video_path"]:
                        try:
                            print(f"Setting new video: {visual_file}")
                            
                            # Simple playlist update - no stop/play needed
                            tabby_visual.playlist = [fv.VideoMedia(abs_visual_path)]
                            state["current_video_path"] = abs_visual_path
                            tabby_visual.update()
                            
                            # Force page update
                            page.update()
                            
                            print("Video update completed successfully")
                            
                        except Exception as e:
                            print(f"Video update error: {e}")
                            # Continue without failing the whole process
                            pass
                    else:
                        print("No video change needed")


                    # UI Population
                    date_obj = datetime.strptime(t_date, '%Y-%m-%d')
                    location_display.value = str(validated_city).upper()
                    date_display.value = f"{date_obj.strftime('%A').upper()} • {date_obj.strftime('%b %d')}"
                    temp_value.value = f"{display_temp}°C"
                    humidity_value.value = f"{int(raw_hum)}%"
                    
                    rain_val.value = f"RAIN: {int(raw_pop * 100)}% chance"
                    sky_val.value = f"SKY: {metrics['condition']}"
                    wind_val.value = f"WIND: {round(raw_wind, 1)} m/s"
                    # Sunset logic with error handling
                    sunset_time = "SUNSET: ERROR"
                    try:
                        if isinstance(weather_raw, dict) and 'city' in weather_raw:
                            city_data = weather_raw['city']
                            
                            # Get timezone offset
                            offset_seconds = int(city_data.get('timezone', 0))
                            
                            # Get sunset timestamp
                            sunset_timestamp = int(city_data.get('sunset', 0))
                            
                            if sunset_timestamp > 0:
                                # Convert to local time
                                utc_sunset = datetime.fromtimestamp(sunset_timestamp, timezone.utc)
                                local_sunset = utc_sunset + timedelta(seconds=offset_seconds)
                                sunset_time = local_sunset.strftime('%I:%M %p')
                                sunset_time = f"SUNSET: {sunset_time}"
                    except Exception as e:
                        print(f"Error getting sunset time: {e}")
                        # Keep ERROR fallback

                    sunset_val.value = sunset_time

                    ai_text, _ = await asyncio.to_thread(
                        get_ai_response, "Sassy", validated_city, 
                        f"{display_temp}C, {metrics['condition']}, {raw_wind}m/s", "7:42 PM", user_input, display_temp
                    )
                    ai_response_display.value = ai_text
                    
                    response_card.visible = True
                    say_sass(ai_text)
                else:
                    status_text.value = "Weather API failed."
                    status_text.color = "#ff4444"

        except Exception as ex:
            status_text.value = f"System Error: {str(ex)}"
            status_text.color = "#ff4444"
        
        finally:
            state["is_thinking"] = False
            process_btn.disabled = False
            city_input.value = ""
            page.update() 

    city_input = ft.TextField(
        label="Enter Location or Ask Follow-up",
        hint_text="e.g. 'What about tomorrow?'",
        border_color="#333",
        focused_border_color="#00ffcc",
        width=300,
        on_submit=lambda e: page.run_task(on_process_click, e)
    )

    process_btn = ft.FilledButton(
        "Generate Forecast",
        icon=ft.Icons.AUTO_AWESOME, 
        on_click=lambda e: page.run_task(on_process_click, e),
        style=ft.ButtonStyle(bgcolor="#00ffcc", color="black")
    )

    page.add(
        ft.Column(
            [
                ft.Container(height=20),
                ft.Text("💅 Sassy Weather", size=28, weight=ft.FontWeight.W_900),
                city_input,
                process_btn,
                status_text,
                response_card,
            ],
            horizontal_alignment="center",
        )
    )

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")