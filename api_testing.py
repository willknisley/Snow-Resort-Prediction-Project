import requests 
from datetime import datetime, timedelta
import pandas as pd

with open ("api_key.txt", "r") as f:
    api_key = f.read().strip()

brighton_url = f"http://api.openweathermap.org/geo/1.0/direct?q=Brighton,UT,US&limit=1&appid={api_key}"

response = requests.get(brighton_url)

if response.status_code == 200:
    data = response.json()

    if data:
        lat = data[0]['lat']
        lon = data[0]['lon']

        print(f"Latitude: {lat}")
        print(f"Longitude: {lon}")

        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)

        start = int(start_time.timestamp())
        end = int(end_time.timestamp())
        
        print(f"Start: {start} ({start_time})")
        print(f"End: {end} ({end_time})")

        history_url = f"https://history.openweathermap.org/data/2.5/history/city?lat={lat}&lon={lon}&type=hour&start={start}&end={end}&appid={api_key}"

        history_response = requests.get(history_url)

        if history_response.status_code == 200:
            history_data = history_response.json()

            df = pd.DataFrame(history_data['list'])
            print(df.head)
        else:
            print(f"Error: {history_response.status_code}")
            print(history_response.text)
    print(data)
else:
    print(f"Error: {response.status_code}")
    print(response.text)