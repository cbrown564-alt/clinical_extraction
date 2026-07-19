$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RepoPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$Protocol = "docs/experiments/gan2026/gan2026_matched_v05_local_test450_and_qwen_val750_protocol_2026-07-18.md"
$QueueRoot = Join-Path $RepoRoot "scratch\local_queue\gan_v05_20260718"
$StatusLog = Join-Path $QueueRoot "queue.status.log"

New-Item -ItemType Directory -Force -Path $QueueRoot | Out-Null
Set-Location $RepoRoot

function Invoke-GanRun {
    param(
        [string]$Name,
        [string]$Model,
        [string]$Split,
        [string]$Jsonl,
        [string]$Markdown,
        [string]$Log,
        [string[]]$ExtraArgs = @()
    )
    $resumeArgs = @()
    if (Test-Path -LiteralPath $Jsonl) { $resumeArgs = @("--resume-existing") }
    "START $(Get-Date -Format o) $Name" | Add-Content $StatusLog
    & $RepoPython scripts/run_gan2026_v05_hosted_condition.py `
        --prompt-version gan2026_hybrid_structured_events_v0.5 `
        --pipeline llm_with_rules `
        --split $Split `
        --model $Model `
        --temperature 0 `
        --max-tokens 16000 `
        --disable-dspy-cache `
        --progress-every 5 `
        --jsonl $Jsonl `
        --markdown $Markdown `
        @resumeArgs @ExtraArgs *>&1 | Tee-Object -FilePath $Log
    if ($LASTEXITCODE -ne 0) { throw "$Name failed with exit code $LASTEXITCODE" }
    "DONE $(Get-Date -Format o) $Name" | Add-Content $StatusLog
}

function Assert-PilotGate {
    param([string]$Name, [string]$Jsonl)
    $rows = @(Get-Content -LiteralPath $Jsonl | ForEach-Object { $_ | ConvertFrom-Json })
    $structured = @($rows | Where-Object { $null -ne $_.structured_record }).Count
    $callFailures = @($rows | Where-Object { $_.call_error }).Count
    $evidenceValid = @($rows | Where-Object { $_.evidence_valid -eq $true }).Count
    $blocking = @(
        $rows | Where-Object {
            $null -eq $_.structured_record -or
            @($_.parse_errors | Where-Object {
                $_ -match '^(schema_validation_error|unscorable_final_label|json_parse_error|not_run)'
            }).Count -gt 0
        }
    ).Count
    if ($rows.Count -ne 5 -or $structured -ne 5 -or $callFailures -ne 0 -or
        $evidenceValid -ne 5 -or $blocking -ne 0) {
        throw "$Name pilot failed: rows=$($rows.Count) structured=$structured calls=$callFailures evidence=$evidenceValid blocking=$blocking"
    }
    "PILOT_PASS $(Get-Date -Format o) $Name" | Add-Content $StatusLog
}

function Invoke-LocalCondition {
    param([string]$Slug, [string]$Model)
    $pilotRoot = "scratch/validation/gan2026_matched_v05_local/$Slug"
    $testRoot = "scratch/holdout/gan2026_matched_v05_local/$Slug"
    New-Item -ItemType Directory -Force -Path $pilotRoot, $testRoot | Out-Null
    Invoke-GanRun `
        "${Slug}_validation5_pilot" $Model "validation" `
        "$pilotRoot/rows.jsonl" "$pilotRoot/report.md" `
        (Join-Path $QueueRoot "${Slug}_pilot.log") `
        @("--limit", "5")
    Assert-PilotGate $Slug "$pilotRoot/rows.jsonl"
    Invoke-GanRun `
        "${Slug}_test450" $Model "test" `
        "$testRoot/rows.jsonl" "$testRoot/report.md" `
        (Join-Path $QueueRoot "${Slug}_test450.log") `
        @("--frozen-test-protocol", $Protocol)
}

"QUEUE_START $(Get-Date -Format o) pid=$PID protocol=$Protocol" | Add-Content $StatusLog

Invoke-LocalCondition "qwen36_35b" "ollama_chat/qwen3.6:35b"
Invoke-LocalCondition "gemma4_26b" "ollama_chat/gemma4:26b"

$QwenValidationRoot = "scratch/local_queue/qwen36_35b/gan"
New-Item -ItemType Directory -Force -Path $QwenValidationRoot | Out-Null
Invoke-GanRun `
    "qwen36_35b_validation750_v05" "ollama_chat/qwen3.6:35b" "validation" `
    "$QwenValidationRoot/v05_validation750_full.jsonl" `
    "$QwenValidationRoot/v05_validation750_full.md" `
    (Join-Path $QueueRoot "qwen36_35b_validation750_v05.log") `
    @("--escalation-reason", "Full validation750 requested after the complete v0.5 local test450 conditions")

"QUEUE_COMPLETE $(Get-Date -Format o) pid=$PID" | Add-Content $StatusLog
