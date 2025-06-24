import sys
import requests
import subprocess

def get_uuid():
    try:
        result = subprocess.check_output([
            "powershell", "-Command",
            "(Get-WmiObject Win32_ComputerSystemProduct).UUID"
        ])
        uuid = result.decode().strip()
        return uuid
    except Exception as e:
        return None

def main():
    if len(sys.argv) != 2:
        return

    token = sys.argv[1].strip().upper()

    uuid = get_uuid()
    if not uuid:
        return

    try:
        response = requests.post("http://localhost:5000/validate_token", json={
            "token": token,
            "uuid": uuid
        })

        if response.status_code == 200:
            print("ok")
        else:
            print("error")
    except Exception as e:
        print("error")

if __name__ == "__main__":
    main()
