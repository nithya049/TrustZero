import uuid
import hashlib
import os
import sys
import pickle
import subprocess
from pathlib import Path
from mife.single.damgard import FeDamgard

AUTH_FILE = "viewer.auth"

def resource_path(filename):
    """ Get absolute path to bundled resource (works for dev and PyInstaller) """
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
        print(f"[ERROR] Unable to retrieve system UUID: {e}")
        sys.exit(1)

def hash_uuid(uuid_str):
    """SHA256 hash of the system UUID."""
    return hashlib.sha256(uuid_str.encode()).hexdigest().lower()

def verify_uuid_binding():
    uuid_str = get_system_uuid()
    uuid_hash = hash_uuid(uuid_str)
    auth_file = get_auth_path()

    if not os.path.exists(auth_file):
        print("[ERROR] UUID binding file missing.")
        sys.exit(1)

    with open(auth_file, "r") as f:
        stored_hash = f.read().strip().lower()
        if stored_hash != uuid_hash:
            print("[ERROR] Device not authorized. UUID mismatch.")
            sys.exit(1)
        else:
            print("[OK] Device verified.")

def decrypt_and_display():
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

    print("[CLIENT] People with age > 18:", eligible_names)

if __name__ == "__main__":
    verify_uuid_binding()
    decrypt_and_display()
