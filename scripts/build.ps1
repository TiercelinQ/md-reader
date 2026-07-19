# Build MD Reader (.exe) via PyInstaller.
# Prérequis : venv activé avec requirements.txt + requirements-dev.txt installés.
# Usage : powershell -ExecutionPolicy Bypass -File scripts\build.ps1

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "Build MD Reader (.exe)..."
python -m PyInstaller build.spec --noconfirm

Write-Host "Terminé. Exécutable dans dist\MD Reader.exe"
