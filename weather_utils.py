from datetime import datetime, timezone
import math

# ================================================
# Parses user input to determine correct date
# ================================================
def determine_target_date(user_text, all_dates):
    user_text = user_text.lower()
    today = datetime.now().strftime('%Y-%m-%d')

    # Handle "Tomorrow"
    if "tomorrow" in user_text:
        target_day = "Tomorrow"
        if len(all_dates) > 1:
            display_date = all_dates[1]
        else:
            display_date = all_dates[0]
            
    elif any(day.lower() in user_text for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]):
        user_day = None
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            if day.lower() in user_text:
                user_day = day
                break
        
        if user_day:
            target_day = user_day
            for date in all_dates:
                day_name = datetime.strptime(date, '%Y-%m-%d').strftime('%A')
                if day_name.lower() == user_day.lower():
                    display_date = date
                    break
            else:
                display_date = today
        else:
            display_date = today
            target_day = "Today"
            
    else:
        # Default to today
        display_date = today
        target_day = "Today"
    
    return display_date, target_day

    # Default to Today
    # return Today, "Today"                

# =================================
# Weather calcs
# =================================
def calculate_wind_chill(temp_c, wind_kph, lat, deg, speed):
    if speed < 2: 
        return "Calm"

    # Southern Hemisphere (Sydney)
    if lat < 0:
        # Widened the window: 130 to 230 degrees covers more of the "South"
        if 130 <= deg <= 230:
            return "a chilly Southerly from the ocean"
        elif 150 <= deg <= 210 and speed > 5:
            return "a biting Southerly buster from Antarctica"
        elif 270 <= deg <= 330:
            return "a hot Westerly from the desert"
            
    # Northern Hemisphere
    else:
        if 330 <= deg or deg <= 30:
            return "a freezing Northerly from Siberia"
    
    # NEW: If it's coming from the South but not in the "Buster" range
    if lat < 0 and (100 < deg < 260):
        return "a cool breeze from the South"
        
    return "a standard breeze"


def get_daily_maxes(data):
    daily_maxes = {}
    
    # Process all data points
    for item in data['list']:
        date = item['dt_txt'].split(' ')[0]
        temp = item['main']['temp']
        humidity = item['main']['humidity']
        desc = item['weather'][0]['description']
        pop = item.get('pop', 0)

        if date not in daily_maxes or temp > daily_maxes[date]['temp']:
            daily_maxes[date] = {'temp': temp, 'condition': desc, 'humidity': humidity, 'pop': pop}
    
    return daily_maxes

def get_current_day_max(daily_maxes):
    """Get the maximum temperature for today"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Return today's max if available
    if today in daily_maxes:
        return daily_maxes[today]
    else:
        # If today not in data, return the highest temperature
        # This shouldn't happen if API is working correctly
        if daily_maxes:
            max_temp = max(daily_maxes.items(), key=lambda x: x[1]['temp'])
            return max_temp[1]
        return None



def format_sassy_summary(daily_maxes):
    # ----------------------------------------------------------------------------
    # CONVERT DICTIONARY INTO STRING
    # ----------------------------------------------------------------------------
    """Turns the dictionary into a simple string for the AI to read."""
    summary = ""
    for date, info in list(daily_maxes.items())[:5]:
        day = datetime.strptime(date, '%Y-%m-%d').strftime('%A')
        summary += f"{day}: {info['temp']}°C ({info['condition']}). "
    return summary