$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RepoPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$Protocol = "docs/experiments/gan2026/gan2026_six_model_llm_only_test450_protocol_2026-08-01.md"
$PromptVersion = "gan2026_llm_only_canonical_pipeline_v0.8"
$PanelRoot = Join-Path $RepoRoot "scratch\holdout\gan2026_six_model_llm_only_test450_20260801"
$LogRoot = Join-Path $RepoRoot "scratch\validation\gan2026_six_model_llm_only_test450_20260801"
$QueueName = $args[0]
if (-not $QueueName) {
    throw "Usage: run_gan2026_six_model_llm_only_test450_queues.ps1 <hosted_openai|local>"
}

New-Item -ItemType Directory -Force -Path $PanelRoot, $LogRoot | Out-Null
Set-Location $RepoRoot

if (Test-Path (Join-Path $RepoRoot ".env")) {
    Get-Content (Join-Path $RepoRoot ".env") | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            Set-Item -Path ("Env:" + $matches[1].Trim()) -Value $matches[2].Trim()
        }
    }
}

function Invoke-LlmOnlyCondition {
    param(
        [string]$Slug,
        [string]$Model,
        [double]$Temperature,
        [int]$MaxTokens
    )
    $outRoot = Join-Path $PanelRoot $Slug
    New-Item -ItemType Directory -Force -Path $outRoot | Out-Null
    $jsonl = Join-Path $outRoot "rows.jsonl"
    $markdown = Join-Path $outRoot "aggregate.md"
    $log = Join-Path $LogRoot "$Slug.log"
    $resumeArgs = @()
    if (Test-Path -LiteralPath $jsonl) { $resumeArgs = @("--resume-existing") }
    "START $(Get-Date -Format o) $Slug model=$Model" | Add-Content -LiteralPath $StatusLog
    # Progress JSON is emitted on stderr; do not let PowerShell treat it as terminating.
    $previousErrorAction = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & $RepoPython -u scripts/run_gan2026_llm_only_condition.py `
        --prompt-version $PromptVersion `
        --pipeline llm `
        --split test `
        --frozen-test-protocol $Protocol `
        --model $Model `
        --temperature $Temperature `
        --max-tokens $MaxTokens `
        --disable-dspy-cache `
        --progress-every 5 `
        --jsonl $jsonl `
        --markdown $markdown `
        @resumeArgs *>&1 | Tee-Object -FilePath $log
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorAction
    if ($exitCode -ne 0) {
        "FAIL $(Get-Date -Format o) $Slug exit=$exitCode" | Add-Content -LiteralPath $StatusLog
        throw "$Slug failed with exit code $exitCode"
    }
    "DONE $(Get-Date -Format o) $Slug" | Add-Content -LiteralPath $StatusLog
}

$StatusLog = Join-Path $LogRoot "$QueueName.status.log"
"QUEUE_START $(Get-Date -Format o) queue=$QueueName pid=$PID" | Add-Content -LiteralPath $StatusLog

if ($QueueName -eq "hosted_openai") {
    Invoke-LlmOnlyCondition "gpt41mini" "openai/gpt-4.1-mini" 0 10000
    Invoke-LlmOnlyCondition "gpt56luna" "openai/gpt-5.6-luna" 1 10000
    Invoke-LlmOnlyCondition "gpt56sol" "openai/gpt-5.6-sol" 0 10000
}
elseif ($QueueName -eq "local") {
    Invoke-LlmOnlyCondition "qwen36_35b" "ollama_chat/qwen3.6:35b" 0 16000
    Invoke-LlmOnlyCondition "gemma4_26b" "ollama_chat/gemma4:26b" 0 16000
}
else {
    throw "Unknown queue: $QueueName"
}

"QUEUE_COMPLETE $(Get-Date -Format o) queue=$QueueName pid=$PID" | Add-Content -LiteralPath $StatusLog
