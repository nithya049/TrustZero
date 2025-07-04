import pandas as pd
import pickle
import time
from mife.single.damgard import FeDamgard
from mife.single.selective.ddh import FeDDH

start_time = time.time()

df = pd.read_csv("mission_briefing.csv")
key = FeDDH.generate(1)
public_key = key.get_public_key()

cipher_casualties = []
cipher_supplies = []
cipher_sightings = []
cipher_success = []
cipher_comm_flags = []
comm_keys = []

sum_vector = [1]
sum_key_casualties = FeDDH.keygen(sum_vector, key)
sum_key_supplies = FeDDH.keygen(sum_vector, key)
sum_key_sightings = FeDDH.keygen(sum_vector, key)
sum_key_success = FeDDH.keygen(sum_vector, key)

encryption_start = time.time()

for i in range(len(df)):
    casualties = [int(df.loc[i, "Casualties"])]
    supply = [int(df.loc[i, "SupplyUsed(L)"])]
    sightings = [int(df.loc[i, "EnemySightings"])]
    success = [int(df.loc[i, "SuccessRating"])]
    comm_disrupted = 1 if df.loc[i, "CommDisrupted"].strip().lower() == "yes" else 0

    cipher_casualties.append(FeDDH.encrypt(casualties, key))
    cipher_supplies.append(FeDDH.encrypt(supply, key))
    cipher_sightings.append(FeDDH.encrypt(sightings, key))
    cipher_success.append(FeDDH.encrypt(success, key))

    cipher_comm_flags.append(FeDDH.encrypt([comm_disrupted], key))
    sk = FeDDH.keygen([1 if comm_disrupted else 0], key)
    comm_keys.append(sk)

encryption_end = time.time()

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

end_time = time.time()

print("[SERVER] Data encrypted and saved to ../fe_military.pkl")
print(f"[TIMING] Total time: {end_time - start_time:.4f} seconds")
print(f"[TIMING] Encryption loop time: {encryption_end - encryption_start:.4f} seconds")
