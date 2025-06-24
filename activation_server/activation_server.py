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
    
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w") as f:
            f.write("{}")
    with open(path, "r") as f:
        return json.load(f)


def save_file(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

@app.route("/validate_token", methods=["POST"])
def validate_token():
    data = request.get_json()
    token = data.get("token", "").strip().upper()
    uuid = data.get("uuid")

    # Load tokens file
    if not os.path.exists("tokens.json"):
        return jsonify({"status": "error", "reason": "Token store missing"}), 500

    with open("tokens.json", "r") as f:
        tokens = json.load(f)

    if token not in tokens:
        return jsonify({"status": "error", "reason": "Invalid token"}), 403

    if tokens[token].get("used", False):
        return jsonify({"status": "error", "reason": "Token already used"}), 403

    # Mark token as used
    tokens[token]["used"] = True
    tokens[token]["uuid"] = uuid

    with open("tokens.json", "w") as f:
        json.dump(tokens, f, indent=2)

    return jsonify({"status": "ok"}), 200

@app.route("/status/<token>")
def status(token):
    tokens = load_file(TOKENS_FILE)
    if token in tokens:
        return jsonify(tokens[token])
    else:
        return jsonify({"error": "not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)