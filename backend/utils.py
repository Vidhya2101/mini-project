import csv
from datetime import datetime
import os

# Load emission factors
def load_emission_factors(file_path='emission_factors.csv'):
    factors = {}
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            factors[row['activity']] = float(row['emission_factor'])
    return factors

# Calculate emissions
def calculate_emissions(data, factors):
    emissions = {
        'transport': 0.0,
        'phone': 0.0,
        'laptop': 0.0,
    }
    emissions['transport'] += data.get('car_km', 0) * factors.get('car', 0)
    emissions['transport'] += data.get('bus_km', 0) * factors.get('bus', 0)
    emissions['transport'] += data.get('bike_km', 0) * factors.get('bike', 0)
    emissions['phone'] = data.get('phone_hrs', 0) * factors.get('phone', 0)
    emissions['laptop'] = data.get('laptop_hrs', 0) * factors.get('laptop', 0)
    emissions['total'] = emissions['transport'] + emissions['phone'] + emissions['laptop']
    return emissions

# Save data
def save_user_data(file_path, user_data):
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=user_data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(user_data)

# Recommend trees
def recommend_trees(emission_kg):
    return round(emission_kg / 21.77, 2)  # Avg 1 tree absorbs ~21.77kg CO₂/year
