# 02 — Processing steps

Last updated: 2026-07-31

Exact source, configuration, scorer, test, and replay paths are in the
[retained evidence index](../experiments/retained_evidence_manifest.md).

This page is the abstract. The arrows below compress each method into four
steps, which is too few to explain ownership, improvement, regression, or
evidence — the selected Gan hybrid expands "deterministic selection and
normalization" into schema repair, event normalization, label resolution, and
ten ordered repair families.

For the full account — every stage, its owner, whether it may change clinical
meaning, its implementation, and its governing test — read the
[architecture layer](../architecture/README.md). Those documents are generated
from machine-readable stage manifests and from teaching cases that execute the
real pipelines, so they cannot drift from the code without failing CI.

## Gan 2026

```text
letter
  → rules or model extract seizure-frequency facts
  → deterministic selection and normalization where the method permits it
  → Gan label formatting
  → Purist and Pragmatic scoring
```

The selected comparison has one rules-only run, one LLM-only run, and one run
that combines an LLM event extractor with deterministic normalization. The
saved multi-model result (`V12`) is an aggregate comparison, not runnable code.

## ExECTv2

```text
letter
  → task-specific extractors
  → diagnosis, seizure-frequency, prescription, and investigation transforms
  → combine clinical findings
  → score clinical fact recovery and the stricter companion metrics
```

The selected comparison has a deterministic all-nine baseline, a GEPA LLM-only
negative comparison, and the historical LLM-with-rules development control
(`v08`). `v08` remains reproducible, but its deterministic Prescription
producer and Seizure Frequency extractor union do not meet the final family
ownership boundary.

New final-comparison evidence must follow
[decision 0040](../decisions/0040-final-exect-llm-with-rules-family-ownership.md):
the named model supplies all four families, Prescription uses bounded
post-model correction rather than deterministic substitution, and Seizure
Frequency uses attributable projection and suppression without an independent
extractor union.

Retained evidence index v3 fixes source commit `46562134` and records the exact
dependencies, prompts, scorers, split rules, repairs, model policy, and CI
workflow. Any change that can alter a prediction requires a new recorded
version and a complete replay. This rule does not authorize model calls.

Saved-output replays found normalization gains of +0.0389 on ExECT dev140 and
+0.0293 on Gan dev750. Retained Gan artifacts use the legacy identifier
`validation750`. The exact-evidence check changed neither score;
rejection and repair tests provide its separate evidence.
