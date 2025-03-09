"""
IndianWeatherPulse - Data Visualization Module
This script creates visualizations from the collected weather data.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta

DATA_DIR = "../indian_weather_data"
MASTER_FILE = f"{DATA_DIR}/IndianWeatherPulse_Master.csv"

def create_visualizations():
    """Create a set of visualizations from the master dataset"""
    if not os.path.exists(MASTER_FILE):
        print("No data available for visualization yet. Run data collection first.")
        return
    
    # Load data
    df = pd.read_csv(MASTER_FILE)
    
    # Convert timestamp to datetime 
    # Note: Keep as datetime object instead of just date for plotting
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d', errors='coerce')
    
    # Create visualizations directory
    vis_dir = f"{DATA_DIR}/visualizations"
    os.makedirs(vis_dir, exist_ok=True)
    
    # Generate different visualizations
    create_temperature_comparison(df, vis_dir)
    create_city_temperature_trend(df, vis_dir)
    create_humidity_comparison(df, vis_dir)
    create_temperature_heatmap(df, vis_dir)
    create_wind_rose(df, vis_dir)
    
    print(f"Visualizations created and saved to {vis_dir}")

def create_temperature_comparison(df, output_dir):
    """Create bar chart of current temperatures across cities"""
    plt.figure(figsize=(12, 8))
    
    # Filter for most recent current data for each city
    current_data = df[df['data_type'] == 'current']
    if current_data.empty:
        current_data = df  # Use all data if no current data available
        
    latest_data = current_data.sort_values('timestamp').groupby('city').last().reset_index()
    latest_data = latest_data.sort_values('temperature')
    
    # Create bar chart
    plt.barh(latest_data['city'], latest_data['temperature'])
    plt.xlabel('Temperature (°C)')
    plt.ylabel('City')
    plt.title('Current Temperature Across Indian Cities')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Add temperature values at the end of each bar
    for i, temp in enumerate(latest_data['temperature']):
        plt.text(temp + 0.3, i, f"{temp:.1f}°C", va='center')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/temperature_comparison.png")
    plt.close()

def create_city_temperature_trend(df, output_dir, cities=None):
    """Create line chart of temperature trends for selected cities"""
    if cities is None:
        # Default to top 5 most populated cities
        cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"]
    
    plt.figure(figsize=(14, 8))
    
    # Filter data for selected cities and sort by timestamp
    # Make a copy to avoid SettingWithCopyWarning
    city_data = df[df['city'].isin(cities)].copy().sort_values('timestamp')
    
    # Convert timestamp to datetime if not already
    if not pd.api.types.is_datetime64_dtype(city_data['timestamp']):
        city_data['timestamp'] = pd.to_datetime(city_data['timestamp'], errors='coerce')
    
    # Drop rows with NaT timestamps
    city_data = city_data.dropna(subset=['timestamp'])
    
    # Create a line for each city
    for city in cities:
        city_temps = city_data[city_data['city'] == city]
        if not city_temps.empty:
            plt.plot(city_temps['timestamp'], city_temps['temperature'], marker='o', markersize=4, label=city)
    
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.title('Temperature Trends Across Major Indian Cities')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/city_temperature_trends.png")
    plt.close()

def create_humidity_comparison(df, output_dir):
    """Create histogram of humidity distribution"""
    plt.figure(figsize=(12, 8))
    
    # Filter for data with humidity values
    humidity_data = df.dropna(subset=['humidity'])
    
    if not humidity_data.empty:
        # Create a grouped bar chart
        sns.boxplot(x='city', y='humidity', data=humidity_data)
        plt.xticks(rotation=90)
        plt.xlabel('City')
        plt.ylabel('Humidity (%)')
        plt.title('Humidity Distribution Across Indian Cities')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/humidity_comparison.png")
    
    plt.close()

def create_temperature_heatmap(df, output_dir):
    """Create heatmap showing temperature variations across cities and time"""
    # Filter for historical data which has regular timestamps
    hist_data = df[df['data_type'] == 'historical'].copy()
    
    
    hist_data['timestamp'] = pd.to_datetime(hist_data['timestamp'], format='%Y-%m-%d')
    
    # Extract date from timestamp for grouping
    hist_data['date'] = hist_data['timestamp']
    
    print(hist_data)
    
    
    # Create pivot table: rows=cities, columns=dates, values=avg temperature
    pivot_data = hist_data.pivot_table(
        index='city', 
        columns='date', 
        values='temperature',
        aggfunc='mean'
    )
    
    # Skip if pivot table is empty
    if pivot_data.empty:
        print("No valid data for temperature heatmap pivot table")
        return
    
    # Sort cities by average temperature (hottest to coldest)
    city_temps = pivot_data.mean(axis=1).sort_values(ascending=False)
    pivot_data = pivot_data.reindex(city_temps.index)
    
    plt.figure(figsize=(16, 10))
    sns.heatmap(pivot_data, cmap='YlOrRd', annot=False, fmt=".1f", linewidths=.5)
    
    plt.title('Temperature Heatmap Across Indian Cities Over Time')
    plt.ylabel('City')
    plt.xlabel('Date')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/temperature_heatmap.png")
    plt.close()

def create_wind_rose(df, output_dir):
    """Create wind rose diagram showing wind direction and speed distributions"""
    plt.figure(figsize=(10, 10))
    
    # Filter data with valid wind information
    wind_data = df.dropna(subset=['wind_speed', 'wind_direction'])
    
    if wind_data.empty:
        print("No valid data for wind rose diagram")
        return
    
    # Convert directions to 16 compass directions
    bins = np.arange(-11.25, 372.25, 22.5)
    direction_names = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
                       'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    
    # Calculate the direction and speed bins
    dir_bins = np.digitize(wind_data['wind_direction'], bins) % 16
    dir_counts = np.bincount(dir_bins, minlength=16)
    
    # Create the wind rose
    angles = np.linspace(0, 2*np.pi, 16, endpoint=False)
    width = 2*np.pi / 16
    
    ax = plt.subplot(111, polar=True)
    bars = ax.bar(angles, dir_counts, width=width, bottom=0.0)
    
    # Color code the bars by frequency
    norm = plt.Normalize(dir_counts.min(), dir_counts.max())
    for bar, angle in zip(bars, angles):
        bar.set_facecolor(plt.cm.viridis(norm(bar.get_height())))
    
    # Set the labels
    ax.set_xticks(angles)
    ax.set_xticklabels(direction_names)
    
    plt.title('Wind Direction Distribution')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/wind_rose.png")
    plt.close()

if __name__ == "__main__":
    # Run visualizations directly if script is executed
    create_visualizations()