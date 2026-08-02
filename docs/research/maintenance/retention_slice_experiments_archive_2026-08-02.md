# Decision 0048 retention slice: `experiments/archive/`

Date: 2026-08-02  
Status: classified — **keep**  
Decision: [0048](../../decisions/0048-comprehension-and-handoff-refactor.md)  
Scope: every tracked file under `experiments/archive/`

## Inventory

Exactly three tracked files, all under
`experiments/archive/gan2026_validation750_iterations/`:

| Path | Role |
| --- | --- |
| `.../gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_gpt41mini_2026-06-07.md` | Human-readable companion report for Gan rules-only reference cell |
| `.../gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07.md` | Companion for Gan LLM-only reference cell |
| `.../gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.md` | Companion for Gan LLM-with-rules reference cell |

No other tracked files exist under `experiments/archive/`.

## Reference evidence

Each Markdown path is listed with `sha256` and `bytes` in
`docs/experiments/retained_evidence_manifest.json` under the corresponding
Gan reference cell (`gan2026_rules_only_reference`,
`gan2026_llm_only_reference`, `gan2026_hybrid_reference`) `artifacts` array,
alongside the JSONL replay input. `scripts/check_retained_evidence_manifest.py`
and `clinical_extraction.core.retained_evidence` fingerprint these as text
artifacts (CRLF→LF) and fail on missing path or hash drift.

The same three paths appear in `experiments/registry.jsonl` as
`artifact_paths` for the 2026-06-07 three-way comparison runs.

Replay verification uses the JSONL inputs, not the Markdown tables, but the
Markdown files remain part of the frozen reference-cell artifact closure and
record the original run summary plus permitted-development row tables.

## Decision: KEEP

| Gate | Result |
| --- | --- |
| Retained-evidence / reference cell | **Required** — hashed artifacts on all three Gan reference cells |
| Registry lineage | Listed for the three-way comparison runs |
| Code/tests load Markdown for prediction | No (JSONL is the replay input) |
| Unique explanatory value | Yes — original run reports for the six-method reference package |

Deleting any of these three files would break retained-evidence validation
without a coordinated manifest edit. Decision 0048 does not authorize dropping
reference-cell artifacts merely because they live under an `archive/` directory
name.

Owner: retained evidence index
([`docs/experiments/retained_evidence_manifest.json`](../../experiments/retained_evidence_manifest.json)
and [`docs/experiments/retained_evidence_manifest.md`](../../experiments/retained_evidence_manifest.md)).
Claim boundary remains the existing Gan reference-cell and paper-provenance
owners; these Markdown companions do not expand holdout permissions.

## Follow-up hygiene (completed same day)

Removed the stale mock-registry run
`gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13` from
`frontend/public/mock-data/registry.json`. Both listed artifact paths were
already pruned from the repository (JSONL and archive Markdown); the live
`experiments/registry.jsonl` retains only the aggregate-only test450 Markdown
companion. This does not change the keep decision for the three hashed archive
Markdown files above.

`scripts/check_doc_hygiene.py` mentions `experiments/archive/` only as a
preferred landing place instead of underscore-prefixed root directories; that is
guidance, not a keep/delete signal for these three files.

## Verification

```powershell
.venv\Scripts\python.exe scripts\check_retained_evidence_manifest.py
```

Passed after classification. No model calls; no locked-row inspection. No files
deleted in this slice.
