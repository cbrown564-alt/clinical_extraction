$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$QueueRoot = Join-Path $Root "scratch\local_queue"
$Protocol = "docs/experiments/local_six_model_queue_protocol_2026-07-15.md"

function Invoke-QueueStep {
    param([string]$Name, [string[]]$Arguments)
    $log = Join-Path $QueueRoot "$Name.log"
    "START $(Get-Date -Format o) $Name" | Add-Content (Join-Path $QueueRoot "queue.status.log")
    & $Python @Arguments *>&1 | Tee-Object -FilePath $log
    if ($LASTEXITCODE -ne 0) { throw "$Name failed with exit code $LASTEXITCODE" }
    "DONE $(Get-Date -Format o) $Name" | Add-Content (Join-Path $QueueRoot "queue.status.log")
}

function Invoke-LocalProbe {
    param([string]$Slug, [string]$Model)
    Invoke-QueueStep "${Slug}_structured_probe" @(
        "scripts/probe_ollama_structured_output.py", "--model", $Model
    )
}

Set-Location $Root
$GemmaExect = "configs/exectv2/six_model_comparison/gemma4_26b_dev140.json"
Invoke-LocalProbe "qwen36_35b" "qwen3.6:35b"
Invoke-QueueStep "qwen_exect_test60" @("scripts/run_hosted_holdout_panel.py", "--config", "configs/holdout/local_exect_qwen_test60_20260715.json", "--panel", "exectv2")
Invoke-LocalProbe "gemma4_26b" "gemma4:26b"
Invoke-QueueStep "gemma_exect_dev5" @("scripts/smoke_exectv2_six_model_condition.py", "--config", $GemmaExect, "--rows", "5")
Invoke-QueueStep "gemma_exect_dev140" @("scripts/run_exectv2_six_model_comparison.py", "--config", $GemmaExect, "--no-dspy-cache")
Invoke-QueueStep "gemma_exect_test60" @("scripts/run_hosted_holdout_panel.py", "--config", "configs/holdout/local_exect_gemma_test60_20260715.json", "--panel", "exectv2")

function Invoke-Gan {
    param([string]$Slug, [string]$Model)
    $base = "scratch/local_queue/$Slug/gan"
    Invoke-QueueStep "${Slug}_gan_dev5" @("scripts/run_gan2026_hosted_condition.py", "--prompt-version", "gan2026_hybrid_structured_events_v0.7", "--pipeline", "llm_with_rules", "--split", "validation", "--limit", "5", "--model", $Model, "--temperature", "0", "--max-tokens", "16000", "--disable-dspy-cache", "--jsonl", "$base/dev5.jsonl", "--markdown", "$base/dev5.md")
    Invoke-QueueStep "${Slug}_gan_test450" @("scripts/run_gan2026_hosted_condition.py", "--prompt-version", "gan2026_hybrid_structured_events_v0.7", "--pipeline", "llm_with_rules", "--split", "test", "--frozen-test-protocol", $Protocol, "--model", $Model, "--temperature", "0", "--max-tokens", "16000", "--disable-dspy-cache", "--jsonl", "$base/test450_sealed_rows.jsonl", "--markdown", "$base/test450_aggregate.md")
}

Invoke-Gan "qwen36_35b" "ollama_chat/qwen3.6:35b"
Invoke-Gan "gemma4_26b" "ollama_chat/gemma4:26b"
"COMPLETE $(Get-Date -Format o)" | Add-Content (Join-Path $QueueRoot "queue.status.log")
