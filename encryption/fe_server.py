import pandas as pd
import pickle
import time
from mife.single.selective.ddh import FeDDH

start_time = time.time()
chunk_size = 500

key = FeDDH.generate(500)  # Assuming 500-dim vector encryption supported
public_key = key.get_public_key()

# Precompute sum key (dot product with all 1s)
sum_vector = [1] * chunk_size
sum_key_casualties = FeDDH.keygen(sum_vector, key)
sum_key_supplies = FeDDH.keygen(sum_vector, key)
sum_key_sightings = FeDDH.keygen(sum_vector, key)
sum_key_success = FeDDH.keygen(sum_vector, key)

# Store encrypted vectors
unit_ids_all = []
cipher_casualties = []
cipher_supplies = []
cipher_sightings = []
cipher_success = []
cipher_comm_flags = []
comm_keys = []

encryption_start = time.time()

for chunk in pd.read_csv("mission_briefing.csv", chunksize=chunk_size):
    n = len(chunk)  # May be <500 in last chunk
    unit_ids_all.extend(chunk["UnitID"].tolist())

    # Convert to integer vectors
    casualties_vec = chunk["Casualties"].astype(int).tolist()
    supply_vec = chunk["SupplyUsed(L)"].astype(int).tolist()
    sightings_vec = chunk["EnemySightings"].astype(int).tolist()
    success_vec = chunk["SuccessRating"].astype(int).tolist()
    comm_flags_vec = chunk["CommDisrupted"].str.strip().str.lower().eq("yes").astype(int).tolist()

    # Encrypt vectors
    cipher_casualties.append(FeDDH.encrypt(casualties_vec, key))
    cipher_supplies.append(FeDDH.encrypt(supply_vec, key))
    cipher_sightings.append(FeDDH.encrypt(sightings_vec, key))
    cipher_success.append(FeDDH.encrypt(success_vec, key))
    cipher_comm_flags.append(FeDDH.encrypt(comm_flags_vec, key))

    # Create access vector for keygen (binary vector)
    comm_keys.append(FeDDH.keygen(comm_flags_vec, key))

encryption_end = time.time()

data = {
    "UnitIDs": unit_ids_all,
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
