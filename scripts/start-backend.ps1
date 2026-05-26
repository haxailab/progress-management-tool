$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$venvDir = Join-Path $backendDir ".venv"
$pythonExe = Join-Path $venvDir "Scripts\python.exe"

Set-Location $backendDir

if (-not (Test-Path -LiteralPath $pythonExe)) {
    python -m venv .venv
}

& $pythonExe -m pip install --disable-pip-version-check -r requirements.txt
& $pythonExe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
