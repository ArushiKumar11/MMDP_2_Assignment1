"""
IndianWeatherPulse - Utility Functions
This script contains helper functions for data analysis and processing.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

DATA_DIR = "../indian_weather_data"
MASTER_FILE = f"{DATA_DIR}/IndianWeatherPulse_Master.csv"

def load_master_dataset():
    """Load the master dataset if it exists"""
    if not os.path.exists(MASTER_FILE):
        print("Master dataset not found. Run data collection first.")
        return None
    
    df = pd.read_csv(MASTER_FILE)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def get_city_stats(city_name):
    """Get statistical summary for a specific city"""
    df = load_master_dataset()
    if df is None:
        return None
    
    city_data = df[df['city'] == city_name]
    if city_data.empty:
        print(f"No data found for {city_name}")
        return None
    
    # Calculate statistics
    stats = {
        'avg_temperature': city_data['temperature'].mean(),
        'min_temperature': city_data['temperature'].min(),
        'max_temperature': city_data['temperature'].max(),
        'avg_humidity': city_data['humidity'].mean(),
        'avg_wind_speed': city_data['wind_speed'].mean(),
        'data_start_date': city_data['timestamp'].min(),
        'data_end_date': city_data['timestamp'].max(),
        'total_records': len(city_data)
    }
    
    return stats

def detect_weather_anomalies(threshold=2.0):
    """Detect temperature anomalies across cities"""
    df = load_master_dataset()
    if df is None:
        return None
    
    anomalies = []
    
    # Calculate mean and standard deviation for each city
    for city in df['city'].unique():
        city_data = df[df['city'] == city]
        if len(city_data) < 5:  # Need enough data for meaningful statistics
            continue
            
        city_mean = city_data['temperature'].mean()
        city_std = city_data['temperature'].std()
        
        # Find anomalies (temperatures more than threshold standard deviations from mean)
        city_anomalies = city_data[abs(city_data['temperature'] - city_mean) > threshold * city_std]
        
        for _, row in city_anomalies.iterrows():
            anomalies.append({
                'city': city,
                'timestamp': row['timestamp'],
                'temperature': row['temperature'],
                'zscore': (row['temperature'] - city_mean) / city_std
            })
    
    return pd.DataFrame(anomalies)

def compare_cities(city1, city2):
    """Compare weather patterns between two cities"""
    df = load_master_dataset()
    if df is None:
        return None
    
    city1_data = df[df['city'] == city1]
    city2_data = df[df['city'] == city2]
    
    if city1_data.empty or city2_data.empty:
        print(f"Insufficient data for comparison")
        return None
    
    # Get overlapping dates
    common_dates = set(city1_data['timestamp'].dt.date).intersection(set(city2_data['timestamp'].dt.date))
    
    if not common_dates:
        print("No overlapping dates for comparison")
        return None
    
    # Filter for common dates
    city1_filtered = city1_data[city1_data['timestamp'].dt.date.isin(common_dates)]
    city2_filtered = city2_data[city2_data['timestamp'].dt.date.isin(common_dates)]
    
    # Calculate comparison metrics
    comparison = {
        'avg_temp_diff': city1_filtered['temperature'].mean() - city2_filtered['temperature'].mean(),
        'avg_humidity_diff': city1_filtered['humidity'].mean() - city2_filtered['humidity'].mean(),
        'avg_wind_diff': city1_filtered['wind_speed'].mean() - city2_filtered['wind_speed'].mean(),
        'correlation': city1_filtered['temperature'].corr(city2_filtered['temperature']),
        'common_dates_count': len(common_dates)
    }
    
    return comparison

def get_seasonal_patterns(city_name=None):
    """Analyze seasonal weather patterns"""
    df = load_master_dataset()
    if df is None:
        return None
    
    # Filter by city if specified
    if city_name:
        df = df[df['city'] == city_name]
        if df.empty:
            print(f"No data found for {city_name}")
            return None
    
    # Add season column
    df['month'] = df['timestamp'].dt.month
    
    # Define seasons (for Northern Hemisphere)
    df['season'] = pd.cut(
        df['month'],
        bins=[0, 2, 5, 8, 11, 12],
        labels=['Winter', 'Spring', 'Summer', 'Autumn', 'Winter'],
        ordered=False
    )
    
    # Calculate seasonal averages
    seasonal_data = df.groupby(['city', 'season']).agg({
        'temperature': 'mean',
        'humidity': 'mean',
        'wind_speed': 'mean',
        'precipitation': 'mean'
    }).reset_index()
    
    return seasonal_data