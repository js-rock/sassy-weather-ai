### TO DO LIST ###
# 1. [DONE] make temp not show decimal
# 2. [DONE] Fixed Video border_radius TypeError by using Container clipping
# 3. [DONE] Fixed DeprecationWarning: ft.app() -> ft.run()
# 4. [DONE] Fixed AttributeError: Alignment constants
# 5. [DONE] Fixed DeprecationWarning: ft.border.all -> ft.Border.all (Flet 0.80+)
# 6. [DONE] Fixed DeprecationWarning: ft.margin.only -> ft.Margin.only (Flet 0.80+)
# 7. [OPEN] get sassy tabby videos working (Currently rendering black, pathing fix needed)
# 8. [OPEN] Voice commands needed in flet?

import flet as ft
import flet_video as fv
import asyncio
import re
import random
import os
from datetime import datetime

# --- MASTER PIPELINE IMPORTS ---
from weather_api import get_weather_data
from sanitizer import sanitize_city
from llm_brain import extract_city_from_text, get_ai_response
from weather_utils import get_daily_maxes, determine_target_date, calculate_wind_chill

# --- APP STATE ---
state = {
    "last_city": None,
    "is_thinking": False
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
    location_display = ft.Text(value="LOCATION", size=24, weight=ft.FontWeight.W_900, color="white")
    date_display = ft.Text(value="DATE: PENDING...", size=16, weight=ft.FontWeight.BOLD, color="white")
    temp_value = ft.Text(value="--°C", size=28, weight=ft.FontWeight.W_900, color="white")
    humidity_value = ft.Text(value="--%", size=28, weight=ft.FontWeight.W_900, color="white")
    
    rain_val = ft.Text(value="RAIN: --", size=14, weight=ft.FontWeight.BOLD)
    sky_val = ft.Text(value="SKY: --", size=14, weight=ft.FontWeight.BOLD)
    wind_val = ft.Text(value="WIND: --", size=14, weight=ft.FontWeight.BOLD)
    sunset_val = ft.Text(value="SUNSET: --", size=14, weight=ft.FontWeight.BOLD)
    
    ai_response_display = ft.Text(value="", size=14, italic=True, color="#00ffcc", text_align=ft.TextAlign.CENTER)
    status_text = ft.Text("Ready for Sass...", color="#00ffcc", size=14, italic=True)

    # 3. VIDEO COMPONENT
    tabby_visual = fv.Video(
        expand=True,
        fit=ft.BoxFit.COVER,
        autoplay=True,
    )

    # 4. LAYOUT STRUCTURE
    response_card = ft.Container(
        padding=25,
        bgcolor="#1e2130",
        border_radius=20,
        border=ft.Border.all(1, "#333"),
        width=380, 
        visible=False,
        content=ft.Column([
            ft.Container(
                content=tabby_visual, 
                height=200, 
                alignment=ft.Alignment.CENTER,
                border_radius=ft.BorderRadius.all(15),
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS, 
                # FIXED: Updated ft.margin.only to ft.Margin.only
                margin=ft.Margin.only(bottom=10)
            ),
            
            ft.Row([
                ft.Text("📍", size=30),
                location_display,
            ], alignment=ft.MainAxisAlignment.START, spacing=10),
            
            ft.Row([
                ft.Text("📅", size=22),
                date_display,
            ], spacing=10),
            
            ft.Divider(color="#333", height=30),

            ft.Row([
                ft.Container(
                    width=150,
                    height=125,
                    bgcolor="#161925",
                    padding=2,
                    border_radius=15,
                    border=ft.Border.all(1, "#444"),
                    content=ft.Column([
                        ft.Text("🌡️ TEMP", size=12, color="white", weight="bold"),
                        ft.Container(height=3),
                        temp_value,
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                    alignment=ft.MainAxisAlignment.START,
                    spacing=1
                    )
                ),

                ft.Container(
                    width=150,
                    height=125,
                    bgcolor="#161925",
                    padding=2,
                    border_radius=15,
                    border=ft.Border.all(1, ft.Colors.GREY_700),
                    content=ft.Column([
                        ft.Text("🥵 HUMIDITY", size=12, color="white", weight="bold"),
                        ft.Container(height=10),
                        humidity_value
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                    alignment=ft.MainAxisAlignment.START,
                    spacing=1
                    )
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),

            ft.Container(
                # FIXED: Updated ft.margin.only to ft.Margin.only
                margin=ft.Margin.only(top=20),
                content=ft.Column([
                    ft.Row([ft.Text("🌧️", size=18), rain_val], spacing=15),
                    ft.Row([ft.Text("☁️", size=18), sky_val], spacing=15),
                    ft.Row([ft.Text("💨", size=18), wind_val], spacing=15),
                    ft.Row([ft.Text("🌅", size=18), sunset_val], spacing=15),
                ], spacing=12)
            ),

            ft.Divider(color="#333", height=30),
            ai_response_display
        ], spacing=10)
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
        status_text.value = "🔍 Thinking..."
        status_text.color = "#ffcc00"
        process_btn.disabled = True
        page.update()

        try:
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
                    
                    res = determine_target_date(user_input, all_dates)
                    t_date = res[0] if isinstance(res, (list, tuple)) and len(res) > 0 else res
                    if not t_date or t_date not in daily_data:
                        t_date = all_dates[0]
                    
                    metrics = daily_data.get(t_date)
                    
                    raw_temp = float(metrics.get('temp', 0))
                    raw_wind = float(metrics.get('wind_speed', 4.5))
                    raw_hum = float(metrics.get('humidity', 0))
                    raw_pop = float(metrics.get('pop', 0))

                    # Video switching logic (paths to be adjusted tomorrow)
                    condition = metrics['condition'].lower()
                    visual_file = "tabby_sun.mp4"
                    if "rain" in condition or "drizzle" in condition:
                        visual_file = "rainy_tabby.mp4"
                    elif "cloud" in condition:
                        visual_file = "cloudy_tabby.mp4"
                    
                    tabby_visual.src = visual_file
                    tabby_visual.update()

                    date_obj = datetime.strptime(t_date, '%Y-%m-%d')
                    day_str = date_obj.strftime('%A').upper()
                    short_date = date_obj.strftime('%b %d')
                    
                    location_display.value = str(validated_city).upper()
                    date_display.value = f"{day_str} ({short_date})"
                    temp_value.value = f"{int(raw_temp)}°C"
                    humidity_value.value = f"{int(raw_hum)}%"
                    
                    rain_val.value = f"RAIN: {int(raw_pop * 100)}% chance"
                    sky_val.value = f"SKY: {metrics['condition']}"
                    wind_val.value = f"WIND: {raw_wind} m/s"
                    sunset_val.value = "SUNSET: 7:42 PM"

                    ai_text, _ = await asyncio.to_thread(
                        get_ai_response, "Sassy", validated_city, 
                        f"{raw_temp}C, {metrics['condition']}", "7:42 PM", user_input, raw_temp
                    )
                    ai_response_display.value = ai_text
                    
                    response_card.visible = True
                    status_text.value = "Success."
                    status_text.color = "#00ffcc"
                else:
                    status_text.value = "Weather API failed."
                    status_text.color = "#ff4444"

        except Exception as ex:
            status_text.value = f"Error: {str(ex)}"
            status_text.color = "#ff4444"
        
        finally:
            state["is_thinking"] = False
            process_btn.disabled = False
            city_input.value = ""
            page.update() 

    city_input = ft.TextField(
        label="Where are you 'suffering'?",
        border_color="#333",
        focused_border_color="#00ffcc",
        width=300,
        on_submit=lambda e: page.run_task(on_process_click, e)
    )

    process_btn = ft.FilledButton(
        "Get Weather",
        icon=ft.Icons.FLASH_ON, 
        on_click=lambda e: page.run_task(on_process_click, e),
        style=ft.ButtonStyle(
            color="black",
            bgcolor="#00ffcc",
            shape=ft.RoundedRectangleBorder(radius=10),
        )
    )

    page.add(
        ft.Column(
            [
                ft.Text("💅 Sassy Weather", size=32, weight=ft.FontWeight.W_900),
                ft.Divider(height=10, color="transparent"),
                city_input,
                process_btn,
                status_text,
                ft.Divider(height=10, color="transparent"),
                response_card
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")