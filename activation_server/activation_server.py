# activation_server.py
from flask import Flask, request, jsonify, render_template
import os, json, random, string
from email.message import EmailMessage
import smtplib

app = Flask(__name__)
TOKENS_FILE = "tokens.json"
APPROVED_EMAILS_FILE = "approved_emails.json"

EMAIL_SENDER = "securetrustzero@gmail.com"
EMAIL_PASSWORD = "ennx audy kpfi ihdl"

def load_tokens():
    if not os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'w') as f:
            json.dump({}, f)
    with open(TOKENS_FILE, 'r') as f:
        return json.load(f)

def save_tokens(data):
    with open(TOKENS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_approved_emails():
    if not os.path.exists(APPROVED_EMAILS_FILE):
        return set()
    with open(APPROVED_EMAILS_FILE, 'r') as f:
        return set(json.load(f))

def generate_token():
    return str(random.randint(100000, 999999))

def send_otp_email(name, email_id, otp):
    subject = "OTP for Secure Viewer Installation"
    body = f"""Dear {name},

Your One-Time Password (OTP) is: {otp}.

Please enter this OTP during Secure Viewer installation.

Team TrustZero"""

    email = EmailMessage()
    email['From'] = EMAIL_SENDER
    email['To'] = email_id
    email['Subject'] = subject
    email.set_content(body)

    with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(email)

@app.route("/get_token", methods=["GET", "POST"])
def get_token():
    token = None
    error = None
    denied = False  # New flag for template

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        name = email.split("@")[0]
        approved = load_approved_emails()

        if email not in approved:
            error = "Email not authorized. Please contact the administrator."
            return render_template("get_token.html", error=error)

        tokens = load_tokens()

        for t, entry in tokens.items():
            if entry["email"] == email:
                if entry["used"]:
                    denied = True
                    return render_template("get_token.html", denied=denied)
                token = t
                break
        else:
            token = ''.join(random.choices(string.digits, k=6))  # OTP
            tokens[token] = {"email": email, "uuid": None, "used": False}
            save_tokens(tokens)
            send_otp_email(name, email, token)

    return render_template("get_token.html", token=token, error=error, denied=denied)



@app.route("/validate_token", methods=["POST"])
def validate_token():
    data = request.get_json()
    token = data.get("token")
    uuid = data.get("uuid")

    tokens = load_tokens()
    if token not in tokens:
        return jsonify({"status": "error", "reason": "Invalid token"}), 403

    entry = tokens[token]

    if entry["used"]:
        return jsonify({"status": "error", "reason": "Token already used"}), 403

    if entry["uuid"] is None:
        entry["uuid"] = uuid
        entry["used"] = True
        save_tokens(tokens)
        return jsonify({"status": "ok", "message": "Token activated and bound"}), 200

    if entry["uuid"] != uuid:
        return jsonify({"status": "error", "reason": "Token bound to another device"}), 403

    entry["used"] = True
    save_tokens(tokens)
    return jsonify({"status": "ok", "message": "Token verified"}), 200

@app.route("/status/<token>")
def status(token):
    tokens = load_tokens()
    if token in tokens:
        return jsonify(tokens[token])
    return jsonify({"error": "not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
