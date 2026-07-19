$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RepoPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$Protocol = "docs/experiments/gan2026/gan2026_matched_v05_local_test450_and_qwen_val750_protocol_2026-07-18.md"
$OutputRoot = "scratch/holdout/gan2026_matched_v05/deepseek_v4_flash"
$StatusLog = Join-Path $RepoRoot "$OutputRoot/resume_20260718.status.log"

Set-Location $RepoRoot
"START $(Get-Date -Format o) deepseek_v4_flash_remaining_100" | Add-Content $StatusLog

& $RepoPython scripts/run_gan2026_v05_hosted_condition.py `
    --prompt-version gan2026_hybrid_structured_events_v0.5 `
    --pipeline llm_with_rules `
    --split test `
    --frozen-test-protocol $Protocol `
    --model deepseek/deepseek-v4-flash `
    --temperature 0 `
    --max-tokens 32000 `
    --disable-dspy-cache `
    --progress-every 5 `
    --resume-existing `
    --jsonl "$OutputRoot/rows.jsonl" `
    --markdown "$OutputRoot/report.md"

if ($LASTEXITCODE -ne 0) { throw "DeepSeek continuation failed with exit code $LASTEXITCODE" }
"CALLS_COMPLETE $(Get-Date -Format o)" | Add-Content $StatusLog

& $RepoPython scripts/replay_gan2026_v05_current_schema.py `
    --condition deepseek_v4_flash

if ($LASTEXITCODE -ne 0) { throw "DeepSeek current-schema replay failed with exit code $LASTEXITCODE" }
"REPLAY_COMPLETE $(Get-Date -Format o)" | Add-Content $StatusLog
