#!/usr/bin/env bash
set -u
cd /c/Users/cbrow/Code/clinical_extraction
run() {  # $1 = run_id (summary marker), $2 = launcher arg
  for attempt in 1 2 3 4; do
    if [ -f "experiments/$1.json" ]; then echo "[orch] $1 complete"; return 0; fi
    echo "[orch] $1 attempt $attempt $(date +%H:%M:%S)"
    uv run python experiments/gepa_recall_lanes_deepseek_exectv2.py $2
    sleep 5
  done
}
run exectv2_gepa_recall_lanes_deepseekchat_20260628 ""
run exectv2_gepa_baseline_multifamily_deepseekchat_20260628 "--baseline"
echo "[orch] all arms done $(date +%H:%M:%S)"
