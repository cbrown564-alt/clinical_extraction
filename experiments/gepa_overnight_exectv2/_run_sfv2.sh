#!/usr/bin/env bash
set -u
cd /c/Users/cbrow/Code/clinical_extraction
RID=exectv2_gepa_sf_verify_v2_deepseekchat_20260629
for attempt in 1 2 3 4; do
  if [ -f "experiments/$RID.json" ]; then echo "[orch] $RID complete"; break; fi
  echo "[orch] $RID attempt $attempt $(date +%H:%M:%S)"
  uv run python experiments/gepa_sf_verify_v2_deepseek_exectv2.py
  sleep 5
done
echo "[orch] sf-verify-v2 done $(date +%H:%M:%S)"
