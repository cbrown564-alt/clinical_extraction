param(
  [int[]]$Limits = @(1, 25, 50, 250),
  [string[]]$QwenModels = @("ollama_chat/qwen3.6:35b"),
  [string]$GptModel = "openai/gpt-4.1-mini",
  [string]$QwenApiBase = "http://localhost:11434",
  [string]$DateStamp = "2026-06-03",
  [int]$MaxTokens = 1800,
  [double]$Temperature = 0.0,
  [string]$PythonExe = "",
  [switch]$IncludeValidation750,
  [switch]$PromptOnly,
  [switch]$EnableDspyCacheForGpt
)

$ErrorActionPreference = "Stop"

if (-not $env:PYTHONPATH) {
  $env:PYTHONPATH = "src"
}
if (-not $PythonExe) {
  $venvPython = Join-Path -Path (Get-Location) -ChildPath ".venv/Scripts/python.exe"
  $PythonExe = if (Test-Path -Path $venvPython) { $venvPython } else { "python" }
}

function ConvertTo-RunSlug {
  param([string]$Model)
  return $Model.Replace("openai/", "").Replace("ollama_chat/", "").Replace(":", "_").Replace(".", "")
}

function Invoke-PairedRun {
  param(
    [string]$Model,
    [string]$ApiBase,
    [int]$Limit,
    [bool]$DisableCache
  )

  $modelSlug = ConvertTo-RunSlug -Model $Model
  $mode = if ($PromptOnly) { "prompt-only" } else { "live" }
  $modeSlug = $mode.Replace("-", "_")
  $prefix = "experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation${Limit}_${modelSlug}_paired_gate_v0_${modeSlug}_${DateStamp}"
  $sourceJsonl = "${prefix}.jsonl"
  $sourceMd = "${prefix}.md"
  $replayPrefix = "experiments/gan2026_selective_safety_floor_gate_v0_validation${Limit}_${modelSlug}_paired_replay_${modeSlug}_${DateStamp}"
  $replayJsonl = "${replayPrefix}.jsonl"
  $replayJson = "${replayPrefix}.json"
  $replayMd = "${replayPrefix}.md"

  $pipelineArgs = @(
    "--pipeline", "hybrid_parallel_state_candidate_reasoner",
    "--split", "validation",
    "--limit", "$Limit",
    "--model", $Model,
    "--temperature", "$Temperature",
    "--max-tokens", "$MaxTokens",
    "--mode", $mode,
    "--progress-every", "10",
    "--jsonl", $sourceJsonl,
    "--markdown", $sourceMd
  )
  if ($ApiBase) {
    $pipelineArgs += @("--api-base", $ApiBase)
  }
  if ($DisableCache) {
    $pipelineArgs += "--disable-dspy-cache"
  }
  if ($Limit -gt 250) {
    $pipelineArgs += @(
      "--escalation-reason",
      "predeclared paired selective safety-floor gate validation-cycle model comparison"
    )
  }

  Write-Host ""
  Write-Host "== Upstream artifact: $Model validation$Limit =="
  & $PythonExe -m clinical_extraction.tasks.seizure_frequency.gan2026.cli.llm_pipeline_cli @pipelineArgs

  Write-Host ""
  Write-Host "== Selective gate no-call replay: $Model validation$Limit =="
  & $PythonExe -m clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.selective_safety_floor_gate_replay `
    --manifest experiments/gan2026_selective_safety_floor_gate_v0_validation_cycle_manifest_2026-06-03.json `
    --source-artifact $sourceJsonl `
    --jsonl $replayJsonl `
    --json $replayJson `
    --markdown $replayMd `
    --full-artifact-slice-name "validation${Limit}"

  $summary = Get-Content -Path $replayJson -Raw | ConvertFrom-Json
  $slice = $summary.slice_summary."validation${Limit}"
  if ($slice -and $slice.variant_summary) {
    $selective = $slice.variant_summary.selective_safety_floor_gate_v0
    [PSCustomObject]@{
      model = $Model
      limit = $Limit
      rows = $selective.rows
      purist_correct = $selective.purist_correct
      pragmatic_correct = $selective.pragmatic_correct
      changed_rows = $selective.changed_rows
      wrong_to_correct = $selective.wrong_to_correct
      correct_to_wrong = $selective.correct_to_wrong
      deterministic_regressions = $selective.deterministic_correct_regressions
      precision = $selective.changed_label_precision
      source_jsonl = $sourceJsonl
      replay_json = $replayJson
      replay_markdown = $replayMd
    }
  }
}

$allLimits = @($Limits)
if ($IncludeValidation750 -and -not ($allLimits -contains 750)) {
  $allLimits += 750
}
$allLimits = $allLimits | Sort-Object -Unique

$results = @()
foreach ($limit in $allLimits) {
  $results += Invoke-PairedRun -Model $GptModel -ApiBase "" -Limit $limit -DisableCache:(!$EnableDspyCacheForGpt)
  foreach ($qwenModel in $QwenModels) {
    $results += Invoke-PairedRun -Model $qwenModel -ApiBase $QwenApiBase -Limit $limit -DisableCache:$true
  }
}

$results | Format-Table -AutoSize
$runModeSlug = if ($PromptOnly) { "prompt_only" } else { "live" }
$resultsPath = "experiments/gan2026_selective_safety_floor_gate_v0_paired_model_results_${runModeSlug}_${DateStamp}.json"
$results | ConvertTo-Json -Depth 6 | Set-Content -Path $resultsPath -Encoding UTF8
Write-Host ""
Write-Host "Wrote paired model summary: $resultsPath"
