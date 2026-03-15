from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)
user_logs = {}


def get_username(): 
    token = request.headers.get("Authorization")
    if not token or not token.endswith("-token"):
        return None
    return token[:-6]

@app.route('/log', methods=['GET'])
def log():
    username = get_username()
    if not username:
        return jsonify({"error": "No token provided"}), 401
    log = user_logs.get(username, []) 
    return jsonify({"log": log, "message": "Logged"})

@app.route('/log', methods=['POST'])
def add_log():
    username = get_username()
    if not username:
        return jsonify({"error": "No token provided"}), 401
    data = request.get_json()
    entry = {
        "session_type": data["session_type"],
        "duration": data["duration"],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if username not in user_logs:
        user_logs[username] = []
    user_logs[username].append(entry)
    
    return jsonify({"message": "Session logged", "entry": entry})

@app.route('/log', methods=['DELETE'])
def clear_logs():
    username = get_username()
    if not username:
        return jsonify({"error": "No token provided"}), 401
    user_logs[username] = []
    return jsonify({"message": "Logs cleared"})

app.run(port=6003)
