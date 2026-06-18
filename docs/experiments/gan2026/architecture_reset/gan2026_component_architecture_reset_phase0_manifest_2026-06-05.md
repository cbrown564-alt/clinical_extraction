# Gan 2026 Component Architecture Reset Phase 0 Manifest

Date: 2026-06-05

Status: in progress. This manifest freezes the mechanics-review surface for the
component architecture reset. It does not authorize locked-test row-level review,
new holdout development, or benchmark-comparable claims.

## Row Scope

Decision: `validation250` means the first 250 rows returned by
`load_records_for_split("validation")` from `gan2026_split_v1`.

- Split manifest: `data/Gan (2026)/splits/gan2026_split_v1.json`
- Dataset: `data/Gan (2026)/synthetic_data_subset_1500.json`
- Row count: 250
- First source row index: 10
- Last source row index in the frozen prefix: 5584
- Row-level inspection: allowed
- Locked test row-level inspection: forbidden

Source row indices:

```text
10,40,79,103,128,156,180,182,187,190,198,212,218,243,278,280,338,409,419,446,466,467,531,598,659,665,678,694,704,725,731,743,744,763,790,816,849,854,869,891,899,959,960,978,987,1030,1046,1070,1094,1165,1171,1207,1223,1249,1281,1317,1357,1363,1413,1454,1486,1573,1591,1596,1597,1636,1640,1687,1694,1695,1706,1707,1772,1773,1790,1794,1866,1880,1887,1914,1922,1923,1979,1980,2023,2080,2094,2114,2149,2166,2228,2233,2245,2259,2354,2366,2369,2374,2425,2427,2435,2437,2440,2456,2459,2487,2513,2541,2548,2554,2558,2609,2622,2628,2678,2681,2698,2731,2740,2748,2759,2762,2765,2776,2789,2812,2822,2824,2877,2887,2907,2932,2938,2965,2992,3015,3048,3058,3082,3095,3113,3118,3137,3224,3242,3261,3262,3281,3297,3325,3356,3371,3436,3468,3469,3482,3493,3507,3512,3528,3532,3534,3600,3623,3643,3681,3682,3710,3753,3766,3774,3791,3801,3806,3827,3846,3849,3889,3892,3940,3949,3988,3995,3999,4022,4026,4092,4100,4110,4116,4173,4243,4258,4337,4345,4368,4402,4410,4478,4480,4496,4562,4563,4574,4592,4597,4624,4631,4690,4694,4700,4709,4731,4732,4771,4839,4842,4910,4919,4926,4951,4956,4992,4994,5040,5082,5092,5110,5121,5136,5141,5197,5210,5221,5248,5331,5345,5351,5379,5406,5476,5490,5491,5504,5507,5528,5534,5551,5567,5584
```

## Allowed Source Artifacts

Allowed as mechanics-review inputs:

- validation-row-level deterministic baseline and candidate artifacts;
- validation-row-level state graph node and projection artifacts;
- validation-row-level LLM candidate, selected-state, selected-fact, or
  evidence-selection artifacts;
- validation-row-level repair, replay, normalization, and projection-ablation
  artifacts;
- validation-row-level safety-floor, verifier, action-router, and gate artifacts;
- validation-row-level component evidence, source trace, and audit matrix
  artifacts.

Not allowed as mechanics-review inputs:

- locked-test row-level artifacts;
- locked-test row-level failures;
- score-driven development conclusions based on locked-test rows.

Locked-test aggregate summaries may be cited only as motivation for why the
reset is needed. They must not determine component schema, routing, projection,
repair, or selection decisions.

## Model Routes And Prompt Versions

Phase 0 and schema reconstruction use saved replays only.

Live GPT-4.1 mini, Qwen, or other model calls are not allowed during Phase 0.
Live calls may be reconsidered after the schema contract is frozen, but only
when the manifest names the model route, prompt version, cache/replay policy,
allowed output, and predeclared mechanics question. Live calls must not be used
for score-driven optimization during this reset.

## Allowed Outputs

Phase 0 may produce schema notes, candidate-set mappings, provenance mappings,
and review-ledger decisions. It must not produce new benchmark-comparable
claims, new locked-test row-level artifacts, or score-optimized component
changes.

## Initial ExtractedCandidate Schema

Decision: an `ExtractedCandidate` is one member of a row-level `CandidateSet`.
It is emitted after candidate identification and before selection,
normalization, projection, verification, or rendering.

Required fields:

- `candidate_id`
- `component_owner`
- `source_type`
- `source_artifact`
- `source_row_index`
- `candidate_kind`
- `event_type`
- `event_subtype`
- kind-specific detail object: `frequency`, `seizure_free`,
  `last_event_only`, `cluster_details`, `unknown_frequency`, or `no_reference`
- `temporality`
- `certainty`
- `certainty_reason`
- `assertion_status`
- `evidence_span`
- `source_ids`
- `extraction_issues`
- `clinical_or_policy`

Field constraints:

- `candidate_kind` must allow `frequency_rate`, `cluster_frequency`,
  `seizure_free`, `last_event_only`, `unknown_frequency`, and `no_reference`.
- `last_event_only` is used narrowly for a dated or relative last-event
  statement without an explicit seizure-free interval or recurring rate. It
  preserves temporal evidence for later selection, normalization, projection, or
  verification, but it must not render directly to a scorer-facing label during
  extraction.
- `evidence_span.text` is the canonical copied evidence text. Do not carry a
  separate `raw_text` field in `ExtractedCandidate`; if pre-repair model output
  is needed, keep it in a debug trace outside the candidate schema.
- `event_type` is broad and clinical. Allowed values are `seizure`,
  `seizure_like_event`, `non_epileptic_event`, and `unclear_event`.
- `event_subtype` is a source-near string or null, preserving semiology without
  forcing a normalized seizure taxonomy during extraction.
- Do not add `non_seizure_event` as a `candidate_kind`. Non-epileptic or proxy
  status belongs in `event_type`; `candidate_kind` describes the shape of the
  frequency-state evidence.
- `temporality` is the single field for whether the candidate is current,
  recent, historical, or unclear. Do not split it into multiple time fields at
  extraction time.
- `certainty` replaces separate uncertainty and contradiction flag lists. It is
  binary: `certain` or `uncertain`.
- `certainty_reason` is a fixed-list companion field used when `certainty` is
  `uncertain`. Allowed values are `vague_count`, `unclear_time_period`,
  `approximate_wording`, `conditional_statement`, and `other`.
- `temporality` is one of `current`, `recent`, `historical`, or `unclear`.
- `assertion_status` remains in the schema provisionally. Later review must
  assess whether it materially improves selection, verification, or error
  attribution. Allowed values are `asserted`, `negated`, `uncertain`, and
  `conditional`.
- `candidate_kind` determines which detail object is populated. At most one
  kind-specific detail object should be present for a candidate.
- `frequency` is used when `candidate_kind` is `frequency_rate`. It uses
  lightly typed string fields: `count`, `count_range`, `time_period`,
  `time_period_range`, and `source_phrase`.
- `seizure_free` is used when `candidate_kind` is `seizure_free`. It uses
  lightly typed string fields: `duration`, `anchor`, and `source_phrase`.
- `last_event_only` is used when `candidate_kind` is `last_event_only`. It uses
  lightly typed string fields: `event_timing`, `event_count`, and
  `source_phrase`.
- `unknown_frequency` is used when `candidate_kind` is `unknown_frequency`.
- `no_reference` is used when `candidate_kind` is `no_reference`.
- `unknown_frequency` and `no_reference` use only `source_phrase`.
- `cluster_details` is used when `candidate_kind` is `cluster_frequency`. It has
  only lightly typed string fields: `cluster_frequency`, `events_per_cluster`,
  `cluster_count`, and `cluster_period`. Do not duplicate cluster facts in any
  other detail object.
- Normalization and parsing belong to the Normalise stage. Extraction should
  preserve source-near text instead of canonical counts, periods, durations, or
  scorer-ready labels.
- Scorer labels must not appear in `ExtractedCandidate`.
- `clinical_or_policy` must be `clinical`.

Risk note:

- Kind-specific detail objects preserve high-fidelity clinical data, but may be
  harder for LLM extractors than a single generic detail object. Phase 1 should
  explicitly test whether extractors can reliably choose the right detail object
  without being distracted by the schema instructions.
- Extraction may record candidate-local uncertainty through `certainty_reason`,
  but it does not determine row-level ambiguity or conflict. If multiple
  candidates interact in ambiguous or conflicting ways, the router or verifier
  must judge that later from the candidate set and evidence.

Example ordinary rate candidate:

```json
{
  "candidate_kind": "frequency_rate",
  "frequency": {
    "count": "2",
    "count_range": null,
    "time_period": "month",
    "time_period_range": null,
    "source_phrase": "2 seizures per month"
  }
}
```

Example seizure-free candidate:

```json
{
  "candidate_kind": "seizure_free",
  "seizure_free": {
    "duration": "9 months",
    "anchor": "since last clinic review",
    "source_phrase": "seizure free for 9 months"
  }
}
```

Example last-event-only candidate:

```json
{
  "candidate_kind": "last_event_only",
  "last_event_only": {
    "event_timing": "in March",
    "event_count": "1",
    "source_phrase": "Last focal seizure occurred in March"
  }
}
```

Example cluster candidate:

```json
{
  "candidate_kind": "cluster_frequency",
  "cluster_details": {
    "cluster_frequency": "monthly",
    "events_per_cluster": "several",
    "cluster_count": null,
    "cluster_period": "month"
  }
}
```

Example unknown-frequency candidate:

```json
{
  "candidate_kind": "unknown_frequency",
  "unknown_frequency": {
    "source_phrase": "frequency remains unclear"
  }
}
```

Example no-reference candidate:

```json
{
  "candidate_kind": "no_reference",
  "no_reference": {
    "source_phrase": "no seizure frequency reference"
  }
}
```

## Initial CandidateSet Schema

Decision: a `CandidateSet` is a thin row-level envelope around extracted
candidates. It records provenance and assembly issues, but it does not select,
verify, project, render, or score.

Required fields:

- `source_row_index`
- `component_owner`
- `source_artifacts`
- `candidates`
- `assembly_issues`

Allowed `assembly_issues` examples:

- `missing_llm_replay`
- `invalid_candidate_schema`
- `duplicate_candidate_ids`
- `source_artifact_row_missing`

Forbidden fields:

- selected candidate or selected fact;
- final label;
- row-level ambiguity or conflict verdict;
- safety-floor or verifier action;
- projection policy;
- score result.

Example:

```json
{
  "source_row_index": 101,
  "component_owner": "gan2026_validation250_candidate_set_v0",
  "source_artifacts": [
    "deterministic_candidates_validation250.jsonl",
    "llm_structured_events_validation250_replay.jsonl"
  ],
  "candidates": [],
  "assembly_issues": []
}
```

## Temporarily Frozen Legacy Components

Decision: the following legacy components are frozen from behavior changes
during the reset. They may be inspected, replayed from allowed saved artifacts,
and mapped into the new stage model, but they must not be tuned, expanded, or
renamed in code until the disposition ledger assigns each one a final action.

- `hybrid_adjudicator_raw`
- `adapter_layer`
- `H5 repair policy`
- `selective_safety_floor_gate_v0`
- `state_graph_projection`
- `boundary/renderer typed-event layer`
- `untagged_nonprediction_release`
- `staged_action_policy`
- `H6/H9/H10 sidecars`
- `component_evidence_matrix`

Allowed dispositions for later review:

- keep unchanged;
- keep but rename;
- split into multiple stages;
- merge into another component;
- demote to diagnostic-only;
- delete from the assembly path.

Open follow-up:

- test whether saved validation250 extractors can reliably populate the
  kind-specific detail objects, especially when using LLM-derived candidates.
  Initial smoke: ``.

## Review Ledger

| Decision | Status | Resolution | Rationale |
| --- | --- | --- | --- |
| Validation250 row scope | accepted | Use the first 250 rows of the validation split from `gan2026_split_v1`. | Existing split protocol and saved artifacts already use this meaning; keeping it preserves comparability. |
| Allowed saved source artifacts | accepted | Allow validation-row-level artifacts needed to reconstruct component mechanics; exclude locked-test row-level artifacts entirely. | The reset needs inspectable mechanics without leaking locked-test row-level development signal. |
| Live model calls on validation250 | accepted | Use saved replays only for Phase 0 and schema reconstruction. | The reset is about mechanics and contracts; new calls can be introduced only after the contract is frozen and the question is predeclared. |
| Initial `ExtractedCandidate` schema | accepted | Use a source-near candidate member of a row-level `CandidateSet`; use kind-specific detail objects, including distinctive cluster details, unknown and no-reference candidates, one temporality field, binary certainty with fixed certainty reasons, provisional assertion status, no normalization/parsing, and no scorer labels. | This preserves high-fidelity candidate data while keeping selection, normalization, projection, and rendering separate; LLM extractor burden must be tested. |
| Temporarily frozen legacy components | accepted | Freeze legacy components from behavior changes; allow inspection and mapping only until the disposition ledger assigns final actions. | The reset needs stable source mechanics while component roles are rationalized. |
