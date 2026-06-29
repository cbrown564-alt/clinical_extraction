<#
.SYNOPSIS
  Run the four SF-verify Phase 5 overnight runs sequentially.

  Matrix (extraction = deepseek-reasoner for all four):
    1. reasoner extraction + reasoner verify, feedback-only
    2. reasoner extraction + gpt-4.1-mini verify, feedback-only
    3. reasoner extraction + reasoner verify, + hand-curated examples
    4. reasoner extraction + gpt-4.1-mini verify, + hand-curated examples

  Feedback-only runs go first (the attributable primary lever); the +examples runs
  cross the H-examples factor on top, so the example lift is measured against them.

  Plan: docs/plans/exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md (Phase 5).

.EXAMPLE
  # smoke-check the wiring on all four (tiny, still hits the APIs):
  pwsh experiments/run_sf_verify_phase5_matrix.ps1 -Smoke

  # the real overnight run:
  pwsh experiments/run_sf_verify_phase5_matrix.ps1
#>
param(
    [switch]$Smoke
)

$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $PSScriptRoot
$logDir = Join-Path $PSScriptRoot "gepa_overnight_exectv2"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$reasoner = "deepseek/deepseek-reasoner"
$mini = "openai/gpt-4.1-mini"

# Ordered: feedback-only first, then +examples.
$runs = @(
    @{ name = "reasoner_reasoner_fb"; extract = $reasoner; verify = $reasoner; examples = $false },
    @{ name = "reasoner_mini_fb";     extract = $reasoner; verify = $mini;     examples = $false },
    @{ name = "reasoner_reasoner_ex"; extract = $reasoner; verify = $reasoner; examples = $true  },
    @{ name = "reasoner_mini_ex";     extract = $reasoner; verify = $mini;     examples = $true  }
)

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
Write-Host "[matrix] starting $($runs.Count) runs (smoke=$Smoke) at $stamp" -ForegroundColor Cyan

foreach ($run in $runs) {
    $argv = @(
        "run", "python", "experiments/gepa_sf_verify_phase5_exectv2.py",
        "--extraction-model", $run.extract,
        "--verify-model", $run.verify
    )
    if ($run.examples) { $argv += "--with-examples" }
    if ($Smoke) { $argv += "--smoke" }

    $log = Join-Path $logDir ("matrix_{0}_{1}.log" -f $run.name, $stamp)
    Write-Host "`n[matrix] === $($run.name) ===  -> $log" -ForegroundColor Yellow
    Write-Host "[matrix] uv $($argv -join ' ')"

    $started = Get-Date
    & uv @argv 2>&1 | Tee-Object -FilePath $log
    $code = $LASTEXITCODE
    $mins = [math]::Round(((Get-Date) - $started).TotalMinutes, 1)
    if ($code -eq 0) {
        Write-Host "[matrix] $($run.name) OK in $mins min" -ForegroundColor Green
    } else {
        Write-Host "[matrix] $($run.name) FAILED (exit $code) after $mins min — continuing" -ForegroundColor Red
    }
}

Write-Host "`n[matrix] done. Summaries:" -ForegroundColor Cyan
Get-ChildItem -Path $PSScriptRoot -Filter "exectv2_gepa_sf_verify_p5_*.json" |
    Sort-Object LastWriteTime |
    ForEach-Object { Write-Host "  $($_.Name)" }
