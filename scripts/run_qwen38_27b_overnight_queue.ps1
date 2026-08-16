$ErrorActionPreference = "Continue"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$Protocol = "docs/research/shared/qwen38_27b_candidate_protocol_2026-08-14.md"
$QueueRoot = Join-Path $Root "scratch\local_queue\qwen38_27b"
$StatusLog = Join-Path $QueueRoot "queue.status.log"
$Model = "ollama_chat/qwen3.8:27b"
$OllamaTag = "qwen3.8:27b"

New-Item -ItemType Directory -Force -Path $QueueRoot | Out-Null
Set-Location $Root

function Test-CompleteJsonl {
    param([string]$Path, [int]$ExpectedRows, [string]$CompanionPath)
    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    if ($CompanionPath -and -not (Test-Path -LiteralPath $CompanionPath)) { return $false }
    $count = (Get-Content -LiteralPath $Path | Measure-Object -Line).Lines
    return $count -eq $ExpectedRows
}

function Invoke-QueueStep {
    param([string]$Name, [string[]]$Arguments)
    $log = Join-Path $QueueRoot "$Name.log"
    "START $(Get-Date -Format o) $Name" | Add-Content $StatusLog
    & $Python @Arguments *>&1 | Tee-Object -FilePath $log -Append
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 0) {
        "DONE $(Get-Date -Format o) $Name" | Add-Content $StatusLog
        return $true
    }
    "FAILED $(Get-Date -Format o) $Name exit=$exitCode" | Add-Content $StatusLog
    return $false
}

$installed = & ollama list 2>$null | Out-String
if ($installed -notmatch [regex]::Escape($OllamaTag)) {
    "BLOCKED $(Get-Date -Format o) missing $OllamaTag" | Add-Content $StatusLog
    throw "Ollama tag $OllamaTag is not installed. Upgrade Ollama if pull returns 412, then ollama pull $OllamaTag."
}

$smoke = Join-Path $QueueRoot "exect\smoke_dev1.jsonl"
if (-not (Test-Path -LiteralPath $smoke)) {
    "BLOCKED $(Get-Date -Format o) missing smoke $smoke" | Add-Content $StatusLog
    throw "One-letter smoke artifact is missing. Run scripts/smoke_exectv2_six_model_condition.py first."
}

"QUEUE_START $(Get-Date -Format o) pid=$PID protocol=$Protocol" | Add-Content $StatusLog

$exectTestSealed = "scratch/holdout/qwen38_27b_20260814/exect_test60/qwen38_27b_sealed_rows.jsonl"
$exectTestAgg = "scratch/holdout/qwen38_27b_20260814/exect_test60/qwen38_27b_aggregate.json"
if (Test-CompleteJsonl $exectTestSealed 59 $exectTestAgg) {
    "SKIP $(Get-Date -Format o) exect_test60 complete" | Add-Content $StatusLog
} else {
    $ok = Invoke-QueueStep "exect_test60" @(
        "scripts/run_exectv2_six_model_comparison.py",
        "--config", "configs/exectv2/six_model_comparison/qwen38_27b_test60.json",
        "--allow-non-dev140",
        "--no-dspy-cache",
        "--generated-on", "2026-08-14",
        "--allow-row-failures",
        "--progress-every", "1"
    )
    if (-not $ok) { throw "exect_test60 failed" }
}

$ganTestSealed = "scratch/holdout/qwen38_27b_20260814/gan_test450/sealed_rows.jsonl"
$ganTestAgg = "scratch/holdout/qwen38_27b_20260814/gan_test450/aggregate.md"
New-Item -ItemType Directory -Force -Path (Split-Path -Parent (Join-Path $Root $ganTestSealed)) | Out-Null
if (Test-CompleteJsonl $ganTestSealed 450 $ganTestAgg) {
    "SKIP $(Get-Date -Format o) gan_test450 complete" | Add-Content $StatusLog
} else {
    $ok = Invoke-QueueStep "gan_test450" @(
        "scripts/run_gan2026_v05_hosted_condition.py",
        "--prompt-version", "gan2026_hybrid_structured_events_v0.5",
        "--pipeline", "llm_with_rules",
        "--split", "test",
        "--frozen-test-protocol", $Protocol,
        "--model", $Model,
        "--temperature", "0",
        "--max-tokens", "16000",
        "--disable-dspy-cache",
        "--progress-every", "1",
        "--resume-existing",
        "--jsonl", $ganTestSealed,
        "--markdown", $ganTestAgg
    )
    if (-not $ok) { throw "gan_test450 failed" }
}

$exectDev = "experiments/exectv2_six_model_single_call_qwen38_27b_dev140_20260814.jsonl"
$exectDevJson = "experiments/exectv2_six_model_single_call_qwen38_27b_dev140_20260814.json"
if (Test-CompleteJsonl $exectDev 140 $exectDevJson) {
    "SKIP $(Get-Date -Format o) exect_dev140 complete" | Add-Content $StatusLog
} else {
    $ok = Invoke-QueueStep "exect_dev140" @(
        "scripts/run_exectv2_six_model_comparison.py",
        "--config", "configs/exectv2/six_model_comparison/qwen38_27b_dev140.json",
        "--no-dspy-cache",
        "--generated-on", "2026-08-14",
        "--allow-row-failures",
        "--progress-every", "1"
    )
    if (-not $ok) { throw "exect_dev140 failed" }
}

$ganDev = "experiments/gan2026_qwen38_27b_candidate_dev750_20260814/validation750.rows.jsonl"
$ganDevMd = "experiments/gan2026_qwen38_27b_candidate_dev750_20260814/validation750.report.md"
New-Item -ItemType Directory -Force -Path (Split-Path -Parent (Join-Path $Root $ganDev)) | Out-Null
if (Test-CompleteJsonl $ganDev 750 $ganDevMd) {
    "SKIP $(Get-Date -Format o) gan_dev750 complete" | Add-Content $StatusLog
} else {
    $ok = Invoke-QueueStep "gan_dev750" @(
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
        "--jsonl", $ganDev,
        "--markdown", $ganDevMd
    )
    if (-not $ok) { throw "gan_dev750 failed" }
}

"QUEUE_COMPLETE $(Get-Date -Format o) pid=$PID" | Add-Content $StatusLog
