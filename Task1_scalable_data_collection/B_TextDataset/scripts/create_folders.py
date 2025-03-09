import os

categories = [
    "airplanes", "bicycles", "books", "bottles", "buildings", 
    "cars", "cats", "chairs", "clocks", "computers", "dogs", 
    "flowers", "keys", "lamps", "smartphones", "motorcycles", 
    "shoes", "spoons", "tables", "trees"
]

# Define dataset path
base_path = os.path.join(os.getcwd(), "A_ImageDataset", "data")

# Create dataset folders
for category in categories:
    category_path = os.path.join(base_path, category)
    os.makedirs(category_path, exist_ok=True)

print(f" Successfully created dataset folders inside {base_path}")
