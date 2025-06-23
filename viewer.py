from customtkinter import *
import os
import sys
import hashlib
import pickle
import subprocess
from pathlib import Path
from mife.single.damgard import FeDamgard

AUTH_FILE = "viewer.auth"

def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.abspath(filename)

def get_auth_path():
    return os.path.join(os.getenv("LOCALAPPDATA"), "SecureViewer", AUTH_FILE)

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
    except Exception as e:
        return None

def hash_uuid(uuid_str):
    return hashlib.sha256(uuid_str.encode()).hexdigest().lower()

def verify_uuid_binding():
    uuid_str = get_system_uuid()
    if not uuid_str:
        return False, "Unable to retrieve system UUID."
    
    uuid_hash = hash_uuid(uuid_str)
    auth_file = get_auth_path()

    if not os.path.exists(auth_file):
        return False, "UUID binding file missing."

    with open(auth_file, "r") as f:
        stored_hash = f.read().strip().lower()
        if stored_hash != uuid_hash:
            return False, "Device not authorized. UUID mismatch."
    
    return True, "Device verified."

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
        status, message = verify_uuid_binding()

        if status:
            status_label.configure(text="Access Granted", text_color="#00FF04",font=subheading_font)
        else:
            status_label.configure(text="Access Denied", text_color="#FF2B2B",font=subheading_font)

        output_box.insert("end", f"{message}\n\n")

        if status:
            result = decrypt_data()
            output_box.insert("end", "People with age > 18:\n")
            output_box.insert("end", "\n".join(result))
        else:
            output_box.insert("end", "Aborting decryption due to failed verification.")

    run_button = CTkButton(
        app,
        text="Verify & Decrypt",
        command=on_run,
        font=("Trebuchet MS", 19),
        fg_color="#87F1FF",
        hover_color="#42E0F4",
        text_color="black"
    )
    run_button.pack(pady=15)

    CTkButton(app, text="Close", command=app.destroy, font=("Trebuchet MS", 16), fg_color="#FD3434",
        hover_color="#E90000",
        text_color="black").pack(pady=10)

    app.mainloop()


if __name__ == "__main__":
    launch_gui()