$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Venv = Join-Path $Root ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    py -3.11 -m venv $Venv
}
& $Python -m pip install --requirement (Join-Path $Root "requirements.lock")
Write-Host "Setup complete. Copy .env.example to .env, edit it, then run:"
Write-Host ".\.venv\Scripts\python.exe run.py check"
