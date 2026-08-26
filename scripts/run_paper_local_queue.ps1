# Remaining local paper cells for this Ollama machine.
# Hosted models (Grok, Gemini, DeepSeek, GPTs) are out of scope.
#
# Already on this device (do not requeue):
#   Gemma Compact hybrid both splits
#   Qwen Compact hybrid both splits
#   Gemma and Qwen gan_llm_extract_raw / gan_llm_with_rules
#   Gemma Compact extract (exect_llm_only / exect_llm_extract_filtered)
#   Qwen Compact extract leftover 67/140 (wrong prompt; do not resume)
#
# Cell 3 extract is now:
#   Gan   gan_llm_extract
#   ExECT exect_llm_extract  (inventory prompt + inventory F1)
# Compact exect_llm_only is a Gemini ablation only. Do not queue it.
#
# Queue. Qwen stays resident, then Gemma:
#   1. Qwen  exect_llm_extract  dev140
#   2. Qwen  exect_llm_extract  test60
#   3. Qwen  gan_llm_extract    dev750
#   4. Qwen  gan_llm_extract    test450
#   5. Gemma exect_llm_extract  dev140
#   6. Gemma exect_llm_extract  test60
#   7. Gemma gan_llm_extract    dev750
#   8. Gemma gan_llm_extract    test450
#
# Holdout splits stay aggregate-only. Re-run the same script to resume.
#   powershell -File scripts\run_paper_local_queue.ps1
#   powershell -File scripts\run_paper_local_queue.ps1 -StartAt 5

param(
    [int]$StartAt = 1,
    [string]$ApiBase = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw "Missing $Python. Create the repo .venv first."
}

$LogDir = Join-Path $RepoRoot "scratch\local_queue\paper_local"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Log = Join-Path $LogDir "queue-$Stamp.log"

function Write-Log {
    param([string]$Message)
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
    Write-Host $line
    Add-Content -Path $Log -Value $line
}

function Assert-OllamaTag {
    param([string]$Tag)
    $tags = ollama list
    if ($LASTEXITCODE -ne 0) {
        throw "ollama list failed. Start Ollama before this queue."
    }
    if (-not ($tags | Select-String -SimpleMatch $Tag)) {
        throw "$Tag is not installed. Run: ollama pull $Tag"
    }
}

$Jobs = @(
    @{
        Id = 1
        Method = "exect_llm_extract"
        Model = "qwen38_27b"
        Split = "dev140"
        Tag = "qwen3.8:27b"
        Ctx = "32768"
        StopBefore = @("gemma4:26b")
    }
    @{
        Id = 2
        Method = "exect_llm_extract"
        Model = "qwen38_27b"
        Split = "test60"
        Tag = "qwen3.8:27b"
        Ctx = "32768"
        StopBefore = @()
    }
    @{
        Id = 3
        Method = "gan_llm_extract"
        Model = "qwen38_27b"
        Split = "dev750"
        Tag = "qwen3.8:27b"
        Ctx = "32768"
        StopBefore = @()
    }
    @{
        Id = 4
        Method = "gan_llm_extract"
        Model = "qwen38_27b"
        Split = "test450"
        Tag = "qwen3.8:27b"
        Ctx = "32768"
        StopBefore = @()
    }
    @{
        Id = 5
        Method = "exect_llm_extract"
        Model = "gemma4_26b"
        Split = "dev140"
        Tag = "gemma4:26b"
        Ctx = "65536"
        StopBefore = @("qwen3.8:27b")
    }
    @{
        Id = 6
        Method = "exect_llm_extract"
        Model = "gemma4_26b"
        Split = "test60"
        Tag = "gemma4:26b"
        Ctx = "65536"
        StopBefore = @()
    }
    @{
        Id = 7
        Method = "gan_llm_extract"
        Model = "gemma4_26b"
        Split = "dev750"
        Tag = "gemma4:26b"
        Ctx = "65536"
        StopBefore = @()
    }
    @{
        Id = 8
        Method = "gan_llm_extract"
        Model = "gemma4_26b"
        Split = "test450"
        Tag = "gemma4:26b"
        Ctx = "65536"
        StopBefore = @()
    }
)

if ($StartAt -lt 1 -or $StartAt -gt $Jobs.Count) {
    throw "StartAt must be between 1 and $($Jobs.Count)."
}

Write-Log "Paper local live queue (inventory extract + codebook extract). Log: $Log"
Write-Log "Do not resume the Qwen Compact leftover. Gemma Compact extract is not cell 3."

foreach ($job in $Jobs) {
    if ($job.Id -lt $StartAt) {
        Write-Log "Skipping job $($job.Id) $($job.Model) $($job.Method) $($job.Split) (StartAt=$StartAt)."
        continue
    }

    Assert-OllamaTag $job.Tag
    foreach ($resident in $job.StopBefore) {
        Write-Log "Stopping $resident before $($job.Tag)."
        ollama stop $resident | Out-Null
    }

    Remove-Item Env:CLINICAL_EXTRACTION_OLLAMA_NUM_CTX -ErrorAction SilentlyContinue
    $env:CLINICAL_EXTRACTION_OLLAMA_NUM_CTX = $job.Ctx

    Write-Log "Starting job $($job.Id): $($job.Model) $($job.Method) $($job.Split)"
    $paperArgs = @(
        "-m", "clinical_extraction.paper",
        "run",
        "--method", $job.Method,
        "--model", $job.Model,
        "--split", $job.Split,
        "--live",
        "--timeout", "900",
        "--progress-every", "1"
    )
    if ($ApiBase) {
        $paperArgs += @("--api-base", $ApiBase)
    }

    & $Python @paperArgs *>&1 | Tee-Object -FilePath $Log -Append
    if ($LASTEXITCODE -ne 0) {
        throw "Job $($job.Id) $($job.Model) $($job.Method) $($job.Split) exited $LASTEXITCODE. Re-run with -StartAt $($job.Id) to resume."
    }
    Write-Log "Finished job $($job.Id)."
}

Remove-Item Env:CLINICAL_EXTRACTION_OLLAMA_NUM_CTX -ErrorAction SilentlyContinue
Write-Log "Local paper live queue finished. Log: $Log"
Write-Log "Do not inspect test450 or test60 rows. Promotion into paper_experiments/ is a later step."
