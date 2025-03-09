import os
import requests
import json
import time

# Load countries.json
json_file = os.path.join(os.path.dirname(__file__), "countries.json")
print(json_file)
with open(json_file, 'r') as file:
    countries = json.load(file)

# Create a folder to store the anthems
anthem_dir = os.path.join(os.path.dirname(__file__), "../anthems")
if not os.path.exists(anthem_dir):
    os.makedirs(anthem_dir)

# Base URL for the website
base_url = "https://nationalanthems.info/"

# Headers to pretend like a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# Function to download MP3 files
def download_mp3(url, file_path):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"✅ Downloaded MP3 for {file_path}")
    else:
        print(f"❌ Failed to download MP3 from {url}")

# Iterate through each country
for code, name in countries.items():
    mp3_url = f"{base_url}{code.lower()}.mp3"
    mp3_path = os.path.join(anthem_dir, f"{name}.mp3")
    
    # Skip if already downloaded
    if os.path.exists(mp3_path):
        print(f"✅ Already downloaded {name}")
        continue

    # Try downloading
    download_mp3(mp3_url, mp3_path)
    time.sleep(1)  # Prevent rate limiting
