# Self-contained overnight driver for the Qwen cross-model GEPA runs.
# Registered as a Windows Scheduled Task so it runs under Task Scheduler,
# independent of the Claude Code session (which reaped the first launch).
# Ensures its own ollama backend, then runs the resumable orchestrator to
# completion. GEPA resumes from gepa_state.bin checkpoints, so a restart
# continues rather than starting over.

$ErrorActionPreference = 'Continue'

$root      = 'C:\Users\cbrow\code\clinical_extraction'
$logdir    = Join-Path $root 'experiments\gepa_overnight_exectv2'
$ollamaExe = 'C:\Users\cbrow\AppData\Local\Programs\Ollama\ollama.exe'
$py        = Join-Path $root '.venv\Scripts\python.exe'
$runLog    = Join-Path $logdir 'qwen_cross_model_run.log'
$ollamaLog = Join-Path $logdir 'ollama_serve_overnight.log'
$wrapLog   = Join-Path $logdir 'qwen_overnight_wrapper.log'

function Test-Ollama {
    try { Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -TimeoutSec 3 -ErrorAction Stop | Out-Null; return $true }
    catch { return $false }
}

"[$(Get-Date -Format o)] wrapper start" | Out-File -FilePath $wrapLog -Append -Encoding utf8

# 1. Ensure ollama is serving (detached, hidden).
if (-not (Test-Ollama)) {
    Start-Process -FilePath $ollamaExe -ArgumentList 'serve' -WindowStyle Hidden `
        -RedirectStandardOutput $ollamaLog -RedirectStandardError ($ollamaLog + '.err')
    "[$(Get-Date -Format o)] started ollama serve" | Out-File -FilePath $wrapLog -Append -Encoding utf8
}

# 2. Wait up to ~90s for the API to answer.
$up = $false
for ($i = 0; $i -lt 45; $i++) {
    if (Test-Ollama) { $up = $true; break }
    Start-Sleep -Seconds 2
}
if (-not $up) {
    "[$(Get-Date -Format o)] ERROR: ollama did not come up; aborting" | Out-File -FilePath $wrapLog -Append -Encoding utf8
    exit 1
}
"[$(Get-Date -Format o)] ollama up; launching orchestrator" | Out-File -FilePath $wrapLog -Append -Encoding utf8

# 3. Run the orchestrator to completion (resumes from GEPA checkpoints).
"`n===== relaunch via scheduled task $(Get-Date -Format o) =====" | Out-File -FilePath $runLog -Append -Encoding utf8
Set-Location $root
& $py 'experiments\gepa_qwen_cross_model_exectv2.py' *>> $runLog

"[$(Get-Date -Format o)] wrapper done (orchestrator exit $LASTEXITCODE)" | Out-File -FilePath $wrapLog -Append -Encoding utf8
