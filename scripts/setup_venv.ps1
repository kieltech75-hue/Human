# One-command PowerShell script to recreate the venv and install requirements
# Run from the repo root: .\scripts\setup_venv.ps1

param(
    [string]$VenvPath = ".venv",
    [switch]$Force
)

Write-Host "Recreating virtual environment at $VenvPath"

if (Test-Path $VenvPath) {
    if (-not $Force) {
        Write-Host "$VenvPath already exists. Use -Force to remove and recreate." -ForegroundColor Yellow
        Exit 1
    }
    Remove-Item -Recurse -Force $VenvPath
}

python -m venv $VenvPath
if ($LASTEXITCODE -ne 0) { Write-Host "Failed to create venv" -ForegroundColor Red; Exit 2 }

# Determine python executable inside venv depending on platform
if ($IsWindows) {
    $py = Join-Path $VenvPath "Scripts\python.exe"
} else {
    $py = Join-Path $VenvPath "bin/python"
}

& $py -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { Write-Host "Failed to upgrade pip" -ForegroundColor Red; Exit 3 }

& $py -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { Write-Host "Failed to install requirements" -ForegroundColor Red; Exit 4 }

if ($IsWindows) {
    Write-Host "Virtualenv created and dependencies installed. Activate with:`n.\$VenvPath\Scripts\Activate" -ForegroundColor Green
} else {
    Write-Host "Virtualenv created and dependencies installed. Activate with:`nsource $VenvPath/bin/activate" -ForegroundColor Green
}
