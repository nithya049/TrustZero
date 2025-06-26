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
import limit_manager
from limit_manager import limited

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
                hash_bytes = content[index + len(MARKER): index + len(MARKER) + 64]
                return hash_bytes.decode().strip().lower()
            else:
                return None
    except Exception:
        return None

@limited
def verify_uuid_binding():
    uuid_str = get_system_uuid()
    uuid_hash = hash_uuid(uuid_str)
    stored_hash = get_hidden_auth_hash()
    if stored_hash and stored_hash == uuid_hash:
        return True, "Device verified."
    return False, "Device not authorized. UUID mismatch."

def load_data():
    with open(resource_path("fe_military.pkl"), "rb") as f:
        return pickle.load(f)

@limited
def decrypt_total_casualties(data):
    total = 0
    for cipher in data["cipher_casualties"]:
        total += FeDamgard.decrypt(cipher, data["public_key"], data["sum_key_casualties"], (0, 1000))
    return total

@limited
def decrypt_total_supplies(data):
    total = 0
    for cipher in data["cipher_supplies"]:
        total += FeDamgard.decrypt(cipher, data["public_key"], data["sum_key_supplies"], (0, 10000))
    return total

@limited
def decrypt_total_enemy_sightings(data):
    total = 0
    for cipher in data["cipher_sightings"]:
        total += FeDamgard.decrypt(cipher, data["public_key"], data["sum_key_sightings"], (0, 1000))
    return total

@limited
def decrypt_avg_success_rating(data):
    total = 0
    count = len(data["cipher_success"])
    for cipher in data["cipher_success"]:
        total += FeDamgard.decrypt(cipher, data["public_key"], data["sum_key_success"], (0, 10000))
    return round(total / count, 2) if count else 0

@limited
def decrypt_comm_disrupted(data):
    disrupted_units = []
    for uid, cipher, sk in zip(data["UnitIDs"], data["cipher_comm_flags"], data["comm_keys"]):
        result = FeDamgard.decrypt(cipher, data["public_key"], sk, (0, 1))
        if result > 0:
            disrupted_units.append(uid)
    return disrupted_units

def launch_gui():
    limit_manager.load_state()
    limit_manager.start_runtime_monitor()
    if not limit_manager.handle_access():
        messagebox.showerror("Viewer Limit Reached", "Maximum viewer accesses reached.")
        sys.exit(1)

    verified, message = verify_uuid_binding()
    if not verified:
        messagebox.showerror("Unauthorized", f"{message}\nExiting.")
        limit_manager.save_state()
        sys.exit(1)

    set_appearance_mode("dark")
    set_default_color_theme("green")

    heading_font = ("Courier New", 26, "bold")
    subheading_font = ("Courier New", 18)
    text_font = ("Courier New", 14)

    app = CTk()
    app.title("Secure Viewer")
    app.geometry("700x720")
    app.configure(fg_color="#1b1e1c")

    frame = CTkFrame(app, fg_color="#21241e", border_color="#4a5035", border_width=1, corner_radius=12)
    frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.9)

    CTkLabel(frame, text="SECURE ACCESS INTERFACE", font=heading_font, text_color="#a9c386").pack(pady=(20, 10))

    output_box = CTkTextbox(frame, width=580, height=220, font=text_font, wrap="word",
                            text_color="#d6d6d6", fg_color="#2a2e27", border_color="#3d4236", border_width=1)
    output_box.pack(pady=10)

    status_label = CTkLabel(frame, text="", font=subheading_font, text_color="#90ee90")
    status_label.pack(pady=(5, 15))

    data = load_data()

    def run_decrypt(decrypt_func, label):
        output_box.delete("1.0", "end")
        verified, message = verify_uuid_binding()
        if verified:
            status_label.configure(text="Access Granted", text_color="#00FF04")
            result = decrypt_func(data)
            output_box.insert("end", f"{message}\n\n{label}\n")
            if isinstance(result, list):
                output_box.insert("end", "\n".join(result))
            else:
                output_box.insert("end", str(result))
        else:
            status_label.configure(text="Access Denied", text_color="#FF2B2B", font=subheading_font)
            output_box.insert("end", f"{message}\n\nAborting decryption due to failed verification.")

    button_style = {
        "font": text_font,
        "fg_color": "#90ee90",
        "hover_color": "#66e966",
        "text_color": "#1e241a",
        "width": 200,
        "corner_radius": 8
    }

    CTkButton(frame, text="Total Casualties", command=lambda: run_decrypt(decrypt_total_casualties, "Total Casualties:"), **button_style).pack(pady=5)
    CTkButton(frame, text="Total Supply Used", command=lambda: run_decrypt(decrypt_total_supplies, "Total Fuel & Ammo Used (L):"), **button_style).pack(pady=5)
    CTkButton(frame, text="Total Enemy Sightings", command=lambda: run_decrypt(decrypt_total_enemy_sightings, "Total Enemy Sightings:"), **button_style).pack(pady=5)
    CTkButton(frame, text="Average Success Rating", command=lambda: run_decrypt(decrypt_avg_success_rating, "Average Mission Success (%):"), **button_style).pack(pady=5)
    CTkButton(frame, text="Comms Disrupted", command=lambda: run_decrypt(decrypt_comm_disrupted, "Missions with Comm Disruption (UnitIDs):"),
              font=text_font, fg_color="#FECF6A", hover_color="#F4A700", text_color="#1e241a", width=200).pack(pady=5)

    CTkButton(frame, text="Close", command=lambda: [limit_manager.save_state(), app.destroy()],
              font=text_font, fg_color="#FD3434", hover_color="#E90000", text_color="black", width=200).pack(pady=20)

    app.mainloop()


if __name__ == "__main__":
    launch_gui()