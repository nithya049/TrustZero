import time, functools, sys, threading, json, os

# === Configuration ===

MAX_CALLS_PER_FUNC = {
    'verify_user': 2,
    'decrypt_file': 10,
    'decrypt_age_over_18': 3,
    'decrypt_salary_over_45': 3,
    'decrypt_salary_sum': 3
}
MAX_VIEWER_SECONDS = 36000  # 60 minutes TIMEEEEEE
MAX_VIEWER_ACCESSES = 7    # 100
STATE_FILE = "limit_state.json"

# === Runtime State ===
FUNC_CALLS = {}
START_TIME = time.time()
viewer_access_count = 0


# === Load and Save Persistent State ===
def save_state():
    with open(STATE_FILE, "w") as f:
        json.dump({
            'FUNC_CALLS': FUNC_CALLS,
            'viewer_access_count': viewer_access_count,
            'start_time': START_TIME
        }, f)

def load_state():
    global FUNC_CALLS, viewer_access_count, START_TIME
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            FUNC_CALLS.update(data.get('FUNC_CALLS', {}))
            viewer_access_count = data.get('viewer_access_count', 0)
            START_TIME = data.get('start_time', time.time())


# === Runtime Monitor (Viewer Time Limit) ===
def _runtime_monitor():
    while True:
        elapsed = time.time() - START_TIME
        if elapsed > MAX_VIEWER_SECONDS:
            print("[LIMIT] Viewer runtime exceeded. Exiting.")
            save_state()
            sys.exit(1)
        time.sleep(5)

def start_runtime_monitor():
    threading.Thread(target=_runtime_monitor, daemon=True).start()


# === Function Call Limiter ===
def limited(func):
    name = func.__name__
    FUNC_CALLS.setdefault(name, 0)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if FUNC_CALLS[name] >= MAX_CALLS_PER_FUNC.get(name, float('inf')):
            print(f"[BLOCKED] Function '{name}' call limit reached.")
            return None
        FUNC_CALLS[name] += 1
        return func(*args, **kwargs)

    return wrapper


# === Viewer Access Limiter ===
def handle_access():
    global viewer_access_count
    if viewer_access_count >= MAX_VIEWER_ACCESSES:
        print("[BLOCKED] Viewer access limit reached.")
        return False
    viewer_access_count += 1
    return True
