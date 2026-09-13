# Pilot review extension v0.7

Development-only results from saved agy outputs and authored annotations.
The [pilot review](../../../docs/longitudinal/pilot_disagreement_report.md)
owns interpretation; these files own the inspectable evidence. No new model calls,
clinical validation, source-seed selection or corpus release occurred.

| Artifact | Meaning |
| --- | --- |
| `temporal_adjudication.json` | Source-backed decisions for all 144 previously flagged pairs; grouped comparisons preserve every job ID. AI development review, not clinical agreement. |
| `annotation_amendments.json` | Four temporal corrections and patient 011's first-reinterpretation field, with before/after values. |
| `source_snapshot/` | Exact pre-amendment annotations/manifests; source letters and query references unchanged. |
| `link_alignment.json` | Evidence-constrained, mutually unique endpoint candidates and matched relation counts. Unaligned links remain unresolved. |
| `query_field_ablation.json` | Recomputed Q1–Q5 answers for all 240 requests under eight field variants; no reference lookup during prediction. |
| `query_mechanism_review.json` | Every remaining full-input mismatch and its representation/evaluator limit. |
| `review_summary.json` | Structural/coverage checks, temporal review coverage, recorded machine timing and missing human/family timing. |
| `source_use_audit.json` | ExECT release metadata, unresolved Gan terms, unchanged split-manifest hashes and empty next-batch seed selection. |
| `language_audit.json` | Rendered-payload inspection; no deployed prompt or schema change. |
| `verification.json` | Final checks, replay parity, source preservation and known unrelated failures. |
| `effort_session_template.json` | Empty prospective human timing record; not measured effort. |

Historical commands used for the v0.7 artifact version:

```bash
python scripts/longitudinal/review_pilot_alignment.py
python scripts/longitudinal/evaluate_query_witnesses.py
python scripts/longitudinal/summarize_pilot_review.py
```

Adjudication, amendments and mechanism review are authored review records; they
are not automatically regenerated clinical judgments. The summary checks that
all temporal decisions still refer to the original frozen comparison values.
The recorded input/program hashes identify the v0.7 working-tree version. Current
annotations and the query evaluator have since advanced to v0.8; these commands
are not an instruction to overwrite frozen v0.7 files. Use the
[v0.8 entry](../pilot_v0.8/README.md) for current replay. Historical
v0.3–v0.6 measurements and raw captures are preserved separately.
