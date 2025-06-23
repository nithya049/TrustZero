# Integrated viewer.py with one-time token activation, UUID binding, and .dll-based hidden auth storage
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


def embed_auth_in_dll(uuid_hash):
    try:
        os.makedirs(os.path.dirname(AUTH_CARRIER), exist_ok=True)
        # Prevent multiple writes
        if os.path.exists(AUTH_CARRIER):
            with open(AUTH_CARRIER, "rb") as f:
                content = f.read()
                if (MARKER + uuid_hash.encode()) in content:
                    return  # Already embedded
        with open(AUTH_CARRIER, "ab") as f:
            f.write(MARKER + uuid_hash.encode())
    except Exception as e:
        print(f"[ERROR] Could not embed auth in dll: {e}")
        sys.exit(1)


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


def ask_token_gui():
    set_appearance_mode("dark")
    set_default_color_theme("blue")

    class TokenDialog(CTk):
        def __init__(self):
            super().__init__()
            self.title("Enter Activation Token")
            self.geometry("400x200")
            self.resizable(False, False)

            self.token_value = None

            CTkLabel(self, text="Activation Required", font=("Trebuchet MS", 22, "bold")).pack(pady=(20, 10))
            CTkLabel(self, text="Enter your one-time activation token:", font=("Trebuchet MS", 15)).pack(pady=(0, 5))

            self.entry = CTkEntry(self, width=300, font=("Trebuchet MS", 14))
            self.entry.pack(pady=(0, 15))
            self.entry.focus()

            CTkButton(self, text="Submit", command=self.submit_token, font=("Trebuchet MS", 14),
                      fg_color="#87F1FF", hover_color="#42E0F4", text_color="black").pack(pady=10)

        def submit_token(self):
            self.token_value = self.entry.get()
            self.destroy()

    dialog = TokenDialog()
    dialog.mainloop()
    return dialog.token_value


def decrypt_data():
    try:
        with open(resource_path("fe_data.pkl"), "rb") as f:
            data = pickle.load(f)
        names = data["names"]
        cipher_ages = data["cipher_ages"]
        function_keys = data["function_keys"]
        public_key = data["public_key"]
        eligible_names = []
        for name, cipher, sk in zip(names, cipher_ages, function_keys):
            result = FeDamgard.decrypt(cipher, public_key, sk, (0, 150))
            if result > 0:
                eligible_names.append(name)
        return eligible_names
    except Exception as e:
        return [f"Error decrypting data: {e}"]


def launch_gui():
    # Always ask for token
    token = ask_token_gui()
    if not token:
        messagebox.showerror("Activation Failed", "No token entered. Exiting.")
        sys.exit(1)

    uuid = get_system_uuid()
    if not uuid:
        messagebox.showerror("Activation Failed", "Could not retrieve device UUID.")
        sys.exit(1)

    try:
        response = requests.post(SERVER_URL, json={"token": token, "uuid": uuid})
        data = response.json()
        if data.get("status") == "ok":
            uuid_hash = hash_uuid(uuid)
            embed_auth_in_dll(uuid_hash)
            messagebox.showinfo("Activation Successful", "Device successfully activated.")
        else:
            messagebox.showerror("Activation Failed", f"Reason: {data.get('reason', 'Unknown')}")
            sys.exit(1)
    except Exception as e:
        messagebox.showerror("Activation Error", f"Request failed: {e}")
        sys.exit(1)

    # GUI after activation
    set_appearance_mode("dark")
    set_default_color_theme("blue")

    heading_font = ("Trebuchet MS", 30, "bold")
    subheading_font = ("Trebuchet MS", 20)
    text_font = ("Trebuchet MS", 16)

    app = CTk()
    app.title("Secure Viewer")
    app.geometry("600x460")

    title_label = CTkLabel(app, text="Secure Viewer", font=heading_font, text_color="#A9F3FD")
    title_label.pack(pady=20)

    output_box = CTkTextbox(app, width=500, height=200, font=text_font, wrap="word")
    output_box.pack(pady=10)

    status_label = CTkLabel(app, text="", font=subheading_font)
    status_label.pack(pady=(5, 0))

    def on_run():
        output_box.delete("1.0", "end")
        verified, message = verify_uuid_binding()

        if verified:
            status_label.configure(text="Access Granted", text_color="#00FF04", font=subheading_font)
            result = decrypt_data()
            output_box.insert("end", f"{message}\n\n")
            output_box.insert("end", "People with age > 18:\n")
            output_box.insert("end", "\n".join(result))
        else:
            status_label.configure(text="Access Denied", text_color="#FF2B2B", font=subheading_font)
            output_box.insert("end", f"{message}\n\n")
            output_box.insert("end", "Aborting decryption due to failed verification.")

    CTkButton(app, text="Verify & Decrypt", command=on_run, font=("Trebuchet MS", 19),
              fg_color="#87F1FF", hover_color="#42E0F4", text_color="black").pack(pady=15)

    CTkButton(app, text="Close", command=app.destroy, font=("Trebuchet MS", 16),
              fg_color="#FD3434", hover_color="#E90000", text_color="black").pack(pady=10)

    app.mainloop()


if __name__ == "__main__":
    launch_gui()
