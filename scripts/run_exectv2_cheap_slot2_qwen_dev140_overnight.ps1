# Overnight Qwen 3.8 27B remasure of cheap-stack slot 2 on ExECT dev140.
# Resumes a partial sidecar. Does not complete the v0.9.24 control first.
# Run from any directory:
#   powershell -File scripts\run_exectv2_cheap_slot2_qwen_dev140_overnight.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw "Missing $Python. Create the repo .venv first."
}

$LogDir = Join-Path $RepoRoot "scratch\local_queue\cheap_slot2_qwen_dev140"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Log = Join-Path $LogDir "slot2-$Stamp.log"

Write-Host "Checking Ollama for qwen3.8:27b..."
$tags = ollama list
if ($LASTEXITCODE -ne 0) {
    throw "ollama list failed. Start Ollama before this overnight run."
}
if (-not ($tags | Select-String -SimpleMatch "qwen3.8:27b")) {
    throw "qwen3.8:27b is not installed. Run: ollama pull qwen3.8:27b"
}

$env:CLINICAL_EXTRACTION_OLLAMA_NUM_CTX = "32768"
Write-Host "Logging to $Log"
Write-Host "Slot 2 only. v0.9.24 sidecar completion is later and not required."

& $Python "scripts\run_exectv2_v0924_cheap_slot2_dev140.py" `
    --model qwen `
    --live `
    --timeout 900 `
    --progress-every 1 *>&1 | Tee-Object -FilePath $Log

if ($LASTEXITCODE -ne 0) {
    throw "Qwen slot-2 remasure exited $LASTEXITCODE. Re-run this script to resume."
}

Write-Host "Qwen slot-2 remasure finished. Log: $Log"
