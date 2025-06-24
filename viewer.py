# Integrated viewer.py with one-time token activation, UUID binding, and .dll-based hidden auth verification only
import uuid
from customtkinter import *
import os
import sys
import hashlib
import pickle
import subprocess
import requests
import json
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from mife.single.damgard import FeDamgard
from cryptography.fernet import Fernet

AUTH_CARRIER = os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "CLR", "Cache", "winmm.dll")
MARKER = b"--AUTH--"
FERNET_KEY = b"aMu5EtFg3FAGdyFZ_Te9axERe3qfslmFqFTH9ubMec0="
SERVER_URL = "http://localhost:5000/validate_token"

def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.abspath(filename)

def get_system_uuid():
    try:
        result = subprocess.check_output(
            ['powershell', '-Command', "(Get-WmiObject Win32_ComputerSystemProduct).UUID"],
            stderr=subprocess.STDOUT
        )
        lines = result.decode().splitlines()
        uuid_line = next((line.strip() for line in lines if line.strip() and "UUID" not in line), None)
        if uuid_line and not uuid_line.startswith(("00000000", "FFFFFFFF", "ffffffff")):
            return uuid_line
        else:
            raise ValueError("Invalid UUID")
    except Exception:
        return None

def hash_uuid(uuid_str):
    return hashlib.sha256(uuid_str.encode()).hexdigest().lower()

def get_hidden_auth_hash():
    try:
        with open(AUTH_CARRIER, "rb") as f:
            content = f.read()
            index = content.find(MARKER)
            if index != -1:
                hash_bytes = content[index + len(MARKER): index + len(MARKER) + 64]  # SHA256 hex is 64 chars
                return hash_bytes.decode().strip().lower()
            else:
                return None
    except Exception:
        return None

def verify_uuid_binding():
    uuid_str = get_system_uuid()
    uuid_hash = hash_uuid(uuid_str)
    stored_hash = get_hidden_auth_hash()
    if stored_hash and stored_hash == uuid_hash:
        return True, "Device verified."
    return False, "Device not authorized. UUID mismatch."

def load_data():
    with open(resource_path("fe_data.pkl"), "rb") as f:
        return pickle.load(f)

def decrypt_age_over_18(data):
    names = data["names"]
    cipher_ages = data["cipher_ages"]
    function_keys = data["function_keys"]
    public_key = data["public_key"]

    eligible = []
    for name, cipher, sk in zip(names, cipher_ages, function_keys):
        result = FeDamgard.decrypt(cipher, public_key, sk, (0, 150))
        if result > 0:
            eligible.append(name)
    return eligible

def decrypt_salary_over_45(data):
    names = data["names"]
    cipher_salaries = data["cipher_salaries"]
    salary_keys = data["salary_keys"]
    public_key = data["public_key"]

    eligible = []
    for name, cipher, sk in zip(names, cipher_salaries, salary_keys):
        result = FeDamgard.decrypt(cipher, public_key, sk, (0, 150))
        if result > 0:
            eligible.append(name)
    return eligible

def decrypt_salary_sum(data):
    cipher_salaries = data["cipher_salaries"]
    sum_key = data["sum_key"]
    public_key = data["public_key"]

    total = 0
    for cipher in cipher_salaries:
        total += FeDamgard.decrypt(cipher, public_key, sum_key, (0, 10000))
    return total

def launch_gui():
    verified, message = verify_uuid_binding()
    if not verified:
        messagebox.showerror("Unauthorized", f"{message}\nExiting.")
        sys.exit(1)

    # GUI Setup
    set_appearance_mode("dark")
    set_default_color_theme("blue")
    heading_font = ("Trebuchet MS", 30, "bold")
    subheading_font = ("Trebuchet MS", 20)
    text_font = ("Trebuchet MS", 16)

    app = CTk()
    app.title("Secure Viewer")
    app.geometry("600x540")

    CTkLabel(app, text="Secure Viewer", font=heading_font, text_color="#A9F3FD").pack(pady=20)
    output_box = CTkTextbox(app, width=500, height=200, font=text_font, wrap="word")
    output_box.pack(pady=10)
    status_label = CTkLabel(app, text="", font=subheading_font)
    status_label.pack(pady=(5, 0))

    data = load_data()

    def run_decrypt(decrypt_func, label):
        output_box.delete("1.0", "end")
        verified, message = verify_uuid_binding()
        if verified:
            status_label.configure(text="Access Granted", text_color="#00FF04", font=subheading_font)
            result = decrypt_func(data)
            output_box.insert("end", f"{message}\n\n{label}\n")
            if isinstance(result, list):
                output_box.insert("end", "\n".join(result))
            else:
                output_box.insert("end", str(result))
        else:
            status_label.configure(text="Access Denied", text_color="#FF2B2B", font=subheading_font)
            output_box.insert("end", f"{message}\n\nAborting decryption due to failed verification.")

    CTkButton(app, text="Age > 18", command=lambda: run_decrypt(decrypt_age_over_18, "People with age > 18:"),
              font=("Trebuchet MS", 16), fg_color="#87F1FF", hover_color="#42E0F4",
              text_color="black").pack(pady=5)

    CTkButton(app, text="Salary > 45", command=lambda: run_decrypt(decrypt_salary_over_45, "People with salary > 45:"),
              font=("Trebuchet MS", 16), fg_color="#87F1FF", hover_color="#42E0F4",
              text_color="black").pack(pady=5)

    CTkButton(app, text="Total Salary", command=lambda: run_decrypt(decrypt_salary_sum, "Total Salary of All:"),
              font=("Trebuchet MS", 16), fg_color="#87F1FF", hover_color="#42E0F4",
              text_color="black").pack(pady=5)

    CTkButton(app, text="Close", command=app.destroy, font=("Trebuchet MS", 16),
              fg_color="#FD3434", hover_color="#E90000", text_color="black").pack(pady=10)

    app.mainloop()

if __name__ == "__main__":
    launch_gui()