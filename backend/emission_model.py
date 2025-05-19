# emission_model.py

EMISSION_FACTORS = {
    "car": 0.192,
    "bus": 0.105,
    "bike": 0.072,
    "phone": 0.05,
    "laptop": 0.1
}

def calculate_emissions(car_km, bus_km, bike_km, phone_hrs, laptop_hrs):
    car_emission = car_km * EMISSION_FACTORS["car"]
    bus_emission = bus_km * EMISSION_FACTORS["bus"]
    bike_emission = bike_km * EMISSION_FACTORS["bike"]
    phone_emission = phone_hrs * EMISSION_FACTORS["phone"]
    laptop_emission = laptop_hrs * EMISSION_FACTORS["laptop"]

    total_emission = car_emission + bus_emission + bike_emission + phone_emission + laptop_emission

    return {
        "car_km": car_km,
        "bus_km": bus_km,
        "bike_km": bike_km,
        "phone_hrs": phone_hrs,
        "laptop_hrs": laptop_hrs,
        "total_emission": round(total_emission, 2)
    }

