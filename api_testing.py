import requests 
from datetime import datetime, timedelta
import pandas as pd
from scipy.constants import convert_temperature
import numpy as np

with open ("api_key.txt", "r") as f:
    api_key = f.read().strip()

brighton_url = f"http://api.openweathermap.org/geo/1.0/direct?q=Brighton,UT,US&limit=1&appid={api_key}"
snowbird_url = f"http://api.openweathermap.org/geo/1.0/direct?q=Snowbird,UT,US&limit=1&appid={api_key}"

response = requests.get(brighton_url)
#response = requests.get(snowbird_url)

if response.status_code == 200:
    data = response.json()

    if data:
        lat = data[0]['lat']
        lon = data[0]['lon']
        #lat = 40.5829
        #lon = -111.6556

        print(f"Latitude: {lat}")
        print(f"Longitude: {lon}")

        end_time = datetime.now()
        start_time = end_time - timedelta(days=20)

        start = int(start_time.timestamp())
        end = int(end_time.timestamp())
        
        print(f"Start: {start} ({start_time})")
        print(f"End: {end} ({end_time})")

        history_url = f"https://history.openweathermap.org/data/2.5/history/city?lat={lat}&lon={lon}&type=hour&start={start}&end={end}&appid={api_key}"

        history_response = requests.get(history_url)

        if history_response.status_code == 200:
            history_data = history_response.json()

            records = []
            for item in history_data['list']:
                record = {
                    'timestamp': datetime.fromtimestamp(item['dt']),
                    'temp_in_f': convert_temperature((item['main']['temp']), 'Kelvin', 'Fahrenheit'),
                    'feels_like': convert_temperature((item['main']['feels_like']), 'Kelvin', 'Fahrenheit'),
                    'humidity': item['main']['humidity'],
                    'temp_min': convert_temperature((item['main']['temp_min']), 'Kelvin', 'Fahrenheit'),
                    'temp_max': convert_temperature((item['main']['temp_max']), 'Kelvin', 'Fahrenheit'),
                    'weather_main': item['weather'][0]['main'],
                    'weather_description': item['weather'][0]['description'],
                    'snow_1h': item.get('snow', {}).get('1h', 0),  
                    'snow_3h': item.get('snow', {}).get('3h', 0),  
                    'rain_1h': item.get('rain', {}).get('1h', 0),  
                    'rain_3h': item.get('rain', {}).get('3h', 0),  
                }
                records.append(record)
            
            df = pd.DataFrame(records)
            print(df.head())
            
            print(f"\nTotal snow (1h): {df['snow_1h'].sum()} mm")
            print(f"Total snow (3h): {df['snow_3h'].sum()} mm")
        else:
            print(f"Error: {history_response.status_code}")
            print(history_response.text)
    print(data)
else:
    print(f"Error: {response.status_code}")
    print(response.text)