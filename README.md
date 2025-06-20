# TrustZero

This guide explains how to:

1. ✅ Compile a `.spec` file into a standalone `.exe` using **PyInstaller**.
2. 📦 Package the `.exe` using **NSIS** to create a Windows installer.

---

## 📋 Prerequisites

- Python 3.x installed and added to PATH
- `pyinstaller` installed:
  ```bash
  pip install pyinstaller
  ```
- NSIS installed: [Download NSIS](https://nsis.sourceforge.io/Download)

---

## 🛠 Step 1: Compile `.spec` into Executable with PyInstaller

Ensure you have a `viewer.spec` file ready. To build the `.exe`:

```bash
pyinstaller --onefile --windowed --add-data "fe_data.pkl;." viewer.py
```

> This generates:
>
> - `dist/viewer/viewer.exe` (your final binary)
> - `build/` (intermediate build files)

Make sure any required files (e.g., `.pem`, `.auth`, configs) are bundled via the spec.

## 📝 Step 2: Build the Installer
1. Open NSIS > Compile NSI scripts
2. Load install.nsi
3. Click Compile
4. Output: SecureViewerInstaller.exe
