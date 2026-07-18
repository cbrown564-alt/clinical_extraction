$ErrorActionPreference = "Continue"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$QueueRoot = Join-Path $Root "scratch\local_queue\remaining_full"
$StatusLog = Join-Path $QueueRoot "queue.status.log"
$GanProtocol = "docs/experiments/local_six_model_queue_protocol_2026-07-15.md"
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
    } else {
        "FAILED $(Get-Date -Format o) $Name exit=$exitCode" | Add-Content $StatusLog
    }
}

function Invoke-ExectDev140 {
    param([string]$Slug, [string]$Config, [string]$FinalJsonl)
    if (Test-CompleteJsonl $FinalJsonl 140 ($FinalJsonl -replace '\.jsonl$', '.json')) {
        "SKIP $(Get-Date -Format o) ${Slug}_exect_dev140 complete" | Add-Content $StatusLog
        return
    }
    Invoke-QueueStep "${Slug}_exect_dev140" @(
        "scripts/run_exectv2_six_model_comparison.py",
        "--config", $Config,
        "--no-dspy-cache",
        "--progress-every", "1",
        "--allow-row-failures"
    )
}

function Invoke-ExectTest60 {
    param([string]$Slug, [string]$Config, [string]$SealedRows, [string]$Aggregate)
    if (Test-CompleteJsonl $SealedRows 59 $Aggregate) {
        "SKIP $(Get-Date -Format o) ${Slug}_exect_test60 complete" | Add-Content $StatusLog
        return
    }
    Invoke-QueueStep "${Slug}_exect_test60" @(
        "scripts/run_hosted_holdout_panel.py",
        "--config", $Config,
        "--panel", "exectv2"
    )
}

function Invoke-GanTest450 {
    param([string]$Slug, [string]$Model)
    $base = "scratch/local_queue/$Slug/gan"
    $sealed = "$base/test450_sealed_rows.jsonl"
    $aggregate = "$base/test450_aggregate.md"
    if (Test-CompleteJsonl $sealed 450 $aggregate) {
        "SKIP $(Get-Date -Format o) ${Slug}_gan_test450 complete" | Add-Content $StatusLog
        return
    }
    Invoke-QueueStep "${Slug}_gan_test450" @(
        "scripts/run_gan2026_hosted_condition.py",
        "--prompt-version", "gan2026_hybrid_structured_events_v0.7",
        "--pipeline", "llm_with_rules",
        "--split", "test",
        "--frozen-test-protocol", $GanProtocol,
        "--model", $Model,
        "--temperature", "0",
        "--max-tokens", "16000",
        "--disable-dspy-cache",
        "--progress-every", "1",
        "--resume-existing",
        "--jsonl", $sealed,
        "--markdown", $aggregate
    )
}

"QUEUE_START $(Get-Date -Format o) pid=$PID" | Add-Content $StatusLog

Invoke-ExectDev140 `
    "qwen36_35b" `
    "configs/exectv2/six_model_comparison/qwen36_35b_dev140.json" `
    "experiments/exectv2_six_model_single_call_qwen36_35b_dev140_20260715.jsonl"
Invoke-ExectTest60 `
    "qwen36_35b" `
    "configs/holdout/local_exect_qwen_test60_20260715.json" `
    "scratch/local_queue/qwen36_35b_exect/test60/qwen36_35b/qwen36_35b_sealed_rows.jsonl" `
    "scratch/local_queue/qwen36_35b_exect/test60/qwen36_35b/qwen36_35b_aggregate.md"

Invoke-ExectDev140 `
    "gemma4_26b" `
    "configs/exectv2/six_model_comparison/gemma4_26b_dev140.json" `
    "experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715.jsonl"
Invoke-ExectTest60 `
    "gemma4_26b" `
    "configs/holdout/local_exect_gemma_test60_20260715.json" `
    "scratch/local_queue/gemma4_26b_exect/test60/gemma4_26b/gemma4_26b_sealed_rows.jsonl" `
    "scratch/local_queue/gemma4_26b_exect/test60/gemma4_26b/gemma4_26b_aggregate.md"

Invoke-GanTest450 "qwen36_35b" "ollama_chat/qwen3.6:35b"
Invoke-GanTest450 "gemma4_26b" "ollama_chat/gemma4:26b"

"QUEUE_COMPLETE $(Get-Date -Format o) pid=$PID" | Add-Content $StatusLog
