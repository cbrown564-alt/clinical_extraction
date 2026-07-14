# Retained Evidence Manifest

Last rebuilt: 2026-07-14

This is the human-readable view of
[`retained_evidence_manifest.json`](retained_evidence_manifest.json). The JSON
file owns selected paths, hashes, byte sizes, retrieval method, dataset and split
metadata, scorer, model role, prompt/program version, replay mode, repair policy,
claim boundary, executable replay expectation, and the source/config/scorer/test
closure needed to regenerate each reference. The full run registry remains
historical lineage; it is not a list of what the reduced repository must keep.

Validate the selected evidence from the repository root:

```sh
source .venv/bin/activate
python scripts/check_retained_evidence_manifest.py
python scripts/verify_reference_evidence.py
```

The structural check fails if a selected file is missing or changed, a run has
drifted from its registry metadata, a closure path is missing, or the two-task ×
three-family matrix is incomplete. The replay check rebuilds or re-scores all six
cells from current code and saved outputs without model calls. Hashes and byte
sizes for retained text artifacts use canonical LF line endings so the same Git
content verifies identically on Windows and Unix checkouts.

## Reference matrix

| Task | Family | Retained run | Split | Headline result | Boundary |
| --- | --- | --- | --- | --- | --- |
| ExECTv2 | Rules only | `exectv2_deterministic_all9_dev_20260714` | dev140 | strict benchmark item F1 `0.3548`; evidence validity `1.0` | Incomplete development reference; not the operational control or benchmark reproduction |
| ExECTv2 | LLM only | `exectv2_gepa_dedup_gpt41mini_h2mb8_20260628` | dev140 | clinical-headline F1 `0.7393` | Negative development comparator; optimizer-only development sub-split used |
| ExECTv2 | Hybrid | `exectv2_holistic_finding_assembly_v08_dev140_p7fix_gpt41mini_20260702` | dev140 | clinical-headline F1 `0.9189` | Current development performance control; primary score reproduces, companion CUI scorer currently replays at `0.4791` versus recorded `0.4729` |
| Gan 2026 | Rules only | `gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_gpt41mini_2026-06-07` | validation750 | `697/750` Purist overall; `688/741` among rendered rows | No-call validation comparator |
| Gan 2026 | LLM only | `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07` | validation750 | `581/750` Purist | Single-pass validation comparator; grounding metric differs from hybrid |
| Gan 2026 | Hybrid | `gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07` | validation750 | `661/748` Purist among rendered rows | Single-call validation reference; frozen operational result is separate |

These six cells are the minimum scientific comparison set. They do not require
keeping every prompt, candidate, ablation, report, UI adapter, or runner that led
to them. The ExECT hybrid cell does require the five saved producer outputs named
by its assembly config; those inputs are selected and hash-checked here.

## Supporting evidence packages

| Package | Story support | What is proven | What remains open |
| --- | --- | --- | --- |
| Gan holdout quality | S2, S3, S8 | Single-call operational `364/450` versus V12 ceiling `379/450` Purist | Matched calls, tokens, cost, latency, model, hardware, and cache table |
| Gan reliability | S5, S8 | Existing grounding, calibration, routing, consistency, robustness, and operational analyses | Deployment validation and final matched cross-task scorecard |
| ExECT model transfer | S4, S5, S8 | Same-core GPT-4.1-mini, DeepSeek, and Qwen evidence, with permitted dev140 cached outputs and configs retained | Three remaining exact models and cross-model overconfidence analysis |
| Cross-task ablation | S1, S6 | Normalization contributes on both tasks; current evidence gate is score-inert | Schema/evidence rejection and repair challenge fixtures; remaining stage isolation |
| ExECT calibration | S5, S8 | Internal correctness rule: Brier `0.2225`, base-rate `0.2340`, ECE `0.0587` | Out-of-sample model-reported confidence and bounded routing verdict |
| Annotation quality | S7, S9 | Family ledgers, canonical SF/Dx analyses, and blind replication are retained | One complete generated taxonomy with every cited case, handling, sensitivity, and review status |

## Authority and deletion rule

Claim status is owned by
[`docs/canon/10_paper_provenance.md`](../canon/10_paper_provenance.md). This
manifest owns the files selected as proof. `experiments/registry.jsonl` owns run
lineage.

A file outside the manifest is not automatically deletable: source, configuration,
scorer, test, and regeneration dependencies still have to be traced. Once that
closure is recorded, an unselected candidate must be removed as a complete
vertical slice rather than moved into another tracked archive.
