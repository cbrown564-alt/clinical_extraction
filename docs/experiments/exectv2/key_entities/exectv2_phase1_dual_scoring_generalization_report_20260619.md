# ExECTv2 Phase 1 Dual-Scoring Generalization Report

- Date: `2026-06-19`
- Scope: ADR 0030 target indicators only: `Diagnosis`, `SeizureFrequency`,
  `Prescription`, `Investigations`
- Policy: v0.42 projection behavior frozen; no projection-rule tuning; no locked
  test rows inspected
- Mode: no model calls for this report

## Commands

Verified the saved v0.42 dev25 replay under both scoring keys:

```powershell
uv run python scripts\phase0_dual_scoring.py
```

Extracted existing dev140 comparator metrics from the saved focused-route source
JSON:

```powershell
@'
import json
from pathlib import Path
TARGET=("Diagnosis","SeizureFrequency","Prescription","Investigations")
report=json.loads(Path('experiments/exectv2_family_routed_with_focused_diagnosis_route_dev140_gpt41mini_20260618.json').read_text())
print(f"source={report['pipeline_family']} split={report['split']} stage={report['stage']} rows={report['row_count']}")
for c in report['candidates']:
    print('\n'+c['name'], c['ownership'])
    rr=c['routed_primary_recovery']
    hs=rr['headline_scores']
    ca=c['cui_audit']['per_entity']
    for ind in TARGET:
        h=hs[ind]['f1']
        b=ca[ind]['benchmark_f1']
        s=ca[ind]['semantic_f1']
        print(f"{ind}: headline={h:.4f} benchmark={b:.4f} semantic={s:.4f} gap={h-b:.4f}")
    overall=c['cui_audit']['overall']
    print(f"routed_headline_overall={rr['overall']['f1']:.4f}")
    print(f"overall benchmark_raw={overall['benchmark_f1_raw_llm']:.4f} after_cui={overall['benchmark_f1_after_cui_projection']:.4f} semantic={overall['semantic_f1']:.4f}")
'@ | uv run python -
```

## Surfaces

| Surface | Artifact | Rows | Model/source | Replay/live status |
| --- | --- | ---: | --- | --- |
| v0.42 dev25 dual score | `experiments/exectv2_target_indicators_single_call_v042_reproject_v041live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl` | 25 | local Qwen saved v0.41 live raw, v0.42 no-call projection | no-call replay |
| dev140 target comparators | `experiments/exectv2_family_routed_with_focused_diagnosis_route_dev140_gpt41mini_20260618.json` | 140 | existing GPT-4.1-mini / deterministic routed artifacts | saved artifact replay |
| ADR 0030 dev140 target report | `experiments/exectv2_adr0030_target_indicator_report_dev140_20260619.json` | 140 | derived target readout from the focused-route source JSON | existing report |

No exact v0.42 single-call local-Qwen dev140 replay artifact was found. A new
live dev140 call would create a new artifact rather than answer the smallest
available no-call generalization check.

## Dev25 v0.42 Dual Score

Same predictions, same 25 letters, two keys:

| Indicator | Headline F1 | Benchmark F1 | Semantic F1 | Headline - benchmark |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0.9376 | 0.2857 | 0.2857 | +0.6519 |
| SeizureFrequency | 0.9811 | 0.6885 | 0.6885 | +0.2926 |
| Prescription | 0.9250 | 0.1205 | 0.1205 | +0.8045 |
| Investigations | 0.9756 | 0.5854 | 0.6829 | +0.3902 |
| Overall | 0.9487 | 0.3675 raw / 0.3816 after CUI projection | 0.3816 | about +0.57 |

This verifies the Phase 0 reconciliation numbers. The dev25 `>0.900` result is
a headline-key result, not benchmark-comparable evidence.

## Dev140 Held-Out Comparators

Existing dev140 target artifacts do not include an exact v0.42 local-Qwen
single-call replay, but they are the safest held-out development surface
currently available. They show target-key behavior on 140 development letters
without spending new calls.

| Candidate | Ownership | Headline overall | Benchmark raw | Benchmark after CUI | Semantic |
| --- | --- | ---: | ---: | ---: | ---: |
| deterministic_all9 | `rules_only` | 0.7301 | 0.3586 | 0.3540 | 0.3706 |
| llm_only_all_entities | `llm_first` | 0.4313 | 0.0000 | 0.1110 | 0.1151 |
| hybrid_all_entities | `hybrid` | 0.5684 | 0.1810 | 0.1917 | 0.2195 |
| family_routed_llm_first | `llm_first_with_hybrid_sf_route` | 0.5592 | 0.0593 | 0.1789 | 0.1833 |
| family_routed_with_focused_diagnosis_route | `llm_first_with_hybrid_diagnosis_and_sf_routes` | 0.7081 | 0.1486 | 0.2316 | 0.2941 |

Best existing dev140 headline by target indicator from the ADR 0030 report:

| Indicator | Best candidate | Headline F1 |
| --- | --- | ---: |
| Diagnosis | deterministic_all9 | 0.7302 |
| SeizureFrequency | deterministic_all9 | 0.7277 |
| Prescription | deterministic_all9 | 0.9072 |
| Investigations | llm_only_all_entities | 0.7475 |

Only Prescription clears the `>0.900` headline threshold on existing dev140
target artifacts. No existing dev140 comparator clears all four indicators.

## Interpretation

Reject the v0.42 headline generalization claim as currently supported. The exact
dev25 v0.42 replay reproduces the high headline score, but the same predictions
remain near the established benchmark-key ceiling. Existing dev140 target
comparators show a large headline drop and no all-four-indicator clearance, with
benchmark-key results still far below a paper-comparable claim.

Revised claim language: v0.42 is a dev25 no-call projection artifact on a
lenient target headline key. Generalization to dev140 is unproven until an exact
frozen v0.42 dev140 single-call replay/live artifact exists, and any such
readout must report both the headline key and benchmark key.

Next task: create or locate an exact v0.42 dev140 local-Qwen single-call
saved-output artifact only after predeclaring the run cost and purpose; otherwise
continue treating existing dev140 comparators as the held-out warning signal.
