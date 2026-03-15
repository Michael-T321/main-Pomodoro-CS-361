from flask import Flask, jsonify, request
import random

quotes = ["You're doing great!", "Keep up the hard work!", "You're almost there!", "You're getting smarter by the minute!",
        "Great work! Every focused session builds momentum.", "Rest now — you've earned it.",
        "Focus isn't about perfection — it's about showing up."]

user_prefs = {}
app = Flask(__name__)

def get_username(): 
    token = request.headers.get("Authorization")
    if not token or not token.endswith("-token"):
        return None
    return token[:-6]

@app.route('/quote', methods = ['GET'])
def quote():
    return jsonify({"quote": random.choice(quotes)})

@app.route('/quote/settings', methods=['GET'])
def quoteStatus():
    username = get_username()
    if not username:
        return jsonify({"error": "No token provided"}), 401
    status = user_prefs.get(username, "ON") 
    return jsonify({"quote": status, "message": f"Quotes are {status}"})

@app.route('/quote/settings', methods=['PUT'])
def changeQuoteStatus():
    username = get_username()
    if not username:
        return jsonify({"error": "No token provided"}), 401
    data = request.get_json()
    new_pref = data["quote"]
    user_prefs[username] = new_pref
    return jsonify({"message": "Quote preference updated", "quote": new_pref})

app.run(port=6001)