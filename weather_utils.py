from datetime import datetime

def get_daily_maxes(data):
    # ----------------------------------------------------------------------------
    # PROCESS RAW OPENWEATHER JSON 
    # ----------------------------------------------------------------------------
    daily_maxes = {}
    for item in data['list']:
        date = item['dt_txt'].split(' ')[0]
        temp = item['main']['temp'] # Using 'temp' for accuracy
        humidity = item['main']['humidity']
        desc = item['weather'][0]['description']

        if date not in daily_maxes or temp > daily_maxes[date]['temp']:
            daily_maxes[date] = {'temp': temp, 'condition': desc, 'humidity': humidity}
    
    return daily_maxes

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