from flask import Flask, request, jsonify, send_from_directory
import csv
import os
from datetime import datetime
from flask_cors import CORS
from collections import defaultdict
import math

app = Flask(__name__)
CORS(app)
USER_CSV = "user_data.csv"  # stores both login and activity info

# Emission calculation factors (India-specific)
EMISSION_FACTORS = {
    "car": 0.192,      # kg CO2 per km
    "bus": 0.105,
    "bike": 0.072,
    "phone": 0.012,    # kg CO2 per hr
    "laptop": 0.04
}

# Unified CSV fieldnames
CSV_FIELDS = ["name", "email", "phone", "date", "car_km", "bus_km", "bike_km", "phone_hrs", "laptop_hrs", "total_emission"]

# Handle login submission
@app.route("/submit_login", methods=["POST"])
def submit_login():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    name = data.get("name", "")
    email = data.get("email", "")
    phone = data.get("phone", "")
    today = datetime.now().strftime("%Y-%m-%d")

    # Prevent duplicate login entry for same user on the same day
    if os.path.exists(USER_CSV):
        with open(USER_CSV, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["email"] == email and row["date"] == today and float(row["total_emission"]) > 0:
                    return jsonify({"status": "success"})  # Already logged today with activity

    # Save placeholder entry
    row = {
        "name": name,
        "email": email,
        "phone": phone,
        "date": today,
        "car_km": 0,
        "bus_km": 0,
        "bike_km": 0,
        "phone_hrs": 0,
        "laptop_hrs": 0,
        "total_emission": 0
    }

    file_exists = os.path.exists(USER_CSV)
    with open(USER_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not file_exists or os.stat(USER_CSV).st_size == 0:
            writer.writeheader()
        writer.writerow(row)

    return jsonify({"status": "success"})

# Handle activity submission
@app.route("/submit_activity", methods=["POST"])
def submit_activity():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    name = data.get("name", "")
    email = data.get("email", "")
    phone = data.get("phone", "")
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Use the km values sent directly
    car_km = float(data.get("car_km", 0))
    bus_km = float(data.get("bus_km", 0))
    bike_km = float(data.get("bike_km", 0))
    phone_hrs = float(data.get("phone_hrs", 0))
    laptop_hrs = float(data.get("laptop_hrs", 0))

    # Calculate emissions
    total_emission = (
        car_km * EMISSION_FACTORS["car"] +
        bus_km * EMISSION_FACTORS["bus"] +
        bike_km * EMISSION_FACTORS["bike"] +
        phone_hrs * EMISSION_FACTORS["phone"] +
        laptop_hrs * EMISSION_FACTORS["laptop"]
    )

    row = {
        "name": name,
        "email": email,
        "phone": phone,
        "date": date_str,
        "car_km": car_km,
        "bus_km": bus_km,
        "bike_km": bike_km,
        "phone_hrs": phone_hrs,
        "laptop_hrs": laptop_hrs,
        "total_emission": round(total_emission, 2)
    }

    file_exists = os.path.exists(USER_CSV)
    with open(USER_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not file_exists or os.stat(USER_CSV).st_size == 0:
            writer.writeheader()
        writer.writerow(row)

    return jsonify({"status": "success", "total_emission": round(total_emission, 2)})

# Get results for visualizations
@app.route("/get_results", methods=["GET"])
def get_results():
    email = request.args.get("email")
    if not email:
        return jsonify({"status": "error", "message": "Email parameter missing"}), 400

    if not os.path.exists(USER_CSV):
        return jsonify({"status": "error", "message": "No data found"}), 404

    activities = []
    with open(USER_CSV, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("email") == email:
                activities.append(row)

    if not activities:
        return jsonify({"status": "error", "message": "No activity data"}), 404

    total_transport = 0
    total_phone = 0
    total_laptop = 0
    date_totals = defaultdict(float)

    for entry in activities:
        try:
            car_km = float(entry.get("car_km", 0))
            bus_km = float(entry.get("bus_km", 0))
            bike_km = float(entry.get("bike_km", 0))
            phone_hrs = float(entry.get("phone_hrs", 0))
            laptop_hrs = float(entry.get("laptop_hrs", 0))
            total = float(entry.get("total_emission", 0))
            date = entry.get("date")

            total_transport += car_km * EMISSION_FACTORS["car"] + bus_km * EMISSION_FACTORS["bus"] + bike_km * EMISSION_FACTORS["bike"]
            total_phone += phone_hrs * EMISSION_FACTORS["phone"]
            total_laptop += laptop_hrs * EMISSION_FACTORS["laptop"]
            date_totals[date] += total
        except:
            continue

    emissions = {
        "Transport": round(total_transport, 2),
        "Phone": round(total_phone, 2),
        "Laptop": round(total_laptop, 2),
        "Total": round(total_transport + total_phone + total_laptop, 2)
    }

    history = [{"date": d, "total_emission": round(e, 2)} for d, e in sorted(date_totals.items())]
    latest_entry = activities[-1] 
    latest_total = round(float(latest_entry["total_emission"]), 2)
    latest_date = latest_entry["date"]
    user_name = latest_entry["name"]
    
    trees_to_plant = math.ceil(latest_total / 21.77)

    return jsonify({
        "status": "success",
        "name": latest_entry.get("name"),
        "email": latest_entry.get("email"),
        "date": latest_entry.get("date"),
        "total_emission": latest_total,
        "emissions": emissions,
        "history": history,
        "trees_to_plant": trees_to_plant
    })
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('static', path)

@app.route("/")
def serve_login():
    return send_from_directory('static', 'login.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

