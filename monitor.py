import os, time
from pathlib import Path

MAX_RUNS = 5
STATE_FILE = Path(__file__).parent / "viewer_state.txt"

def scramble():
    with open("fe_data.pkl", "wb") as f:
        f.write(os.urandom(2048))
    print("[MONITOR] Data scrambled due to policy violation.")

def check_usage():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            count = int(f.read())
    else:
        count = 0

    count += 1
    with open(STATE_FILE, "w") as f:
        f.write(str(count))

    if count > MAX_RUNS:
        scramble()

if __name__ == "__main__":
    check_usage()
