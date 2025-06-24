import pandas as pd
import pickle
from mife.single.damgard import FeDamgard

# Load CSV
data_df = pd.read_csv('data.csv')
names = data_df['name'].tolist()
ages = data_df['age'].tolist()
salaries = data_df['salary'].tolist()

# FE Setup
key = FeDamgard.generate(1)
public_key = key.get_public_key()

# Encrypt ages and generate age-related keys
cipher_ages = []
age_keys = []

for age in ages:
    cipher = FeDamgard.encrypt([age], key)
    cipher_ages.append(cipher)
    y = [1 if age > 18 else 0]  # Function vector: output 1 if age > 18
    sk = FeDamgard.keygen(y, key)
    age_keys.append(sk)

# Encrypt salaries and generate salary-related keys
cipher_salaries = []
salary_keys = []

for salary in salaries:
    cipher = FeDamgard.encrypt([salary], key)
    cipher_salaries.append(cipher)
    y = [1 if salary > 45 else 0]  # Function vector: output 1 if salary > 45
    sk = FeDamgard.keygen(y, key)
    salary_keys.append(sk)

# Generate sum key for total salary
y_sum = [1]  # Sum all salaries
sum_key = FeDamgard.keygen(y_sum, key)

# Save to file outside encryption folder
data = {
    "names": names,
    "cipher_ages": cipher_ages,
    "function_keys": age_keys,
    "cipher_salaries": cipher_salaries,
    "salary_keys": salary_keys,
    "sum_key": sum_key,
    "public_key": public_key
}

with open("../fe_data.pkl", "wb") as f:
    pickle.dump(data, f)

print("[SERVER] Data encrypted and saved to ../fe_data.pkl")
