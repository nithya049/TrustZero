import pandas as pd
import pickle
from mife.single.damgard import FeDamgard

# Load CSV
df = pd.read_csv('people.csv')
names = df['name'].tolist()
ages = df['age'].tolist()

# FE Setup
key = FeDamgard.generate(1)
public_key = key.get_public_key()

# Encrypt ages and generate function keys
cipher_ages = []
function_keys = []

for age in ages:
    cipher = FeDamgard.encrypt([age], key)
    cipher_ages.append(cipher)

    # Function vector: output 1 if age > 18
    y = [1 if age > 18 else 0]
    sk = FeDamgard.keygen(y, key)
    function_keys.append(sk)

# Save to file
data = {
    "names": names,
    "cipher_ages": cipher_ages,
    "function_keys": function_keys,
    "public_key": public_key
}

with open("fe_data.pkl", "wb") as f:
    pickle.dump(data, f)

print("[SERVER] Data encrypted and saved to fe_data.pkl")
