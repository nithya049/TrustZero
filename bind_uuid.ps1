# Get system UUID
$uuid = (Get-WmiObject Win32_ComputerSystemProduct).UUID

# Validate UUID
if ($uuid -and $uuid -notmatch "^(00000000|FFFFFFFF)-") {
    # Compute SHA-256 hash of UUID
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($uuid)
    $sha256 = New-Object System.Security.Cryptography.SHA256Managed
    $hashBytes = $sha256.ComputeHash($bytes)
    $hash = [System.BitConverter]::ToString($hashBytes) -replace "-", ""

    # Define auth path
    $authPath = "$env:LOCALAPPDATA\SecureViewer"

    # Ensure directory exists
    if (-not (Test-Path $authPath)) {
        New-Item -ItemType Directory -Path $authPath -Force | Out-Null
    }

    # Write hash to viewer.auth
    Set-Content -Path "$authPath\viewer.auth" -Value $hash
    Write-Output "Device UUID hash bound at $authPath\viewer.auth"
} else {
    Write-Error "Invalid or missing UUID. Cannot bind device."
    exit 1
}
