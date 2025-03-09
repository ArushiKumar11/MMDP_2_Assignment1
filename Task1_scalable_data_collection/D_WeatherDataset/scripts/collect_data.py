"""
IndianWeatherPulse - Weather Data Collection Script
This script collects historical and real-time weather data for 20 Indian cities.
"""

import os
import time
import datetime
import schedule
import requests
import pandas as pd
#from dotenv import load_dotenv

API_KEY = "925eaa7149b8031172e175a6e920a680"
DATA_DIR = "../indian_weather_data"

# List of 20 Indian cities
CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", 
    "Kolkata", "Guwahati", "Pune", "Jaipur", "Agra", 
    "Ahmedabad", "Nagpur", "Indore", "Bhubaneswar", "Panaji", 
    "Visakhapatnam", "Patna", "Vadodara", "Shimla", "Amritsar"
]


# Create directory for data storage
os.makedirs(DATA_DIR, exist_ok=True)

def get_city_coordinates(city):
    """Get latitude and longitude for a city"""
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},in&limit=1&appid={API_KEY}"
    try:
        response = requests.get(geo_url)
        response.raise_for_status()
        
        geo_data = response.json()
        if not geo_data:
            print(f"No coordinates found for {city}")
            return None, None
        
        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        return lat, lon
    except requests.exceptions.RequestException as e:
        print(f"Error getting coordinates for {city}: {e}")
        return None, None

def get_current_weather(city):
    """Fetch current weather data for a given city"""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},in&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        weather_data = {
            'city': city,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data['wind']['speed'],
            'wind_direction': data['wind']['deg'],
            'weather_condition': data['weather'][0]['main'],
            'weather_description': data['weather'][0]['description'],
            'clouds': data.get('clouds', {}).get('all', 0),
            'visibility': data.get('visibility', 0) / 1000,  # Convert to km
            'data_type': 'current'
        }
        return weather_data
    except requests.exceptions.RequestException as e:
        print(f"Error getting current weather for {city}: {e}")
        return None

def get_historical_weather_open_meteo(city, days_back=30):
    """Fetch historical weather data using Open-Meteo API (free)"""
    historical_data = []
    
    # Get city coordinates
    lat, lon = get_city_coordinates(city)
    if not lat or not lon:
        return []
    
    # Calculate start and end dates
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days_back)
    
    # Format dates for API
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # Open-Meteo API call (free with no key required)
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date_str}&end_date={end_date_str}&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,apparent_temperature_mean,precipitation_sum,wind_speed_10m_max,wind_direction_10m_dominant,et0_fao_evapotranspiration&timezone=auto"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        # Process daily data
        dates = data['daily']['time']
        
        for i, date in enumerate(dates):
            weather_data = {
                'city': city,
                'timestamp': date,
                'temperature': data['daily']['temperature_2m_mean'][i],
                'temperature_max': data['daily']['temperature_2m_max'][i],
                'temperature_min': data['daily']['temperature_2m_min'][i],
                #'humidity': (data['daily']['relativehumidity_2m_max'][i] + data['daily']['relativehumidity_2m_min'][i]) / 2,
                'precipitation': data['daily']['precipitation_sum'][i],
                'feels_like':data['daily']['apparent_temperature_mean'][i],
                'wind_speed': data['daily']['wind_speed_10m_max'][i],
                'wind_direction': data['daily']['wind_direction_10m_dominant'][i],
                'humidity':data['daily']['et0_fao_evapotranspiration'][i],
                'data_type': 'historical'
            }
            historical_data.append(weather_data)
        return historical_data
    except requests.exceptions.RequestException as e:
        print(f"Error getting historical data for {city}: {e}")
        return []

def collect_and_store_data():
    """Collect both current and historical weather data for all cities and store in CSV"""
    all_data = []
    
    for city in CITIES:
        
        print(f"Collecting data for {city}...")
        
        # Get current weather
        current_data = get_current_weather(city)
        if current_data:
            all_data.append(current_data)
        
        # Get historical weather
        historical_data = get_historical_weather_open_meteo(city)
        all_data.extend(historical_data)
        
        time.sleep(5)  # To avoid hitting API rate limits
    
    # Create DataFrame and save to CSV
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    df = pd.DataFrame(all_data)
    csv_filename = f"{DATA_DIR}/IndianWeatherPulse_{timestamp}.csv"
    df.to_csv(csv_filename, index=False)
    
    print(f"Data collected and saved to {csv_filename}")
    return df

def update_master_dataset():
    """Update the master dataset with new data"""
    master_file = f"{DATA_DIR}/IndianWeatherPulse_Master.csv"
    
    # Collect new data
    new_data = collect_and_store_data()
    
    # Update or create master file
    if os.path.exists(master_file):
        master_df = pd.read_csv(master_file)
        updated_df = pd.concat([master_df, new_data], ignore_index=True)
        # Remove duplicates if any
        updated_df.drop_duplicates(subset=['city', 'timestamp'], keep='last', inplace=True)
    else:
        updated_df = new_data
    
    # Save updated master dataset
    updated_df.to_csv(master_file, index=False)
    print(f"Master dataset updated: {master_file}")
    return updated_df

def scheduled_data_collection():
    """Function to be scheduled for periodic data collection"""
    print(f"Scheduled data collection started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    update_master_dataset()
    
    # Import visualization script only when needed to avoid circular imports
    import sys
    sys.path.append('.')
    from visualize_data import create_visualizations
    
    create_visualizations()

def setup_scheduled_collection():
    """Set up scheduled data collection (twice daily)"""
    # Schedule collection at 6 AM and 6 PM
    schedule.every().day.at("06:00").do(scheduled_data_collection)
    schedule.every().day.at("18:00").do(scheduled_data_collection)
    
    print("Scheduled data collection set up. Press Ctrl+C to stop.")
    
    # Run pending tasks
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("Scheduled collection stopped by user.")

def demo_run():
    """Run a demonstration of the data collection"""
    print("Running initial data collection...")
    update_master_dataset()
    
    # Import visualization script only when needed
    import sys
    sys.path.append('.')
    from visualize_data import create_visualizations
    
    create_visualizations()
    print("\nDemonstration complete. To start scheduled collection, call setup_scheduled_collection()")

if __name__ == "__main__":
    # You can comment/uncomment these based on what you want to do
    demo_run()  # Run once for demonstration
    # setup_scheduled_collection()  # Start scheduled collection