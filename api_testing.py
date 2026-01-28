import requests 
import pandas as pd
from scipy.constants import convert_temperature
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


resorts = {
    'Brighton': {'lat': 40.5983, 'lon': -111.5837},
    'Solitude': {'lat': 40.6238, 'lon': -111.5975},
    'Snowbird': {'lat': 40.5810, 'lon': -111.6567},
    'Alta': {'lat': 40.5889, 'lon': -111.6388},
    'Deer Valley': {'lat': 40.611, 'lon': -111.4999},
    'Park City': {'lat': 40.6576, 'lon': -111.5700},
    'Snowbasin': {'lat': 41.1994, 'lon': -111.8593},
}

all_records = []
current_year = datetime.now().year


for resort_name, coords in resorts.items():
    weather_data = []

    lat = coords['lat']
    lon = coords['lon']

    for year_change in range(10):
        base_year = current_year - year_change


        for month_data in [(base_year, 12), (base_year + 1, 1), 
                    (base_year + 1, 2), (base_year + 1, 3)]:
            year, month = month_data
            start_date = datetime(year, month, 1)

            if start_date > datetime.now():
                continue
            end_date = start_date + relativedelta(months=1)
            
            if end_date > datetime.now():
                end_date = datetime.now()

            weather_data.append({
                'season': f"{base_year}-{base_year + 1}",
                'month': start_date.strftime('%B %Y'),
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            })

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
                    'resort': resort_name,
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

    resort_summary = df.groupby('resort')['snowfall_inch'].sum().sort_values(ascending=False)
    print(f"\nTotal snowfall by resort (10 years):")
    for resort, total in resort_summary.items():
        print(f"  {resort}: {total:.2f} inches")

        print(f"\nTotal snowfall by season:")
    season_summary = df.groupby('season')['snowfall_inch'].sum().sort_values(ascending=False)
    for season, total in season_summary.head(5).items():
        print(f"  {season}: {total:.2f} inches")
    
    df.to_csv('all_resorts_snow_data.csv', index=False)
    print("\nData saved to all_resorts_snow_data.csv")
else:
    print("\nNo data collected!")