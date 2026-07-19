$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RepoPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$ControllerRoot = Join-Path $RepoRoot "scratch\local_queue\gan2026_six_model_comparison_20260718"
$StatusLog = Join-Path $ControllerRoot "finalizer.status.log"
$PartialJson = Join-Path $ControllerRoot "final_summary_check.json"
$PartialMarkdown = Join-Path $ControllerRoot "final_summary_check.md"

Set-Location $RepoRoot

"FINALIZER_START $(Get-Date -Format o) pid=$PID" | Add-Content -LiteralPath $StatusLog
while ($true) {
    $controllers = @(
        Get-CimInstance Win32_Process | Where-Object {
            $_.CommandLine -and
            $_.CommandLine -match 'run_gan2026_six_model_validation_comparison\.ps1'
        }
    )
    if ($controllers.Count -eq 0) { break }
    "WAIT_CONTROLLERS $(Get-Date -Format o) active=$($controllers.Count)" |
        Add-Content -LiteralPath $StatusLog
    Start-Sleep -Seconds 30
}

& $RepoPython scripts/summarize_gan2026_six_model_validation_comparison.py `
    --json $PartialJson `
    --markdown $PartialMarkdown *>&1 |
    Tee-Object -FilePath (Join-Path $ControllerRoot "finalizer.preflight.log")
if ($LASTEXITCODE -ne 0) {
    "FINALIZER_INCOMPLETE $(Get-Date -Format o) exit=$LASTEXITCODE" |
        Add-Content -LiteralPath $StatusLog
    exit $LASTEXITCODE
}

& $RepoPython scripts/summarize_gan2026_six_model_validation_comparison.py *>&1 |
    Tee-Object -FilePath (Join-Path $ControllerRoot "finalizer.publish.log")
if ($LASTEXITCODE -ne 0) {
    throw "Final summary publication failed with exit code $LASTEXITCODE"
}

"FINALIZER_COMPLETE $(Get-Date -Format o)" | Add-Content -LiteralPath $StatusLog
