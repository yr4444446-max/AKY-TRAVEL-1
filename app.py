"""
Plan Your Trip India — Flask Backend
AI Trip Planner API
Run with: python app.py
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# ─── City Database ───────────────────────────────────────────────
CITY_DATA = {
    "jaipur": {
        "name": "Jaipur",
        "famous": ["Amber Fort", "City Palace", "Hawa Mahal", "Jantar Mantar", "Nahargarh Fort"],
        "hidden": ["Panna Meena ka Kund", "Sisodia Rani Garden", "Khole ke Hanuman Ji", "Sanganer Village"],
        "food": [
            {"name": "Pyaaz Kachori", "price": 20},
            {"name": "Dal Baati Churma", "price": 80},
            {"name": "Laal Maas", "price": 200},
            {"name": "Ghewar", "price": 60},
            {"name": "Mawa Kachori", "price": 30},
        ],
        "per_day_cost": {"budget": 1100, "normal": 2900, "luxury": 8700},
        "tips": "Visit forts early morning to avoid crowds. Hire a local guide for ₹500.",
    },
    "goa": {
        "name": "Goa",
        "famous": ["Baga Beach", "Basilica of Bom Jesus", "Fort Aguada", "Anjuna Beach", "Calangute Beach"],
        "hidden": ["Butterfly Beach", "Arambol Sweet Lake", "Divar Island", "Cabo de Rama Fort"],
        "food": [
            {"name": "Prawn Balchão", "price": 150},
            {"name": "Bebinca dessert", "price": 60},
            {"name": "Goan Fish Curry Rice", "price": 200},
            {"name": "Cafreal Chicken", "price": 180},
        ],
        "per_day_cost": {"budget": 1550, "normal": 4200, "luxury": 10500},
        "tips": "North Goa for parties, South Goa for peace. Rent a scooter for ₹300/day.",
    },
    "manali": {
        "name": "Manali",
        "famous": ["Rohtang Pass", "Solang Valley", "Hadimba Temple", "Beas River", "Mall Road"],
        "hidden": ["Naggar Castle", "Great Himalayan National Park", "Chandrakhani Pass", "Bijli Mahadev"],
        "food": [
            {"name": "Siddu (local bread)", "price": 50},
            {"name": "Trout Fish Fry", "price": 250},
            {"name": "Aktori pancake", "price": 40},
            {"name": "Dham feast", "price": 120},
        ],
        "per_day_cost": {"budget": 1400, "normal": 3500, "luxury": 8800},
        "tips": "Carry warm clothes even in summer. Book permits for Rohtang Pass online.",
    },
    "varanasi": {
        "name": "Varanasi",
        "famous": ["Dashashwamedh Ghat", "Kashi Vishwanath Temple", "Sarnath", "Manikarnika Ghat", "Assi Ghat"],
        "hidden": ["Lalita Ghat", "Scindia Ghat", "Tulsi Manas Temple", "Ramnagar Fort"],
        "food": [
            {"name": "Kachori Sabzi", "price": 30},
            {"name": "Banarasi Paan", "price": 20},
            {"name": "Thandai", "price": 50},
            {"name": "Tamatar Chaat", "price": 40},
            {"name": "Malaiyo (winter only)", "price": 30},
        ],
        "per_day_cost": {"budget": 950, "normal": 2550, "luxury": 6500},
        "tips": "Wake up for sunrise boat ride on Ganga. Ganga Aarti at Dashashwamedh Ghat is unmissable.",
    },
    "kerala": {
        "name": "Kerala",
        "famous": ["Alleppey Backwaters", "Munnar Tea Gardens", "Kovalam Beach", "Periyar Wildlife Sanctuary", "Varkala Cliff"],
        "hidden": ["Gavi Eco Forest", "Bekal Fort", "Thenmala Eco Tourism", "Athirapally Waterfalls"],
        "food": [
            {"name": "Appam & Stew", "price": 80},
            {"name": "Kerala Sadya", "price": 150},
            {"name": "Karimeen Pollichathu", "price": 300},
            {"name": "Puttu & Kadala Curry", "price": 60},
            {"name": "Pazham Pori", "price": 20},
        ],
        "per_day_cost": {"budget": 1400, "normal": 3850, "luxury": 10000},
        "tips": "Houseboat stay in Alleppey is a must-do. October–February is peak season.",
    },
    "ladakh": {
        "name": "Ladakh",
        "famous": ["Pangong Lake", "Nubra Valley", "Leh Palace", "Magnetic Hill", "Hemis Monastery"],
        "hidden": ["Tso Moriri Lake", "Zanskar Valley", "Dah Hanu Village", "Phugtal Monastery"],
        "food": [
            {"name": "Thukpa noodle soup", "price": 80},
            {"name": "Skyu pasta", "price": 70},
            {"name": "Butter Tea (Po Cha)", "price": 30},
            {"name": "Tsampa porridge", "price": 50},
            {"name": "Steamed Momos", "price": 60},
        ],
        "per_day_cost": {"budget": 1900, "normal": 4700, "luxury": 12000},
        "tips": "Acclimatize for 2 days in Leh before high-altitude excursions. Carry cash — ATMs are unreliable.",
    },
}

def get_city_key(destination):
    d = destination.lower().strip()
    for key in CITY_DATA:
        if key in d or d in key:
            return key
    return None

def build_day_plan(city_data, days, style):
    all_spots = city_data["famous"] + city_data["hidden"]
    food_list = city_data["food"]
    plan = []

    activities = {
        "budget": ["Walk + explore local markets", "Sunrise photography", "Street food hunting", "Free museum visit"],
        "normal": ["Guided tour", "Local transport tour", "Sunset cruise/view", "Cultural show"],
        "luxury": ["Private chauffeur tour", "Helicopter/premium excursion", "Spa & wellness", "Fine dining experience"],
    }

    for d in range(1, min(int(days), 8) + 1):
        morning_spot = all_spots[(d * 2 - 2) % len(all_spots)]
        evening_spot = all_spots[(d * 2 - 1) % len(all_spots)]
        food_item = food_list[(d - 1) % len(food_list)]
        bonus = activities[style][(d - 1) % len(activities[style])]

        plan.append({
            "day": d,
            "morning": f"Visit {morning_spot}",
            "afternoon": bonus,
            "evening": f"Explore {evening_spot}",
            "food_recommendation": f"Try {food_item['name']} (~₹{food_item['price']})",
        })

    return plan

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/planner', methods=['POST'])
def planner():
    data = request.get_json()

    destination = data.get('destination', '').strip()
    budget = int(data.get('budget', 10000))
    days = int(data.get('days', 3))
    style = data.get('style', 'normal')  # budget / normal / luxury

    if not destination:
        return jsonify({'error': 'Destination is required'}), 400

    city_key = get_city_key(destination)
    city_data = CITY_DATA.get(city_key) if city_key else None

    if city_data:
        per_day = city_data['per_day_cost'].get(style, city_data['per_day_cost']['normal'])
        famous = city_data['famous']
        hidden = city_data['hidden']
        food = [f"{f['name']} (~₹{f['price']})" for f in city_data['food']]
        tips = city_data['tips']
        city_name = city_data['name']
    else:
        per_day = {'budget': 1000, 'normal': 3000, 'luxury': 8000}.get(style, 3000)
        famous = [f"{destination} Heritage Site", f"{destination} City Centre", f"{destination} Museum", "Local Market", "Viewpoint"]
        hidden = [f"Old town lanes of {destination}", "Local village nearby", "Scenic route", "Sunrise point"]
        food = ["Local breakfast thali (~₹60)", "Street snacks (~₹30)", "Regional curry (~₹150)", "Sweet shop treats (~₹40)"]
        tips = f"Hire a local guide for the best experience in {destination}."
        city_name = destination.title()

    total_estimate = per_day * days
    breakdown = {
        "accommodation": round(per_day * 0.40) * days,
        "food": round(per_day * 0.25) * days,
        "transport": round(per_day * 0.20) * days,
        "activities": round(per_day * 0.15) * days,
    }
    surplus = budget - total_estimate

    day_plan = build_day_plan(
        {'famous': famous, 'hidden': hidden, 'food': [{'name': f.split('(')[0].strip(), 'price': 100} for f in food]},
        days, style
    )

    return jsonify({
        "success": True,
        "destination": city_name,
        "days": days,
        "style": style,
        "budget_total": budget,
        "estimated_cost": total_estimate,
        "cost_per_day": per_day,
        "surplus": surplus,
        "breakdown": breakdown,
        "famous_places": famous,
        "hidden_gems": hidden,
        "street_food": food,
        "day_plan": day_plan,
        "tips": tips,
    })

@app.route('/contact', methods=['POST'])
def contact():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')
    # In production, send email via SMTP or save to DB
    print(f"[Contact] From: {name} <{email}> — {message}")
    return jsonify({"success": True, "message": "Thank you! We'll get back to you within 24 hours."})

if __name__ == '__main__':
    print("🌿 Plan Your Trip India — Flask Server")
    print("📍 Running on http://localhost:5000")
    app.run(debug=True, port=5000)
