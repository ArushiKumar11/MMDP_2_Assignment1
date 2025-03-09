import os
import time
import json
import random
import requests
import pandas as pd
from datetime import datetime
import subprocess
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Directory setup
BASE_DIR = os.path.join(os.getcwd(), "C_AudioDataset")
AUDIO_DIR = os.path.join(BASE_DIR, "audio_files")
METADATA_FILE = os.path.join(BASE_DIR, "metadata.json")

# Create directories if they don't exist
os.makedirs(AUDIO_DIR, exist_ok=True)

# List of public radio stations with stream URLs
# These URLs are examples - you may need to find working stream URLs
RADIO_STATIONS = [
    {"name": "BBC Radio 1", "url": "http://stream.live.vc.bbcmedia.co.uk/bbc_radio_one"},
    {"name": "NPR", "url": "https://npr-ice.streamguys1.com/live.mp3"},
    {"name": "KEXP", "url": "https://kexp.streamguys1.com/kexp160.aac"},
    {"name": "Classic FM", "url": "https://media-ice.musicradio.com/ClassicFMMP3"},
    {"name": "France Info", "url": "http://direct.franceinfo.fr/live/franceinfo-midfi.mp3"},
    {"name": "ABC Radio Sydney", "url": "https://live-radio01.mediahubaustralia.com/2LRW/aac/"},
    {"name": "CBC Radio One", "url": "https://cbcliveradio-lh.akamaihd.net/i/CBCR1_TOR@118420/master.m3u8"},
    {"name": "SomaFM Groove Salad", "url": "http://ice1.somafm.com/groovesalad-256-mp3"},
    {"name": "WNYC", "url": "http://fm939.wnyc.org/wnycfm"},
    {"name": "Jazz24", "url": "https://live.wostreaming.net/direct/ppm-jazz24aac-ibc1"},
    {"name": "Radio Paradise", "url": "http://stream.radioparadise.com/aac-128"},
    {"name": "WAMU", "url": "https://hd1.wamu.org/"},
    {"name": "Triple J", "url": "https://live-radio01.mediahubaustralia.com/2TJW/aac/"},
    {"name": "Smooth Jazz", "url": "https://smoothjazz.cdnstream1.com/2585_128.mp3"},
    {"name": "BBC World Service", "url": "http://stream.live.vc.bbcmedia.co.uk/bbc_world_service"}
]

# Function to get audio duration using ffprobe
def get_audio_duration(file_path):
    """Get the duration of an audio file using ffprobe"""
    try:
        cmd = [
            "ffprobe", 
            "-v", "error", 
            "-show_entries", "format=duration", 
            "-of", "default=noprint_wrappers=1:nokey=1", 
            file_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            logger.warning(f"Could not determine duration: {result.stderr}")
            return None
            
        duration = float(result.stdout.strip())
        return duration
    except Exception as e:
        logger.error(f"Error getting duration: {str(e)}")
        return None

# Function to download and save audio stream
def record_audio_stream(station, duration, index):
    """
    Record audio from a radio station stream for a specified duration.
    
    Args:
        station (dict): Dictionary containing station name and URL
        duration (int): Duration to record in seconds
        index (int): Index number for the output file
    
    Returns:
        dict: Metadata about the recording or None if failed
    """
    try:
        station_name = station["name"]
        stream_url = station["url"]
        timestamp = datetime.now()
        
        # Create a filename with station name, date, and index
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"{index:02d}_{station_name.replace(' ', '_')}_{timestamp_str}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)
        
        logger.info(f"Recording {duration} seconds from {station_name}")
        
        # Use ffmpeg to download and save the stream
        # The -t parameter sets the duration in seconds
        command = [
            "ffmpeg",
            "-y",  # Overwrite output file if it exists
            "-i", stream_url,  # Input URL
            "-t", str(duration),  # Duration
            "-c:a", "libmp3lame",  # Audio codec
            "-b:a", "128k",  # Bitrate
            filepath  # Output file
        ]
        
        # Execute the command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Failed to record {station_name}: {stderr.decode()}")
            return None
            
        # Check if file was created and has content
        if not os.path.exists(filepath) or os.path.getsize(filepath) < 1000:  # Check if file is too small
            logger.error(f"Recording failed or file too small: {filepath}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return None
        
        # Get the actual duration using ffprobe instead of pydub
        actual_duration = get_audio_duration(filepath)
        if actual_duration is None:
            actual_duration = duration  # Use requested duration as fallback
            
        # Create metadata
        metadata = {
            "file_name": filename,
            "station_name": station_name,
            "stream_url": stream_url,
            "timestamp": timestamp_str,
            "requested_duration": duration,
            "actual_duration": actual_duration,
            "file_size_kb": os.path.getsize(filepath) / 1024
        }
        
        logger.info(f"Successfully recorded {filename} ({actual_duration:.1f} seconds)")
        return metadata
        
    except Exception as e:
        logger.error(f"Error recording {station['name']}: {str(e)}")
        # Clean up any partial file
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return None

# Function to check if ffmpeg is installed
def check_ffmpeg():
    """Check if ffmpeg is installed and accessible"""
    try:
        result = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            version_info = result.stdout.decode().split('\n')[0]
            logger.info(f"FFmpeg is installed: {version_info}")
            return True
        else:
            logger.error("FFmpeg check failed with non-zero return code")
            return False
    except FileNotFoundError:
        logger.error("FFmpeg not found. Please install FFmpeg and make sure it's in your PATH.")
        return False
    except Exception as e:
        logger.error(f"Error checking FFmpeg: {str(e)}")
        return False

# Main function to collect the dataset
def collect_audio_dataset(num_samples=30, min_duration=30, max_duration=90):
    """
    Collect audio samples from random radio stations
    
    Args:
        num_samples (int): Number of audio samples to collect
        min_duration (int): Minimum duration in seconds
        max_duration (int): Maximum duration in seconds
    """
    # First check if ffmpeg is installed
    if not check_ffmpeg():
        logger.error("Cannot continue without FFmpeg. Please install it first.")
        return 0
        
    metadata_list = []
    successful_samples = 0
    attempts = 0
    max_attempts = num_samples * 3  # Allow for some failures
    
    logger.info(f"Starting collection of {num_samples} audio samples")
    
    while successful_samples < num_samples and attempts < max_attempts:
        # Select a random station
        station = random.choice(RADIO_STATIONS)
        
        # Generate a random duration between min and max
        duration = random.randint(min_duration, max_duration)
        
        # Record the audio
        metadata = record_audio_stream(station, duration, successful_samples + 1)
        
        attempts += 1
        
        if metadata:
            metadata_list.append(metadata)
            successful_samples += 1
            logger.info(f"Progress: {successful_samples}/{num_samples} samples collected")
        else:
            logger.warning(f"Failed attempt {attempts}/{max_attempts}")
        
        # Wait between recordings to avoid overwhelming the servers
        wait_time = random.uniform(1, 3)
        time.sleep(wait_time)
    
    # Save metadata to JSON file
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata_list, f, indent=4)
    
    # Also save as CSV for easier analysis
    df = pd.DataFrame(metadata_list)
    df.to_csv(os.path.join(BASE_DIR, "metadata.csv"), index=False)
    
    logger.info(f"Dataset collection complete: {successful_samples} samples collected")
    logger.info(f"Metadata saved to {METADATA_FILE}")
    
    return successful_samples

if __name__ == "__main__":
    print("=" * 50)
    print("RadioSoundscapes Dataset Collection")
    print("=" * 50)
    
    # Dataset parameters
    NUM_SAMPLES = 30
    MIN_DURATION = 30  # seconds
    MAX_DURATION = 90  # seconds
    
    print(f"Collecting {NUM_SAMPLES} audio samples of {MIN_DURATION}-{MAX_DURATION} seconds each...")
    collected = collect_audio_dataset(NUM_SAMPLES, MIN_DURATION, MAX_DURATION)
    
    print("\nCollection Summary:")
    print(f"- Samples collected: {collected}/{NUM_SAMPLES}")
    print(f"- Audio files stored in: {AUDIO_DIR}")
    print(f"- Metadata stored in: {METADATA_FILE}")
    
    print("=" * 50)