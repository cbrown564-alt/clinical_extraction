# Retained Evidence Manifest

Last rebuilt: 2026-07-14
Architecture-boundary note updated: 2026-07-15

This is the human-readable view of
[`retained_evidence_manifest.json`](retained_evidence_manifest.json). The JSON
file owns the reduced architecture freeze plus selected paths, hashes, byte
sizes, retrieval method, dataset and split
metadata, scorer, model role, prompt/program version, replay mode, repair policy,
claim boundary, executable replay expectation, and the source/config/scorer/test
closure needed to regenerate each reference. The full run registry remains
historical lineage; it is not a list of what the reduced repository must keep.

Validate the selected evidence from the repository root:

```sh
source .venv/bin/activate
python scripts/check_retained_evidence_manifest.py
python scripts/verify_reference_evidence.py
python scripts/check_exectv2_model_led_audit.py
python scripts/analyze_exectv2_model_led_dev140_regressions.py
```

The structural check fails if a frozen policy or selected file is missing or
changed, a run has drifted from its registry metadata, a closure path is
missing, or the two-task × three-family matrix is incomplete. The replay check
rebuilds or re-scores all six cells from current code and saved outputs without
model calls. The ExECT architecture check separately replays the selected
decision-0040 supporting package from historical Git blobs and compares only
aggregate output. Hashes and byte sizes for retained text artifacts use canonical LF
line endings so the same Git content verifies identically on Windows and Unix
checkouts.

The five largest selected ExECT replay files use Git LFS. Their manifest entries
record both the canonical content fingerprint and the immutable LFS object ID.
Run `git lfs pull` after cloning if LFS objects were not downloaded during
checkout; CI requests them explicitly.

## Architecture freeze

Freeze `reduced_reference_architecture_20260714` records:

- source commit `465621341c6af59f2fc028be7bf5f9e325739c50`;
- Python 3.11 plus the exact dependency declaration and lock;
- every retained reference-cell ID;
- exact prompt, scorer, split, repair, model, split-runbook, quality-workflow,
  and dependency policy fingerprints;
- the retained runtime identifiers and the honest three-of-six model-panel
  boundary; and
- the no-call verification commands required before evidence changes.

The freeze does not authorize model calls. New calls require a predeclaration;
semantic changes require a new freeze ID and complete replay.

Decision 0040 is the accepted family contract for the final ExECT model
comparison. Its durable configurations, corrected audit, and aggregate-only
Git-blob replay are selected supporting architecture evidence. The replay
reproduces family ownership, `state_profile`, attribution, regression,
schema/parse, and exact-evidence records without model calls or test60 row
inspection. The selected `v08` reference row remains a historical development
control rather than proof of the final architecture, and the three corrected
historical rows are not promoted as the final model panel.

## Reference matrix

| Task | Family | Retained run | Split | Headline result | Boundary |
| --- | --- | --- | --- | --- | --- |
| ExECTv2 | Rules only | `exectv2_deterministic_all9_dev_20260714` | dev140 | strict benchmark item F1 `0.3548`; evidence validity `1.0` | Incomplete development reference; not the operational control or benchmark reproduction |
| ExECTv2 | LLM only | `exectv2_gepa_dedup_gpt41mini_h2mb8_20260628` | dev140 | clinical-headline F1 `0.7393` | Negative development comparator; optimizer-only development sub-split used |
| ExECTv2 | LLM with rules | `exectv2_holistic_finding_assembly_v08_dev140_p7fix_gpt41mini_20260702` | dev140 | clinical-headline F1 `0.9189` | Historical development performance control; does not meet decision 0040; primary score reproduces, companion CUI scorer currently replays at `0.4791` versus recorded `0.4729` |
| Gan 2026 | Rules only | `gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_gpt41mini_2026-06-07` | validation750 | `697/750` Purist overall; `688/741` among rendered rows | No-call validation comparator |
| Gan 2026 | LLM only | `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07` | validation750 | `581/750` Purist | Single-pass validation comparator; grounding metric differs from LLM with rules |
| Gan 2026 | LLM with rules | `gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07` | validation750 | `661/748` Purist among rendered rows | Single-call validation reference; fixed operational result is separate |

These six cells are the minimum scientific comparison set. They do not require
keeping every prompt, candidate, ablation, report, UI adapter, or runner that led
to them. The ExECT LLM-with-rules cell does require the five saved producer outputs named
by its assembly config; those inputs are selected and hash-checked here.

## Supporting evidence packages

| Package | Story support | What is proven | What remains open |
| --- | --- | --- | --- |
| Gan holdout quality and efficiency | S2, S3, S8 | Single-pass `364/450` versus V12 `379/450` Purist; one versus three cold model passes per note | Tokens, cost, latency, hardware, retries, and cache use were not measured in a matched run and must not be claimed |
| Gan reliability | S5, S8 | Existing grounding, calibration, routing, consistency, robustness, and operational analyses | Deployment validation and final matched cross-task scorecard |
| ExECT model transfer | S4, S5, S8 | The historical graph and corrected decision-0040 architecture replay run with GPT-4.1-mini, DeepSeek, and Qwen; the replay reproduces corrected aggregates, `state_profile`, attribution, regression, schema/parse, and exact-evidence accounting | Three remaining exact models; cross-task unknown-versus-rate analysis |
| ExECT model-led dev140 regressions | S4, S8 | On 319 changed model/family rows, the family-local view records 160 rescues, 41 regressions, and 118 changed-still-wrong outcomes with exact evidence; SF is retained, while Diagnosis and Prescription require a bounded candidate | Frozen candidate replay, test60 transfer, and the final six-model comparison |
| Cross-task ablation | S1, S6 | Normalization contributes on both tasks; current evidence gate is score-inert | Schema/evidence rejection and repair challenge fixtures; remaining stage isolation |
| ExECT calibration and confidence | S5, S8 | Internal correctness rule: Brier `0.2225`, base-rate `0.2340`, ECE `0.0587`; aggregate-only test60 model-confidence AUROC `0.5394` / `0.5503` / `0.4895` for GPT-4.1-mini / historical DeepSeek / Qwen, with neither fixed routing rule adopted | Deployment calibration, thinking-enabled DeepSeek V4 Flash confidence, and a six-model confidence comparison |
| ExECT published metrics | S7 | Paper-derived normalized-phrase, CUI, and all-feature scorer plus a no-call all-nine-entity dev140 replay: macro item F1 `0.5687`, `0.7144`, and `0.6020` | Original system, annotation process, and reported `0.87`/`0.90` validation scores are not reproduced |
| Annotation quality | S7, S9 | Generated 584-record taxonomy hash-checks 13 retained sources, maps all 57 explicitly cited letters, separates original scores from sensitivity handling, and records three open and one fixed direct gold issues | Ten historical Diagnosis concept rows remain aggregate-only; independent clinical review is still required for clinical-validity claims |

## Authority and deletion rule

Claim status is owned by
[`docs/canon/10_paper_provenance.md`](../canon/10_paper_provenance.md). This
manifest owns the files selected as proof. `experiments/registry.jsonl` owns run
lineage.

A file outside the manifest is not automatically deletable: source, configuration,
scorer, test, and regeneration dependencies still have to be traced. Once that
closure is recorded, an unselected candidate must be removed as a complete
vertical slice rather than moved into another tracked archive.
