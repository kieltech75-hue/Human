param(
    [Parameter(Mandatory=$true)]
    [string]$BinaryPath,
    [Parameter(Mandatory=$true)]
    [string]$OutputPath
)

$binary = Resolve-Path $BinaryPath
$targetDir = Split-Path -Parent $OutputPath
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

$installer = @"
@echo off
setlocal
set "BIN=%~dp0"
set "TARGET=%BIN%human.exe"
copy /Y "$binary" "%TARGET%"
setx PATH "%PATH%;%BIN%"
@echo Installed Human to %TARGET%
"@

Set-Content -Path $OutputPath -Value $installer -Encoding Ascii
