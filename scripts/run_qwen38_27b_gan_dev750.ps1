$ErrorActionPreference = "Continue"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$Protocol = "docs/research/shared/qwen38_27b_candidate_protocol_2026-08-14.md"
$QueueRoot = Join-Path $Root "scratch\local_queue\qwen38_27b"
$StatusLog = Join-Path $QueueRoot "gan_dev750.status.log"
$Model = "ollama_chat/qwen3.8:27b"
$OllamaTag = "qwen3.8:27b"
$Name = "gan_dev750"
$Jsonl = "experiments/gan2026_qwen38_27b_candidate_dev750_20260814/validation750.rows.jsonl"
$Markdown = "experiments/gan2026_qwen38_27b_candidate_dev750_20260814/validation750.report.md"
$ExpectedRows = 750

New-Item -ItemType Directory -Force -Path $QueueRoot | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path -Parent (Join-Path $Root $Jsonl)) | Out-Null
Set-Location $Root

function Test-CompleteJsonl {
    param([string]$Path, [int]$ExpectedRows, [string]$CompanionPath)
    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    if ($CompanionPath -and -not (Test-Path -LiteralPath $CompanionPath)) { return $false }
    $count = (Get-Content -LiteralPath $Path | Measure-Object -Line).Lines
    return $count -eq $ExpectedRows
}

$installed = & ollama list 2>$null | Out-String
if ($installed -notmatch [regex]::Escape($OllamaTag)) {
    "BLOCKED $(Get-Date -Format o) missing $OllamaTag" | Add-Content $StatusLog
    throw "Ollama tag $OllamaTag is not installed. Upgrade Ollama if pull returns 412, then ollama pull $OllamaTag."
}

"QUEUE_START $(Get-Date -Format o) pid=$PID protocol=$Protocol cell=$Name" | Add-Content $StatusLog

if (Test-CompleteJsonl $Jsonl $ExpectedRows $Markdown) {
    "SKIP $(Get-Date -Format o) $Name complete" | Add-Content $StatusLog
    Write-Host "$Name already complete: $Jsonl"
    exit 0
}

$log = Join-Path $QueueRoot "$Name.log"
"START $(Get-Date -Format o) $Name" | Add-Content $StatusLog
& $Python @(
    "scripts/run_gan2026_v05_hosted_condition.py",
    "--prompt-version", "gan2026_hybrid_structured_events_v0.5",
    "--pipeline", "llm_with_rules",
    "--split", "validation",
    "--model", $Model,
    "--temperature", "0",
    "--max-tokens", "16000",
    "--disable-dspy-cache",
    "--progress-every", "1",
    "--resume-existing",
    "--escalation-reason", "Qwen 3.8 27B reserved-candidate live dev750 cell",
    "--jsonl", $Jsonl,
    "--markdown", $Markdown
) *>&1 | Tee-Object -FilePath $log -Append

$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    "FAILED $(Get-Date -Format o) $Name exit=$exitCode" | Add-Content $StatusLog
    throw "$Name failed with exit code $exitCode"
}

if (-not (Test-CompleteJsonl $Jsonl $ExpectedRows $Markdown)) {
    "FAILED $(Get-Date -Format o) $Name incomplete after exit 0" | Add-Content $StatusLog
    throw "$Name exited 0 but $Jsonl is not $ExpectedRows rows with companion $Markdown"
}

"DONE $(Get-Date -Format o) $Name" | Add-Content $StatusLog
"QUEUE_COMPLETE $(Get-Date -Format o) pid=$PID" | Add-Content $StatusLog
