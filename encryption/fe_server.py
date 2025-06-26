import pandas as pd
import pickle
from mife.single.damgard import FeDamgard

df = pd.read_csv("mission_briefing.csv")
key = FeDamgard.generate(1)
public_key = key.get_public_key()

cipher_casualties = []
cipher_supplies = []
cipher_sightings = []
cipher_success = []
cipher_comm_flags = []
comm_keys = []

sum_vector = [1]
sum_key_casualties = FeDamgard.keygen(sum_vector, key)
sum_key_supplies = FeDamgard.keygen(sum_vector, key)
sum_key_sightings = FeDamgard.keygen(sum_vector, key)
sum_key_success = FeDamgard.keygen(sum_vector, key)

for i in range(len(df)):
    casualties = [int(df.loc[i, "Casualties"])]
    supply = [int(df.loc[i, "SupplyUsed(L)"])]
    sightings = [int(df.loc[i, "EnemySightings"])]
    success = [int(df.loc[i, "SuccessRating"])]
    comm_disrupted = 1 if df.loc[i, "CommDisrupted"].strip().lower() == "yes" else 0

    cipher_casualties.append(FeDamgard.encrypt(casualties, key))
    cipher_supplies.append(FeDamgard.encrypt(supply, key))
    cipher_sightings.append(FeDamgard.encrypt(sightings, key))
    cipher_success.append(FeDamgard.encrypt(success, key))

    cipher_comm_flags.append(FeDamgard.encrypt([comm_disrupted], key))
    sk = FeDamgard.keygen([1 if comm_disrupted else 0], key)
    comm_keys.append(sk)

data = {
    "UnitIDs": df["UnitID"].tolist(),
    "cipher_casualties": cipher_casualties,
    "sum_key_casualties": sum_key_casualties,
    "cipher_supplies": cipher_supplies,
    "sum_key_supplies": sum_key_supplies,
    "cipher_sightings": cipher_sightings,
    "sum_key_sightings": sum_key_sightings,
    "cipher_success": cipher_success,
    "sum_key_success": sum_key_success,
    "cipher_comm_flags": cipher_comm_flags,
    "comm_keys": comm_keys,
    "public_key": public_key
}

with open("../fe_military.pkl", "wb") as f:
    pickle.dump(data, f)

print("[SERVER] Data encrypted and saved to ../fe_data.pkl")
