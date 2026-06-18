# Gan 2026 ExtractedCandidate Schema Mapping Smoke

Date: 2026-06-05

Status: validation250 saved-artifact schema smoke. This is not a score report,
benchmark claim, or locked-test analysis.

## Question

Can saved validation250 artifacts be mapped into the proposed
`ExtractedCandidate` and `CandidateSet` shape?

## Source Artifacts

All inputs are validation-row-level saved artifacts allowed by the Phase 0
manifest.

| Artifact role | Source artifact | Rows checked |
| --- | --- | ---: |
| deterministic candidate events | `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_gpt41mini_v02_live_2026-06-01.jsonl` | 250 |
| LLM structured event list | `experiments/gan2026_hybrid_structured_events_validation250_qwen36_35b_max5000_overnight_2026-06-01.jsonl` | 250 |
| LLM selected fact with operands | `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 250 |
| LLM sparse selected state | `experiments/gan2026_simplified_schema_a2_validation250_2026-06-03.jsonl` | 250 |

## Aggregate Result

| Source | Rows with candidate-like source | Candidate-like records | Main result |
| --- | ---: | ---: | --- |
| deterministic candidates | 250 | 397 | Maps best; cluster details need extra decomposition. |
| LLM structured events | 167 | 325 | Conceptually closest LLM source; 83 rows have raw-output-only parse failures. |
| LLM selected fact | 250 | 250 | Useful selected-fact evidence, but not a candidate set. |
| LLM sparse selected state | 248 | 248 | Useful selected-state evidence, but not a candidate set; some source phrases missing from structured operands. |

## Kind Coverage

| Source | frequency_rate | cluster_frequency | seizure_free | last_event_only | unknown_frequency | no_reference |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| deterministic candidates | 271 | 13 | 79 | 0 | 7 | 27 |
| LLM structured events | 178 | 37 | 65 | 20 | 24 | 1 |
| LLM selected fact | 184 | 25 | 34 | 1 | 2 | 4 |
| LLM sparse selected state | 194 | 11 | 38 | 0 | 3 | 2 |

## Mapping Findings

1. Deterministic candidate events are the cleanest first mapping target.

They already have stable event ids, kind, evidence, start/end spans, rule
metadata, and source-near match groups. Their old `denominator` naming should
map to the new `time_period` language.

Example source:

```json
{
  "event_id": "event_1",
  "kind": "frequency_rate",
  "evidence": "four per day",
  "match_groups": {
    "count": "four",
    "unit": "day"
  },
  "raw_value": "4 per day",
  "rule_id": "rate.direct_count_per_period"
}
```

Target shape:

```json
{
  "candidate_kind": "frequency_rate",
  "frequency": {
    "count": "four",
    "count_range": null,
    "time_period": "day",
    "time_period_range": null,
    "source_phrase": "four per day"
  }
}
```

2. Cluster candidates are viable but require explicit detail extraction.

The new `cluster_details` object is better than the legacy label string, but the
old artifacts often pack cluster information into `raw_value` or rule-specific
match groups.

Example source:

```json
{
  "kind": "cluster_frequency",
  "evidence": "Over the past fortnight she describes a run of brief generalised events, with three short episodes occurring on separate days",
  "match_groups": {
    "per_cluster": "three",
    "period": "fortnight"
  },
  "raw_value": "1 cluster per 2 week, 3 per cluster"
}
```

Target shape:

```json
{
  "candidate_kind": "cluster_frequency",
  "cluster_details": {
    "cluster_frequency": "1 cluster per 2 week",
    "events_per_cluster": "3",
    "cluster_count": "1",
    "cluster_period": "2 week"
  }
}
```

3. LLM structured events are the best LLM candidate-source ancestor, but not yet
reliable as-is.

They include multiple events per row and cover `last_event_only`, but 83 of 250
rows have no parsed `structured_record` in the checked artifact. Those rows
would require dialect/schema repair before they can contribute to a candidate
set.

Example `last_event_only` source:

```json
{
  "kind": "last_event_only",
  "evidence": "last event taking place on site in the loading area",
  "raw_value": "on site in the loading area",
  "temporality": "recent"
}
```

4. Selected-fact and selected-state artifacts should not be used as primary
candidate extraction sources.

They contain one selected object per row, not a broad candidate set. They are
useful for Phase 3 Select review and for seeding examples, but treating them as
Extract output would repeat the same architecture problem: extraction and
selection collapse together.

5. The proposed certainty and assertion fields are mappable, with small
translation rules.

Legacy assertion values such as `historical`, `hypothetical`, `unknown`, and
`present` need mapping to the accepted set:

- `present` -> `asserted`
- `historical` -> `asserted` with `temporality = historical`
- `hypothetical` -> `conditional` or `uncertain`, depending on evidence
- `unknown` -> `uncertain`

Legacy `future` temporality appeared rarely and should map to `unclear` unless
the candidate is excluded from current-frequency extraction.

## Decision Implications

- Keep kind-specific detail objects. The saved artifacts can support them, and
  they expose cluster and boundary cases more faithfully than a single generic
  detail object.
- Start implementation with deterministic candidate mapping. It gives full
  validation250 coverage and stable source ids.
- Use LLM structured-events artifacts only after a replay/dialect-repair pass
  turns raw-output-only rows into valid event records.
- Do not map selected-state artifacts into `CandidateSet` except as diagnostic
  sidecars or Phase 3 selection evidence.
- Add a Phase 1 test that specifically measures whether LLM extractors populate
  the correct detail object for `frequency_rate`, `cluster_frequency`,
  `seizure_free`, `last_event_only`, `unknown_frequency`, and `no_reference`.
- For LLM candidate extraction, keep detail fields source-near. The LLM should
  find the clinical candidate statement and broad kind; deterministic
  normalization should expand counts, ranges, intervals, durations, and canonical
  operands.

## Schema Pressure Points

- `cluster_details` needs deterministic helper logic to decompose legacy
  `raw_value` strings and rule-specific match groups.
- `certainty_reason` will be sparse in older deterministic artifacts and should
  default to null when `certainty = certain`.
- The schema should preserve source-near strings even when old artifacts expose
  numeric operands, because normalization remains a later stage.
- A fresh 15-row GPT-4.1-mini schema probe initially showed good candidate/kind
  extraction but brittle parsed operands, duplicate repeated values, and
  exact-copy issues around special characters. After moving parsed operands out
  of the LLM contract, repairing neutral copy artifacts deterministically, and
  filtering trigger-only cluster drafts, the v5 source-near probe completed with
  15/15 candidate sets and no parse, evidence, source-phrase, or detail-object
  failures.
