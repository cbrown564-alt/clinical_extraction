$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$QueueRoot = Join-Path $Root "scratch\local_queue"
$Protocol = "docs/experiments/gan2026/gan2026_local_val750_qwen_gemma_protocol_2026-07-18.md"
$StatusLog = Join-Path $QueueRoot "gan_val750_queue_20260718.status.log"
$QwenLog = Join-Path $QueueRoot "gan_val750_qwen36_35b.log"
$GemmaLog = Join-Path $QueueRoot "gan_val750_gemma4_26b.log"

New-Item -ItemType Directory -Force -Path $QueueRoot | Out-Null
Set-Location $Root

function Get-ActiveLocalRunner {
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.CommandLine -and
            $_.CommandLine -match 'run_(exectv2_six_model_comparison|gan2026_hosted_condition)\.py'
        }
}

function Wait-ForExistingLocalRunners {
    while ($true) {
        $active = @(Get-ActiveLocalRunner)
        if ($active.Count -eq 0) { return }
        "WAIT $(Get-Date -Format o) active=$($active.Count)" | Add-Content $StatusLog
        Start-Sleep -Seconds 15
    }
}

function Invoke-ValidationRun {
    param(
        [string]$Name,
        [string]$Model,
        [string]$Jsonl,
        [string]$Markdown,
        [string]$Log
    )
    "START $(Get-Date -Format o) $Name" | Add-Content $StatusLog
    & $Python scripts/run_gan2026_hosted_condition.py `
        --prompt-version gan2026_hybrid_structured_events_v0.7 `
        --pipeline llm_with_rules `
        --split validation `
        --escalation-reason "Full validation750 requested after completed matched test450; no validation gate" `
        --model $Model `
        --temperature 0 `
        --max-tokens 16000 `
        --disable-dspy-cache `
        --progress-every 1 `
        --jsonl $Jsonl `
        --markdown $Markdown *>&1 | Tee-Object -FilePath $Log
    if ($LASTEXITCODE -ne 0) { throw "$Name failed with exit code $LASTEXITCODE" }
    "DONE $(Get-Date -Format o) $Name" | Add-Content $StatusLog
}

"QUEUE_START $(Get-Date -Format o) pid=$PID protocol=$Protocol" | Add-Content $StatusLog
Wait-ForExistingLocalRunners

Invoke-ValidationRun `
    "qwen36_35b_gan_validation750" `
    "ollama_chat/qwen3.6:35b" `
    "scratch/local_queue/qwen36_35b/gan/validation750_full.jsonl" `
    "scratch/local_queue/qwen36_35b/gan/validation750_full.md" `
    $QwenLog

Invoke-ValidationRun `
    "gemma4_26b_gan_validation750" `
    "ollama_chat/gemma4:26b" `
    "scratch/local_queue/gemma4_26b/gan/validation750_full.jsonl" `
    "scratch/local_queue/gemma4_26b/gan/validation750_full.md" `
    $GemmaLog

"QUEUE_COMPLETE $(Get-Date -Format o) pid=$PID" | Add-Content $StatusLog
