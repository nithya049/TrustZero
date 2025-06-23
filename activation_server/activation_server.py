from flask import Flask, request, jsonify
import json, os

app = Flask(__name__)
TOKENS_FILE = "tokens.json"
UUIDS_FILE = "uuids.json"

# Load or initialize data
def load_file(path):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            json.dump({}, f)
    with open(path, 'r') as f:
        return json.load(f)

def save_file(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

@app.route("/validate_token", methods=["POST"])
def validate_token():
    data = request.json
    token = data.get("token")
    uuid = data.get("uuid")

    tokens = load_file(TOKENS_FILE)
    uuids = load_file(UUIDS_FILE)

    if token not in tokens:
        return jsonify({"status": "invalid", "reason": "token not found"})
    if tokens[token]['used']:
        if uuids.get(token) == uuid:
            return jsonify({"status": "ok", "message": "already registered on this device"})
        else:
            return jsonify({"status": "invalid", "reason": "token already used on another device"})

    # Mark token as used and store UUID
    tokens[token]['used'] = True
    uuids[token] = uuid

    save_file(TOKENS_FILE, tokens)
    save_file(UUIDS_FILE, uuids)

    return jsonify({"status": "ok"})

@app.route("/status/<token>")
def status(token):
    tokens = load_file(TOKENS_FILE)
    if token in tokens:
        return jsonify(tokens[token])
    else:
        return jsonify({"error": "not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)