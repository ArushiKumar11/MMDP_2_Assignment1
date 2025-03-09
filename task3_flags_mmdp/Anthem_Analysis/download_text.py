import os
import requests
from bs4 import BeautifulSoup
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
    "Accept-Language": "en-US,en;q=0.9",
}

# Iterate through each country
for code, name in countries.items():
    
    if(code.lower()<='sl'):
        continue
    url = f"{base_url}{code.lower()}.htm"
    response = requests.get(url, headers=headers)
    print(url)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch {name}")
        time.sleep(1)
        continue
    
    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    anthem_text = ""

    # ✅ First check for "English translation"
    collapse_div = soup.find('div', class_='collapseomatic', title="English translation")
    if collapse_div and collapse_div.find_next_sibling('div', class_='collapseomatic_content'):
        anthem_section = collapse_div.find_next_sibling('div', class_='collapseomatic_content')
        anthem_text = anthem_section.get_text(separator="\n").strip()
    
    # ✅ If no "English translation", check for "English versification"
    if not anthem_text:
        collapse_div = soup.find('div', class_='collapseomatic', title="English versification")
        if collapse_div and collapse_div.find_next_sibling('div', class_='collapseomatic_content'):
            anthem_section = collapse_div.find_next_sibling('div', class_='collapseomatic_content')
            anthem_text = anthem_section.get_text(separator="\n").strip()
    if not anthem_text:
        collapse_div = soup.find('div', class_='collapseomatic', title="English lyrics")
        if collapse_div and collapse_div.find_next_sibling('div', class_='collapseomatic_content'):
            anthem_section = collapse_div.find_next_sibling('div', class_='collapseomatic_content')
            anthem_text = anthem_section.get_text(separator="\n").strip()
    
    # ✅ Still no anthem found? Skip the country
    if not anthem_text:
        print(f"❌ No anthem found for {name}")
        time.sleep(1)
        continue
    
    # ✅ Save the anthem text to a file
    file_path = os.path.join(anthem_dir, f"{name}.txt")
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(anthem_text)
    
    print(f"✅ Saved anthem for {name}")
    time.sleep(1)  # Prevent rate limiting
