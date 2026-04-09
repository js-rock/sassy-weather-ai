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
def calculate_wind_chill(temp, wind_speed, *args):
    # If the 3rd argument (index 0 of args) exists, it's our wind_deg
    wind_deg = args[0] if args else None
    """
    Calculates wind chill for temperatures <= 10°C and 
    converts degrees to compass directions.
    """
    # 1. Direction Logic
    direction = ""
    if wind_deg is not None:
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        idx = round(wind_deg / 45) % 8
        compass = directions[idx]
        
        # Sassy flavor for directions
        if compass == "S": direction = "Southerly "
        elif compass == "N": direction = "Northerly "
        elif compass == "W": direction = "Westerly "
        elif compass == "E": direction = "Easterly "
        else: direction = f"{compass} "

    # 2. Chill Logic
    if temp <= 10 and wind_speed > 4.8:
        chill = 13.12 + 0.6215 * temp - 11.37 * (wind_speed ** 0.16) + 0.3965 * temp * (wind_speed ** 0.16)
        return f"{direction}Feels like {round(chill, 1)}°C"
    
    return f"{direction}Breezy" if wind_speed > 5 else f"{direction}Calm-ish"



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
        summary += f"{day}: {info['temp']}°C ({info['condition']}).\n\n "
    return summary.strip()