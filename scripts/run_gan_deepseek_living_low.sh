#!/usr/bin/env bash
# Re-run living DeepSeek gan_llm_extract at thinking enabled + reasoning_effort=low.
# Archives the previous provider-default (high) living cells first so resume
# does not reuse those raws. Does not promote.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source .venv/bin/activate
export PYTHONUNBUFFERED=1

stamp="$(date -u +%Y%m%dT%H%M%SZ)"
log_dir="$ROOT/scratch/logs"
mkdir -p "$log_dir"

archive_cell() {
  local path="$1"
  local name
  name="$(basename "$path")"
  if [[ -e "$path" ]]; then
    local dest="${path}.provider_default_${stamp}"
    mv "$path" "$dest"
    echo "archived $path -> $dest"
  else
    echo "no existing $name cell to archive"
  fi
}

archive_cell "$ROOT/experiments/paper/gan_llm_extract/deepseek_v4_flash/dev750"
archive_cell "$ROOT/scratch/holdout/paper/gan_llm_extract/deepseek_v4_flash/test450"

python -m clinical_extraction.paper verify \
  --method gan_llm_extract \
  --model deepseek_v4_flash \
  --split dev750

for split in dev750 test450; do
  log="$log_dir/gan_llm_extract_deepseek_v4_flash_${split}_living_low_${stamp}.log"
  echo "starting $split -> $log"
  python -m clinical_extraction.paper run --live \
    --method gan_llm_extract \
    --model deepseek_v4_flash \
    --split "$split" \
    --progress-every 1 \
    | tee "$log"
done
