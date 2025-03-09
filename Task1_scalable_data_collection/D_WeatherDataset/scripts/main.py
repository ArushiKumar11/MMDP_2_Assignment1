"""
IndianWeatherPulse - Main Script
Entry point for the weather data collection and analysis project.
"""

import argparse
import sys
from datetime import datetime

def main():
    """Main entry point for the IndianWeatherPulse project"""
    parser = argparse.ArgumentParser(description='IndianWeatherPulse - Weather Data Collection and Analysis')
    
    parser.add_argument('--collect', action='store_true', help='Collect weather data')
    parser.add_argument('--visualize', action='store_true', help='Generate visualizations')
    parser.add_argument('--schedule', action='store_true', help='Start scheduled data collection')
    parser.add_argument('--days', type=int, default=30, help='Number of days of historical data to collect (default: 30)')
    parser.add_argument('--cities', type=str, help='Comma-separated list of cities to focus on')
    
    args = parser.parse_args()
    
    # Import modules only when needed
    if args.collect or args.schedule:
        from collect_data import collect_and_store_data, update_master_dataset, setup_scheduled_collection
    
    if args.visualize:
        from visualize_data import create_visualizations
    
    # Process commands
    if args.collect:
        print(f"[{datetime.now()}] Starting data collection...")
        update_master_dataset()
        print(f"[{datetime.now()}] Data collection complete")
    
    if args.visualize:
        print(f"[{datetime.now()}] Generating visualizations...")
        create_visualizations()
        print(f"[{datetime.now()}] Visualizations complete")
    
    if args.schedule:
        print(f"[{datetime.now()}] Setting up scheduled data collection...")
        setup_scheduled_collection()
    
    # If no arguments provided, show help
    if not (args.collect or args.visualize or args.schedule):
        parser.print_help()

if __name__ == "__main__":
    main()