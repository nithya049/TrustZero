
# TrustZero – Secure Offline Functional Encryption Viewer

TrustZero is a secure, tamper-resistant data inspection system designed for offline environments. It enables recipients to perform *only limited, pre-approved computations* on encrypted data using **Functional Encryption (FE)**. The system enforces strict access policies such as **one-time installation**, **device binding**, **usage limits**, and **offline-only decryption**. It’s ideal for high-security and air-gapped scenarios.



## Key Features

### Secure Installation and Device Binding
- Delivered as a one-time-use installer (`SecureViewerInstaller.exe`) via NSIS.
- Prompts for a one-time OTP, verified by `validate_token.exe`.
- Runs `bind_uuid.ps1` to bind the installation to a device UUID.
- Stores a hashed UUID in a hidden file (`winmm.dll`) under `AppData\Microsoft\CLR\Cache`.
- Installer self-deletes and cannot be reused or copied.
- Fully functional offline post-installation.

### Functional Encryption-Based Viewer
- The viewer (`viewer.exe`) validates device authorization on launch.
- Loads the encrypted dataset (`fe_military.pkl`) with FeDDH-based ciphertexts.
- Supports FE-decryption for approved inner-product computations only.
- Prevents full data exposure or arbitrary queries.

### Function-Specific Decryption
Pre-defined decryption functions include:
- Total casualties
- Total supplies used
- Total enemy sightings
- Average mission success
- Disrupted communications count

### Offline Usage Monitoring
Managed via `limit_manager.py`, it enforces:
- Maximum runtime (e.g., 60 minutes)
- Limited number of viewer launches (e.g., max 5)
- Function-specific usage limits
- Stores limits in a hidden tracking file (`winmm.dat`)

### Tamper Resistance
- Device UUID binding
- Usage and runtime limitation
- Obfuscated state files


## Repository Structure
fe_server.py            → Encrypts mission data (CSV) using FE

viewer.py               → Secure offline viewer with GUI

validate_token.py       → OTP verification at installation

limit_manager.py        → Access/runtime tracking logic

bind_uuid.ps1           → Retrieves device UUID

fe_military.pkl         → Pickled encrypted dataset

winmm.dll               → Hidden UUID auth hash file

winmm.dat               → Usage state tracking file

installer.nsi           → NSIS script to generate installer

SecureViewerInstaller.exe → Final installer output



## Installation & Usage

### 1. Generate Encrypted Dataset
```bash
   python fe_server.py
```
### 2. Compile `.spec` into Executable with PyInstaller

Ensure you have a `viewer.spec` and `validate_token.spec` file ready. To build the `.exe`:

```bash
    pyinstaller viewer.spec
    pyinstaller validate_token.spec
```

This generates:

> - `dist/viewer/viewer.exe` 
> - `dist/viewer/validate_token.exe`
> - `build/` (intermediate build files)

Make sure any required files (e.g., `.pem`, `.auth`, configs) are bundled via the spec.

### 3. Build the Installer
1. Open NSIS > Compile NSI scripts
2. Load install.nsi
3. Click Compile
4. Output: SecureViewerInstaller.exe

### 4. Visit Secure Activation Server
Leave the activation server running throughout using the command:
```bash
cd activation_server/
python activation_server.py
```
Now, open the secure activation server at `localhost:5000/get_token` and enter the pre-approved email-id.
The OTP will be sent to the id.

### 5. Install the Viewer
- Run SecureViewerInstaller.exe

- Enter your OTP when prompted

- Device UUID is bound and .auth files are dropped in hidden location

- Installer self-destructs after uninstallation to prevent reinstallation or reuse

### 6. Run Viewer
```bash
./viewer.exe
```
- Performs local, controlled decryption on encrypted data

- Only pre-approved queries allowed (e.g., totals, averages, thresholds)

- Fully functional offline, no server or cloud access required

## Use Case Scenarios
- Military: Decrypt mission-specific stats (casualties, supplies) securely on authorized devices.

## Dependencies
- Python 3.10+

- PyMIFE (DDH-based FE)

- cryptography, customtkinter, pyinstaller, NSIS

- Windows environment recommended

## License
This project is licensed under the MIT License. See the LICENSE file for details.
