param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("hosted_openai", "hosted_deepseek", "local")]
    [string]$ExecutionGroup
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RepoPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$ConfigPath = Join-Path $RepoRoot "configs\gan2026\six_model_validation_comparison_20260718.json"
$Config = Get-Content -Raw -LiteralPath $ConfigPath | ConvertFrom-Json
$Protocol = Join-Path $RepoRoot $Config.protocol
$ArtifactRoot = Join-Path $RepoRoot $Config.artifact_root
$ControllerRoot = Join-Path $RepoRoot "scratch\local_queue\gan2026_six_model_comparison_20260718"
$StatusLog = Join-Path $ControllerRoot "$ExecutionGroup.status.log"

New-Item -ItemType Directory -Force -Path $ArtifactRoot, $ControllerRoot | Out-Null
Set-Location $RepoRoot

function Wait-ForPriorLocalQueue {
    if ($ExecutionGroup -ne "local") { return }
    while ($true) {
        $active = @(
            Get-CimInstance Win32_Process | Where-Object {
                $_.CommandLine -and (
                    $_.CommandLine -match 'run_gan2026_v05_local_test_then_qwen_val_queue\.ps1' -or
                    $_.CommandLine -match 'run_gan2026_v05_hosted_condition\.py.*ollama_chat/'
                )
            }
        )
        if ($active.Count -eq 0) { return }
        "WAIT_PRIOR_LOCAL_QUEUE $(Get-Date -Format o) active=$($active.Count)" |
            Add-Content -LiteralPath $StatusLog
        Start-Sleep -Seconds 15
    }
}

function Assert-RowTraceGate {
    param(
        [string]$Name,
        [string]$Jsonl,
        [int]$ExpectedRows,
        [string]$ExpectedMethod
    )
    $rows = @(Get-Content -LiteralPath $Jsonl | ForEach-Object { $_ | ConvertFrom-Json })
    $uniqueRows = @($rows.source_row_index | Sort-Object -Unique)
    $traceRows = @(
        $rows | Where-Object {
            $_.row_trace.schema_version -eq $Config.row_trace_schema -and
            $_.row_trace.method -eq $ExpectedMethod
        }
    ).Count
    $successfulRows = @(
        $rows | Where-Object {
            $null -ne $_.row_trace.model_prediction.record -and
            $null -ne $_.comparison
        }
    ).Count
    $callFailures = @($rows | Where-Object { $_.call_error }).Count
    if (
        $rows.Count -ne $ExpectedRows -or
        $uniqueRows.Count -ne $ExpectedRows -or
        $traceRows -ne $ExpectedRows -or
        ($ExpectedRows -eq 5 -and $successfulRows -ne 5) -or
        ($ExpectedRows -eq 5 -and $callFailures -ne 0)
    ) {
        throw "$Name failed trace gate: rows=$($rows.Count) unique=$($uniqueRows.Count) traces=$traceRows successful=$successfulRows calls=$callFailures"
    }
    "TRACE_GATE_PASS $(Get-Date -Format o) $Name rows=$ExpectedRows" |
        Add-Content -LiteralPath $StatusLog
}

function Invoke-Condition {
    param(
        [object]$Condition,
        [object]$Method,
        [switch]$Pilot
    )
    $runKind = if ($Pilot) { "pilot5" } else { "validation750" }
    $runRoot = Join-Path $ArtifactRoot "$($Condition.slug)\$($Method.method)"
    $jsonl = Join-Path $runRoot "$runKind.rows.jsonl"
    $markdown = Join-Path $runRoot "$runKind.report.md"
    $log = Join-Path $ControllerRoot "$($Condition.slug).$($Method.method).$runKind.log"
    New-Item -ItemType Directory -Force -Path $runRoot | Out-Null

    $extraArgs = @()
    if ($Pilot) {
        $extraArgs += @("--limit", "5")
    } else {
        $extraArgs += @(
            "--escalation-reason",
            "User-requested fixed six-model llm_with_rules versus llm_only validation750 comparison with row traces"
        )
    }
    if (Test-Path -LiteralPath $jsonl) {
        $extraArgs += "--resume-existing"
    }

    $cliTemperature = if ($null -ne $Condition.cli_temperature) {
        [string]$Condition.cli_temperature
    } elseif ($null -ne $Condition.temperature) {
        [string]$Condition.temperature
    } else {
        "0"
    }

    "START $(Get-Date -Format o) $($Condition.slug) $($Method.method) $runKind" |
        Add-Content -LiteralPath $StatusLog
    & $RepoPython scripts/run_gan2026_hosted_condition.py `
        --prompt-version gan2026_hybrid_structured_events_v0.7 `
        --pipeline $Method.pipeline `
        --split validation `
        --model $Condition.model `
        --temperature $cliTemperature `
        --max-tokens $Condition.max_tokens `
        --disable-dspy-cache `
        --progress-every 5 `
        --jsonl $jsonl `
        --markdown $markdown `
        @extraArgs *>&1 | Tee-Object -FilePath $log
    if ($LASTEXITCODE -ne 0) {
        throw "$($Condition.slug) $($Method.method) $runKind failed with exit code $LASTEXITCODE"
    }

    $expectedRows = if ($Pilot) { 5 } else { [int]$Config.row_count }
    Assert-RowTraceGate `
        "$($Condition.slug) $($Method.method) $runKind" `
        $jsonl `
        $expectedRows `
        $Method.method
    "DONE $(Get-Date -Format o) $($Condition.slug) $($Method.method) $runKind" |
        Add-Content -LiteralPath $StatusLog
}

if (-not (Test-Path -LiteralPath $Protocol)) {
    throw "Protocol does not exist: $Protocol"
}

"CONTROLLER_START $(Get-Date -Format o) pid=$PID group=$ExecutionGroup" |
    Add-Content -LiteralPath $StatusLog
Wait-ForPriorLocalQueue

$conditions = @($Config.conditions | Where-Object { $_.execution_group -eq $ExecutionGroup })
foreach ($condition in $conditions) {
    foreach ($method in @($Config.methods)) {
        Invoke-Condition $condition $method -Pilot
        Invoke-Condition $condition $method
    }
}

"CONTROLLER_COMPLETE $(Get-Date -Format o) pid=$PID group=$ExecutionGroup" |
    Add-Content -LiteralPath $StatusLog
