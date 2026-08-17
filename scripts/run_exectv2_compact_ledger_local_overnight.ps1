# Local Compact ledger queue: Gemma 4 26B first, then Qwen 3.8 27B.
# Each model runs ExECT dev140, then aggregate-only test60.
# Resumes incomplete Compact sidecars. Does not inspect test60 rows.
# Run from any directory:
#   powershell -File scripts\run_exectv2_compact_ledger_local_overnight.ps1

param(
    [ValidateSet("gemma-dev140", "gemma-test60", "qwen-dev140", "qwen-test60")]
    [string]$From
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw "Missing $Python. Create the repo .venv first."
}

$LogDir = Join-Path $RepoRoot "scratch\local_queue\compact_ledger_local"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Log = Join-Path $LogDir "queue-$Stamp.log"

Write-Host "Checking Ollama for gemma4:26b and qwen3.8:27b..."
$tags = ollama list
if ($LASTEXITCODE -ne 0) {
    throw "ollama list failed. Start Ollama before this overnight run."
}
foreach ($tag in @("gemma4:26b", "qwen3.8:27b")) {
    if (-not ($tags | Select-String -SimpleMatch $tag)) {
        throw "$tag is not installed. Run: ollama pull $tag"
    }
}

# Per-model context is set inside the Python runner. A leftover value from
# another local script would conflict when Gemma (65536) follows Qwen (32768).
Remove-Item Env:CLINICAL_EXTRACTION_OLLAMA_NUM_CTX -ErrorAction SilentlyContinue

$cells = @(
    @{ Id = "gemma-dev140"; Model = "gemma4_26b"; Split = "dev140" },
    @{ Id = "gemma-test60"; Model = "gemma4_26b"; Split = "test60" },
    @{ Id = "qwen-dev140"; Model = "qwen38_27b"; Split = "dev140" },
    @{ Id = "qwen-test60"; Model = "qwen38_27b"; Split = "test60" }
)
if ($From) {
    $start = 0
    for ($i = 0; $i -lt $cells.Count; $i++) {
        if ($cells[$i].Id -eq $From) {
            $start = $i
            break
        }
    }
    $cells = $cells[$start..($cells.Count - 1)]
}

Write-Host "Logging to $Log"
Write-Host "Living Compact on ExECT. Gemma first, then Qwen 3.8. test60 is aggregate only."

foreach ($cell in $cells) {
    $label = "$($cell.Model) $($cell.Split)"
    Write-Host "Starting $label..."
    # Merge Python stderr as text. LiteLLM writes a harmless cost-map
    # timeout to stderr; with $ErrorActionPreference=Stop, *>&1 turns
    # that warning into a terminating NativeCommandError.
    $pyArgs = @(
        "scripts\run_exectv2_compact_ledger_local_dev140.py",
        "--model", $cell.Model,
        "--split", $cell.Split,
        "--live",
        "--timeout", "900",
        "--progress-every", "1"
    )
    $command = @($Python) + $pyArgs | ForEach-Object {
        if ($_ -match "[\s&]") { '"{0}"' -f $_ } else { $_ }
    }
    cmd /c "$($command -join ' ') 2>&1" | Tee-Object -FilePath $Log -Append
    if ($LASTEXITCODE -ne 0) {
        throw "$label Compact remasure exited $LASTEXITCODE. Re-run with -From $($cell.Id) to resume."
    }
    Write-Host "Finished $label."
}

Write-Host "Local Compact queue finished. Log: $Log"
