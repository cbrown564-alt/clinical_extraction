# Phase 2 development evidence v0.8

The [pilot review](../../../docs/longitudinal/pilot_disagreement_report.md) owns
interpretation and phase disposition. This directory preserves the evidence for
the schema revision, link review and measured independent AI annotation effort.
No expert validation, human timing, generated corpus or benchmark performance is
claimed. The 18-call agy probe has zero incremental per-call charge according to
the user's confirmation; provider telemetry does not report billing.

| Artifact | Meaning |
| --- | --- |
| `annotation_amendments.json`, `source_snapshot/` | Four explicit prior non-use assertions gain supporting scope evidence; original schema/guide and changed cases are preserved. |
| `preserved_inputs.json` | Baseline hashes for all 36 unchanged letters and 12 unchanged query-reference files. |
| `link_adjudication.json` | All 89 formerly unaligned instances reviewed in 65 groups; supported relationships, alternatives and errors remain distinct. |
| `query_field_ablation.json` | Nine variants across 240 fixed Q1–Q5 requests; raw three-state diagnostic answers and evidence. |
| `query_mechanism_review.json` | All 11 remaining conservative diagnostic gaps, their reference evidence and Phase 4 implementation needs. |
| `timed_pass/manifest.json`, `timed_pass/inputs/` | Declared 18 calls, three selected patients, six activities, exact payload hashes and charge basis. Full histories; no expected answers. |
| `timed_pass/outputs/attempts/` | Original stdout/stderr, attempt metadata and parsed output; no semantic repair. |
| `timed_pass/analysis.json` | Replayed timing, schema/grounding/offset checks and limited representation disagreement. |
| `timed_pass/quality_review.json` | Structural/offset failures and unresolved reporter attribution, with explicit dispositions. |
| `language_audit.json` | Inspection of model-facing schema and all prepared payloads. |
| `completion_checks.json`, `verification.json` | Evidence-package checks, broader code checks and known unrelated failures. |

Offline reproduction, with the repository environment activated:

```bash
source .venv/bin/activate
python scripts/longitudinal/evaluate_query_witnesses.py
python scripts/longitudinal/summarize_timed_annotation_probe.py
python scripts/longitudinal/verify_phase2_pilot.py
```

These regenerate only current v0.8 diagnostic/check files and make no model calls.
Review judgments and amendments are authored records; verification checks their
coverage and source hashes, not their clinical correctness. v0.7 temporal review,
older references and original agy failures remain separate historical evidence.

The timing probe uses a fresh temporary project per call and rejects observed
tool steps. A tool catalog is still present in the CLI environment; this is an
observed no-tool run, not proof that the provider was technically tool-free.
Temporal and relationship tasks include assertion extraction and shared JSON
output, so their duration is not the isolated cost of those fields. Three
selected cases do not estimate human labor or a 300-patient workload.
