# ExECTv2 SeizureFrequency LLM-First Event/State Schema Design

Date: 2026-06-18  
Status: design contract only; no new model calls.  
Scope: ExECTv2 dev workstream, SeizureFrequency route for Plan 11.

Coordination note: this design is intended to align with the family-routed
LLM-first comparison predeclaration. That predeclaration leaves exact SF field
names flexible, but assumes source-grounded event/state records with seizure
type, state, count/range, period/denominator, temporal anchor,
evidence/rationale; CUI excluded from model output; and unknown
suppression/defaulting reported as deterministic post-LLM behavior.

## Decision

SeizureFrequency should leave the broad all-family prompt and use a specialist
event/state schema. The model-owned headline is the source-grounded seizure
frequency event inventory: seizure phrase, state, operands, temporal anchor,
target/non-target status, evidence, and rationale. CUI, certainty, and final
ExECTv2 scorer attributes are deterministic projection layers after that
headline.

The primary LLM-first route is a raw-letter SF extractor with the same candidate
shape proven most useful in the specialist SF line:

1. Optional model-owned family checklist for recall pressure.
2. Model-owned `event_frames` for every possible SF, seizure-free, last-event,
   change, cluster, and non-target episode fact.
3. Model-owned scored `findings` copied from target event frames only.
4. Deterministic validation, format projection, CUI sidecar attachment, and
   scoring.

The candidate-span state adjudicator work remains valuable as hybrid mechanism
evidence, but deterministic span proposals or deterministic final selection
cannot support the primary LLM-first headline.

## Why A Separate SF Route Is Required

Plan 11 showed that the single all-entities LLM pass is the wrong shape for SF:
primary CUI-free SF recovery was `0.012`, while evidence for emitted essential
mentions was exact in `743/743` cases. The failure is not citation hygiene. It
is clinical event/state construction.

The specialist SF work points to the needed shape:

- The Qwen clinical-findings line made the model emit source-near findings, then
  restricted deterministic code to parsing, evidence checks, format projection,
  finite CUI lookup, and scoring.
- The later event-frame branch improved the substrate by making the model build
  an explicit event frame before producing scored findings.
- The state-adjudicator line improved dev140 SF by focusing the decision unit on
  active-rate, seizure-free, and unknown/change states, but it is hybrid when
  deterministic spans are supplied.
- The v0.6 state projection and v0.7 unknown suppression results are controlled
  deterministic sidecar evidence, not permission to hide semantic repair inside
  an LLM-first score.

Therefore the new Plan 11 SF route should evaluate whether a raw-letter model
can own the event/state inventory directly, with deterministic code only
transporting those emitted facts into scorer form.

## Model-Owned Clinical Contract

The model must own every prediction-bearing clinical decision:

| Decision | Model-owned field(s) | Notes |
| --- | --- | --- |
| Fact coverage | `event_frames` | Include target and non-target event candidates so misses can be diagnosed. |
| Target status | `target_status`, `include_as_finding` | Deterministic code may report this status, not use it as a hidden selector. |
| Seizure/event phrase | `seizure_phrase`, `finding_text`, `findings[].text` | Preserve source-near generic vs named wording. |
| State | `clinical_kind`, `frequency_statement_type`, event `statement_family` | Represents active rate, seizure-free, unknown/change, last event, dated count, cluster, or non-target. |
| Count/range | `count`, `count_low`, `count_high` | Preserve ranges and vague-count choices as model outputs. |
| Denominator/window | `period_count`, `period_low`, `period_high`, `period_unit` | For recurrence intervals and rates. |
| Temporal anchor | `time_relation`, `point_in_time`, `day`, `month`, `year`, `age_low`, `age_high`, `age_unit` | Includes current-vs-historical and since/during ownership. |
| Frequency change | `frequency_change` | Increased, decreased, frequent, infrequent, or same. |
| Evidence | `evidence` | Exact source substring is required for scored findings. |
| Explanation | `rationale`, `confidence` | Audit metadata only; not scored. |

The model must not emit or be scored on:

- `CUI`
- `CUIPhrase`
- `Certainty`
- `Negation`
- final ExECTv2 attribute dictionaries as the primary clinical headline

## Output JSON Shape

The JSON contract should follow the current specialist SF schema, with CUI and
certainty absent from the model output. The field names below are the current
implementation names, not a naming mandate for the family-routed comparison. A
candidate may use aliases if the same clinical semantics are present and the
adapter maps aliases without adding clinical facts.

```json
{
  "family_checklist": {
    "has_compact_section": true,
    "has_current_rate": true,
    "has_dated_count": false,
    "has_last_event": false,
    "has_zero_status": false,
    "has_frequency_change": false,
    "has_cluster": false,
    "has_non_target_episode": false,
    "checklist_rationale": "Short model-owned recall summary."
  },
  "event_frames": [
    {
      "event_id": "e1",
      "evidence": "Seizure type and frequency: seizures every 3 to 4 weeks",
      "seizure_phrase": "seizures",
      "target_status": "target_epileptic_seizure_frequency",
      "statement_family": "recurrence_interval",
      "source_role": "compact_section",
      "count": "1",
      "count_low": null,
      "count_high": null,
      "period_count": null,
      "period_low": "3",
      "period_high": "4",
      "period_unit": "week",
      "time_relation": null,
      "point_in_time": null,
      "day": null,
      "month": null,
      "year": null,
      "age_low": null,
      "age_high": null,
      "age_unit": null,
      "frequency_change": null,
      "finding_text": "seizures",
      "include_as_finding": true,
      "rationale": "The compact section gives a recurring seizure interval."
    }
  ],
  "findings": [
    {
      "text": "seizures",
      "evidence": "Seizure type and frequency: seizures every 3 to 4 weeks",
      "clinical_kind": "frequency_rate",
      "frequency_statement_type": "recurrence_interval",
      "source_role": "compact_section",
      "count": "1",
      "count_low": null,
      "count_high": null,
      "period_count": null,
      "period_low": "3",
      "period_high": "4",
      "period_unit": "week",
      "time_relation": null,
      "point_in_time": null,
      "day": null,
      "month": null,
      "year": null,
      "age_low": null,
      "age_high": null,
      "age_unit": null,
      "frequency_change": null,
      "confidence": "high",
      "rationale": "One seizure recurring every 3 to 4 weeks."
    }
  ]
}
```

Allowed enum values should remain close to the implemented specialist route:

- `clinical_kind`: `frequency_rate`, `seizure_free`, `frequency_change`,
  `dated_count`, `last_event`, `cluster_frequency`, `other_frequency`
- `frequency_statement_type` / `statement_family`:
  `header_count_since_anchor`, `calendar_count`,
  `calendar_occurrence_no_count`, `recurrence_interval`, `last_event_date`,
  `background_rate`, `seizure_free_duration`,
  `current_control_no_duration`, `current_zero_no_duration`, `change_only`,
  `cluster`, `non_target`, `other_frequency`
- `target_status`: `target_epileptic_seizure_frequency`,
  `non_target_episode`, `history_context_only`,
  `diagnosis_without_frequency`, `future_risk_or_driving`,
  `uncertain_not_scored`
- `source_role`: `compact_section`, `narrative`, `both`
- `time_relation`: `during`, `since`
- `period_unit` and `age_unit`: normalized unit words emitted by the model,
  then format-projected by deterministic code

## Evidence Contract

The evidence contract is stricter than the broad all-family prompt:

- Every scored `finding` must carry an exact source substring.
- Every target `event_frame` should carry evidence, even if a later parser drops
  the corresponding finding for schema reasons.
- Evidence validation is deterministic and non-semantic: exact substring,
  source-id validity, missing evidence, or invalid evidence.
- Deterministic code may not mine evidence to add missing count, denominator,
  state, seizure phrase, date, age, anchor, or frequency-change fields.
- Same-raw-output reparse may be used only for parser/schema attribution and
  must be labelled diagnostic when it changes transport success.
- Evidence validity must be reported by layer: raw event frames, scored
  findings, format-projected mentions, and CUI-projected companion mentions.

The headline cannot use a finding whose clinical content exists only because a
deterministic parser inferred it from evidence.

## Projection And Scoring Ownership

The layer ladder should be reported on the same raw model output:

| Layer | Owner | Allowed behavior | Claim role |
| --- | --- | --- | --- |
| `raw_event_frames` | LLM | Event/state inventory, target status, operands, evidence | Audit substrate for coverage and target selection. |
| `raw_findings` | LLM | Final model-owned target findings | Primary clinical headline before adapters. |
| `schema_valid_findings` | deterministic schema | Parse JSON, drop invalid records, preserve valid model values | Transport health. |
| `evidence_validated` | deterministic validator | Exact/source-near/missing evidence flags | Grounding gate. |
| `format_projected` | deterministic adapter | Normalize spelling/case/enums and map emitted fields to SF scorer attributes | Primary LLM-first scorer layer if no semantic facts are added. |
| `cui_projected` | deterministic benchmark-format adapter | Attach CUI/CUIPhrase from model-emitted phrase through finite SF lexicon | Companion benchmark-format score only. |
| `certainty_projected` | deterministic guideline adapter | No-op or sidecar for SF unless guideline scoring later requires it | Outside LLM-owned headline. |
| `post_llm_state_policy` | deterministic state policy | Optional unknown suppression/defaulting/state projection declared before evaluation | Separate deterministic sidecar; not primary LLM-first headline. |
| `benchmark_rendered` | deterministic adapter | Render accepted ExECTv2 mention dictionaries for legacy scorer | Reproduction/continuity layer. |

Adapter ownership rules:

- CUI projection is allowed only from the model-emitted `text` or
  `seizure_phrase`. If CUI lookup changes the selected seizure type, it is
  semantic repair and the row is no longer LLM-first.
- Certainty and negation remain deterministic guideline projection layers and
  should not be requested from the SF model. Current Plan 11 evidence indicates
  SF contributes no meaningful certainty-only burden.
- Normalization may canonicalize already emitted values such as `last clinic`
  to `LastClinic`, `week` to `Week`, named months to month numbers, and word
  numbers to scorer spelling.
- Normalization may not add an omitted temporal anchor, decide that a bare
  control statement is target, split or merge findings, suppress a finding for
  clinical reasons, or scan the note for missed facts.
- Unknown suppression, unknown defaulting, or deterministic state projection may
  be measured only as declared post-LLM behavior. If it changes a scored state
  or removes/adds a clinical finding, it must be reported as a deterministic
  sidecar or hybrid comparison, not as the model-owned SF headline.

## Essential SF Scoring Surface

The primary Plan 11 SF score should be CUI-free and certainty-free. It should
evaluate the model-owned clinical components:

| Unit | Component(s) |
| --- | --- |
| Phrase/state | seizure phrase plus `clinical_kind` / `frequency_statement_type` |
| Active-rate operands | count or count range, denominator period count/range/unit |
| Seizure-free / zero state | zero count, seizure-free duration, point-in-time anchor |
| Dated count / last event | time relation, day/month/year, age anchor, point in time |
| Unknown/change state | explicit qualitative change/frequency state |
| Duplicate facts | repeated compact/narrative facts remain separate when the source supports separate annotations |
| Evidence | exact selected evidence for every scored finding |

The companion legacy score may attach CUI and render benchmark attributes, but
the report must keep the primary CUI-free clinical score separate from the
CUI-projected companion score.

## Promotion Gates

No new full dev or benchmark-facing run should occur until the route satisfies
the smaller gates without deterministic semantic rescue.

| Stage | Gate | Required evidence |
| --- | --- | --- |
| Schema contract | Parser can accept the JSON shape; invalid records are reported, not repaired semantically | Unit tests for parser, projection boundaries, CUI sidecar separation, and evidence checks. |
| dev5 smoke | No systemic call/parse failure; evidence exactness high; examples inspectable | Report raw frames, raw findings, schema drops, evidence validity, and CUI-free vs CUI-projected score. |
| dev25 promotion | Strict SF component score materially above the broad prompt and no hidden deterministic selector | Item-level failure ledger by phrase discovery, state, operands, temporal anchor, duplicate recall, evidence, and projection. |
| dev140 decision | Completion gate for development claim | Primary CUI-free SF score, CUI companion score, evidence validity by layer, residual slices, and comparison to deterministic and hybrid SF candidates. |
| full 200 / benchmark-facing | Blocked until predeclared | Frozen protocol, no row-level tuning policy, architecture ownership statement, model/version, scorer policy, and projection sidecars declared before the run. |

Candidate promotion should also answer the component evidence contract:

- Which subproblems improved: coverage, target status, temporal selection,
  state boundary, rate denominator, cluster handling, generic-vs-named seizure
  phrase, and adapter rendering.
- Which component owned each improvement.
- Whether deterministic-correct rows regressed.
- Whether changed rows have exact evidence.
- Whether the result is `llm_first`, `llm_only`, `hybrid`, or diagnostic.

## Difference From The Failed Broad All-Family Prompt

| Broad all-family prompt | Specialist SF event/state route |
| --- | --- |
| One mixed schema for five families. | One SF schema whose decision unit is the seizure-frequency event/state. |
| Emits mention-like records that often omit SF operands. | Forces event frames with phrase, state, count/range, denominator, anchor, and target status. |
| Evidence was exact when emitted, but clinical-detail selection collapsed. | Treats exact evidence as necessary but not sufficient; scores event/state construction directly. |
| CUI absence made legacy benchmark raw score misleading. | CUI is an explicit sidecar companion score, never the model-owned headline. |
| Certainty/CUI burden was entangled with clinical recovery. | Certainty and CUI remain deterministic projection layers outside primary SF scoring. |
| One aggregate masked family-specific failure. | SF gets its own gates, slices, and residual taxonomy. |
| Another broad rerun would repeat a known failure. | Next evidence is a predeclared SF route with event/state output and layer attribution. |

## Integration Steps

1. Reuse `ClinicalFindingsRecord`, `EventFrameRecord`, and
   `ClinicalFindingRecord` as the schema base for the Plan 11 SF route.
2. Add a Plan 11 SF adapter that emits the layer ladder above and writes both
   CUI-free and CUI-projected score surfaces.
3. Add tests that prove deterministic code cannot convert non-target
   `event_frames` into scored findings, cannot infer missing operands from
   evidence, and cannot use CUI/certainty to change the clinical headline.
4. Add a report writer that separates phrase discovery, state selection,
   operand construction, temporal anchor, duplicate recall, evidence validity,
   CUI projection, and benchmark rendering.
5. Predeclare dev5/dev25/dev140 gates before any new model calls.

## Claim Language

Supported now:

> The failed Plan 11 broad all-family prompt should be replaced for
> SeizureFrequency by a specialist event/state route whose primary headline is
> CUI-free and certainty-free clinical event recovery.

Supported only after future gated runs:

> A raw-letter SF LLM-first event/state extractor recovers SeizureFrequency
> clinical details at development quality without deterministic semantic repair.

Not supported:

> The current broad all-family prompt can recover SeizureFrequency details.

Not supported:

> Deterministic state projection, unknown suppression, candidate spans, CUI
> lookup, or certainty projection are incidental to an LLM-first SF claim when
> they change the selected clinical fact or final state.
