# Get system UUID
$uuid = (Get-WmiObject Win32_ComputerSystemProduct).UUID

# Validate UUID
if ($uuid -and $uuid -notmatch "^(00000000|FFFFFFFF)-") {
    # Compute SHA-256 hash of UUID
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($uuid)
    $sha256 = New-Object System.Security.Cryptography.SHA256Managed
    $hashBytes = $sha256.ComputeHash($bytes)
    $hash = [System.BitConverter]::ToString($hashBytes) -replace "-", ""

    # Define auth storage path
    $authPath = "$env:LOCALAPPDATA\Microsoft\CLR\Cache"
    $carrierFile = "$authPath\winmm.dll"

    if (-not (Test-Path $authPath)) {
        New-Item -ItemType Directory -Path $authPath -Force | Out-Null
    }

    # Create dummy file with MZ header if it doesn't exist
    if (-not (Test-Path $carrierFile)) {
        [System.IO.File]::WriteAllBytes($carrierFile, [System.Text.Encoding]::ASCII.GetBytes("MZ"))
    }

    # Append marker + hash to dummy file
    $marker = [System.Text.Encoding]::UTF8.GetBytes("--AUTH--")
    $hashBytesFinal = [System.Text.Encoding]::UTF8.GetBytes($hash)

    $fs = [System.IO.File]::Open($carrierFile, [System.IO.FileMode]::Append)
    $fs.Write($marker, 0, $marker.Length)
    $fs.Write($hashBytesFinal, 0, $hashBytesFinal.Length)
    $fs.Close()

    # Hide the file (hidden + system)
    attrib +h +s $carrierFile

    Write-Output "Device UUID hash hidden in $carrierFile"
} else {
    Write-Error "Invalid or missing UUID. Cannot bind device."
    exit 1
}
