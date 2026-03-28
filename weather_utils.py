from datetime import datetime, timezone

def get_daily_maxes(data):
    daily_maxes = {}
    
    # Process all data points
    for item in data['list']:
        date = item['dt_txt'].split(' ')[0]
        temp = item['main']['temp']
        humidity = item['main']['humidity']
        desc = item['weather'][0]['description']

        if date not in daily_maxes or temp > daily_maxes[date]['temp']:
            daily_maxes[date] = {'temp': temp, 'condition': desc, 'humidity': humidity}
    
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