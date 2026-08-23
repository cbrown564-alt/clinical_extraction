#!/usr/bin/env bash
# Finish the remaining DeepSeek six-model cell-3 extracts, one live call at a
# time. Resumes saved rows. Does not archive, overwrite, promote, or inspect
# holdout rows. Omit --reasoning-effort: low is already the living DeepSeek
# setting.
#
#   cd /Users/cobro/code/clinical-extraction
#   caffeinate -i bash scripts/run_deepseek_cell3_overnight.sh
#
# Expected leftovers when this was written: gan_llm_extract dev750 331/750,
# gan_llm_extract test450 missing at living-low (old provider-default archived),
# exect_llm_extract dev140 94/140, exect_llm_extract test60 not started.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source .venv/bin/activate
set -a
# shellcheck disable=SC1091
[ -f .env ] && . ./.env
set +a
export PYTHONUNBUFFERED=1

if [[ -z "${DEEPSEEK_API_KEY:-}" ]]; then
  echo "DEEPSEEK_API_KEY is not set" >&2
  exit 1
fi

stamp="$(date -u +%Y%m%dT%H%M%SZ)"
log_dir="$ROOT/scratch/logs"
mkdir -p "$log_dir"
summary="$log_dir/deepseek_cell3_overnight_${stamp}.summary"
log() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" | tee -a "$summary"; }

run_cell() {
  local method="$1"
  local split="$2"
  local progress="$3"
  local log_file="$log_dir/${method}_deepseek_v4_flash_${split}_overnight_${stamp}.log"

  log "start ${method} deepseek_v4_flash ${split} -> ${log_file}"
  if python -m clinical_extraction.paper run --live \
    --method "$method" \
    --model deepseek_v4_flash \
    --split "$split" \
    --progress-every "$progress" \
    2>&1 | tee "$log_file"
  then
    log "done ${method} ${split}"
    return 0
  fi
  log "FAILED ${method} ${split}"
  return 1
}

failed=0
run_cell gan_llm_extract dev750 10 || failed=1
run_cell gan_llm_extract test450 10 || failed=1
run_cell exect_llm_extract dev140 10 || failed=1
run_cell exect_llm_extract test60 10 || failed=1

if [[ "$failed" -eq 0 ]]; then
  log "overnight queue complete"
  exit 0
fi
log "overnight queue finished with failures; see ${summary}"
exit 1
