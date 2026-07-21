# How it works

`seizure-frequency` sends the selected Gan v0.5 structured-event payload, parses
the event ledger and selection, applies the selected seizure-frequency repair
path, checks exact evidence, and returns one current answer. A deterministic
step that changes the answer is listed under `deterministic_changes`.

`clinical-findings` makes one structured four-family call. The named model
supplies candidates for Diagnosis, Seizure Frequency, Prescription, and
Investigations. The retained family transforms normalize, project, suppress,
or add bounded findings. Every final finding keeps its evidence and recorded
deterministic actions. No rules-only producer silently replaces a model-led
family.

`all` is orchestration, not a merged prompt. It runs both calls independently
and therefore normally uses two calls per note. A failure is recorded inside
its workflow block without deleting the other result.

Prompt, schema, rule-set, and package versions plus SHA-256 asset hashes are in
run metadata. Model content is kept out of default files and appears only in an
explicit private trace.

## Source map for prediction-changing code

The short public path starts in `clinical_extraction_local`:

- `seizure_frequency/pipeline.py` builds the v0.5 call and records attribution.
  The selected internal implementation is
  `clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py`.
  Its schema repair is in `contract/schema_repair.py`; current-time selection,
  diary aggregation, named clinical repair families, and final label rendering
  are in `llm/llm_structured_temporal.py`,
  `llm/llm_structured_monthly_diary.py`,
  `llm/llm_structured_repair_families.py`, and `normalize.py`.
- `clinical_findings/pipeline.py` builds and parses the one-call result. The
  final family assembly is in `clinical_extraction/operational/exect.py`.
  Diagnosis, Prescription, and Investigations changes are in
  `tasks/epilepsy_phenotyping/exectv2/assembly/lenses/`; seizure-frequency
  projection and suppression are in `deterministic/sf_state_projection.py` and
  `deterministic/sf_unknown_suppression.py`.
- Shared format-only retry eligibility and the check that scalar clinical
  values did not change are in `clinical_extraction/core/local_structured_output.py`.

The first prediction owner is the model. When any listed deterministic file
adds, removes, chooses, or changes a clinical fact, the trace records that
action as deterministic-owned rather than crediting it to the model.
