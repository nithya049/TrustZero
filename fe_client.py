import pickle
from mife.single.damgard import FeDamgard

# Load encrypted data
with open("fe_data.pkl", "rb") as f:
    data = pickle.load(f)

names = data["names"]
cipher_ages = data["cipher_ages"]
function_keys = data["function_keys"]
public_key = data["public_key"]

# Decrypt using function keys
eligible_names = []

for name, cipher, sk in zip(names, cipher_ages, function_keys):
    result = FeDamgard.decrypt(cipher, public_key, sk, (0, 150))
    if result > 0:
        eligible_names.append(name)

print("[CLIENT] People with age > 18:", eligible_names)

