from flask import Flask, jsonify, request

app = Flask(__name__)

sounds = ["chime", "doorbell", "alarm clock", "bell"]
user_sounds = {}

def get_username(): 
    token = request.headers.get("Authorization")
    if not token or not token.endswith("-token"):
        return None
    return token[:-6]


@app.route('/sound', methods=['GET'])
def sound():
    return jsonify({"sounds": sounds})
    # create a list of the notfication sounds which we can 

@app.route('/alert', methods=['GET'])
def alert():
    username = get_username()
    if not username:
        return jsonify({"error": "No token provided"}), 401
    sound = user_sounds.get(username, "chime")  # "chime" is the default
    return jsonify({"sound": sound, "message": "Session complete!"})

@app.route('/alert/sound', methods=['PUT'])
def changeNoti():
    username = get_username()
    if not username:
        return jsonify({"error": "No token provided"}), 401
    data = request.get_json()
    new_sound = data["sound"]
    user_sounds[username] = new_sound
    return jsonify({"message": "Sound updated", "sound": new_sound})

app.run(port=6002)