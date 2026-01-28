import requests 
import pandas as pd
from scipy.constants import convert_temperature
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# brighton coordinates
lat = 40.5983
lon = -111.5827


current_year = datetime.now().year
weather_data = []

for year_change in range(3):
    base_year = current_year - year_change


    for month_data in [(base_year, 12), (base_year + 1, 1), 
                (base_year + 1, 2), (base_year + 1, 3)]:
        year, month = month_data
        start_date = datetime(year, month, 1)

        if start_date > datetime.now():
            continue
        end_date = start_date + relativedelta(months=1)
        

        weather_data.append({
            'season': f"{base_year}-{base_year + 1}",
            'month': start_date.strftime('%B %Y'),
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': (end_date - relativedelta(days=1)).strftime('%Y-%m-%d')
        })

all_records = []

for weather in weather_data:
    print(f"Getting {weather['month']} (Season {weather['season']})")


    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": weather['start_date'],
        "end_date": weather['end_date'],
        "hourly": ["snowfall", "snow_depth", "temperature_2m"],
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch",
        "timezone": "America/Denver"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        if 'hourly' in data:
            hourly = data['hourly']
            
            for i in range(len(hourly['time'])):
                record = {
                    'timestamp': datetime.fromisoformat(hourly['time'][i]), 
                    'season': weather['season'],
                    'month': weather['month'],
                    'snowfall_inch': hourly['snowfall'][i] if hourly['snowfall'][i] is not None else 0,
                    'snow_depth_inch': hourly['snow_depth'][i] if hourly['snow_depth'][i] is not None else 0,
                    'temperature_f': hourly['temperature_2m'][i]
                }
                all_records.append(record)
            
            monthly_total = sum(hourly['snowfall'][i] if hourly['snowfall'][i] is not None else 0 
                              for i in range(len(hourly['snowfall'])))
            print(f"  Total snowfall: {monthly_total:.2f} inches")
        else:
            print("  No hourly data available")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if all_records:
    df = pd.DataFrame(all_records)
    print(f"\n{'='*60}")
    print(f"Total records collected: {len(df)}")
    print(f"Total snowfall (all seasons): {df['snowfall_inch'].sum():.2f} inches")
    print(df.head(10))
