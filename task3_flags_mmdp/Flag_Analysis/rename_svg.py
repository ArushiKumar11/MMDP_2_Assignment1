import os
import json

# Paths
svg_folder = os.path.join(os.path.dirname(__file__), "country-flags-main", "svg")
json_file = os.path.join(os.path.dirname(__file__), "country-flags-main", "countries.json")
print(json_file)
# Load the JSON file
with open(json_file, 'r') as file:
    country_mapping = json.load(file)

# Loop through all SVG files
for file_name in os.listdir(svg_folder):
    if file_name.endswith(".svg"):
        # Extract the ISO code from the file name (like "in.svg" -> "in")
        iso_code = file_name.split(".")[0]
        iso_code =iso_code.upper()
        # Check if the ISO code exists in the JSON mapping
        if iso_code in country_mapping:
            # Get the country name
            country_name = country_mapping[iso_code]
            
            # Create the new file name
            new_file_name = f"{country_name}.svg"
            old_path = os.path.join(svg_folder, file_name)
            new_path = os.path.join(svg_folder, new_file_name)
            
            # Rename the file
            os.rename(old_path, new_path)
            print(f"Renamed: {file_name} -> {new_file_name}")
        else:
            print(f"No match found for: {file_name}")

print(" All files renamed successfully!")
