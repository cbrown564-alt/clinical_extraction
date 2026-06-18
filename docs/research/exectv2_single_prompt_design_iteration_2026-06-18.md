# ExECTv2 Single Prompt Design Iteration

Date: 2026-06-18
Scope: four key families on ExECTv2 dev surfaces.
Status: design iteration and rejection of the single-call variant; not a
benchmark-complete claim.

## Question

Can the current family-specific ExECTv2 prompts be replaced by one prompt design
for Prescription, Diagnosis, SeizureFrequency, and Investigations, ideally one
that clears `0.8` for all key families?

The experiment tested the most aggressive form first: one call reads the letter
and emits all four families through a Gan-inspired structured event ledger.

## Experiment Unit

Hypothesis: a shared source-near event ledger with typed candidate evidence
lanes can reduce prompt accretion and recover the family-specific decision
structure inside one prompt.

Minimal change:

- bump the shared key-family structured extractor to
  `exectv2_hybrid_key_family_event_ledger`;
- add a per-letter `candidate_evidence_ledger`;
- add family lane hints for medication, diagnosis, seizure frequency, and
  investigations;
- add transparent render safety gates:
  - drop SeizureFrequency mentions with no frequency-state attribute;
  - drop duplicate modality-only Investigations when a result-bearing mention
    for the same modality exists.

Data surface: ExECTv2 dev25 for live iteration. Dev140 was not spent because the
candidate did not pass the dev25 decision gate.

Metric: key-family clinical-recovery headline F1, with call/parse/evidence gates.

## Results

| Candidate | Model | Rows | Rx | Dx | SF | Inv | Gate read |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| single structured v0.5 | gpt-4.1-mini | dev25 | 0.897 | 0.569 | 0.633 | 0.837 | prior best single prompt |
| v0.6 event ledger | gpt-4.1-mini | dev25 | 0.872 | 0.554 | 0.507 | 0.684 | reject |
| v0.7 tighter lanes | gpt-4.1-mini | dev25 | 0.883 | 0.600 | 0.523 | 0.780 | revise only |
| v0.7 + v0.8 gates replay | none | dev25 | 0.883 | 0.600 | 0.525 | 0.800 | useful gates, still reject |
| v0.8 live | gpt-4.1-mini | dev25 | 0.831 | 0.540 | 0.562 | 0.800 | reject; one parse failure |
| v0.8 live | gpt-4.1 | dev25 | 0.974 | 0.483 | 0.677 | 0.821 | stronger model helps Rx/Inv/SF, still reject |

Second-stage implementation: the selected family-conditioned template was
implemented as
`exectv2_hybrid_family_conditioned_event_ledger` in
`llm_family_conditioned_event_ledger.py`. This uses the same event schema for all
families and changes only a declarative `target_family` profile.

| Candidate | Model | Rows | Rx | Dx | SF | Inv | Gate read |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| family-conditioned v0.1 | gpt-4.1-mini | dev5 | 0.875 | 0.222 | 0.091 | 0.571 | reject; profiles too thin |
| family-conditioned v0.2 | gpt-4.1-mini | dev5 | 0.875 | 0.444 | 0.000 | 0.800 | reject; SF render altitude broke |
| family-conditioned v0.3 | gpt-4.1-mini | dev5 | 0.941 | 0.444 | 0.737 | 0.933 | scale to dev25 gate |
| family-conditioned v0.3 | gpt-4.1-mini | dev25 | 0.824 | 0.405 | 0.429 | 0.769 | reject direct-from-letter design |

Third-stage implementation: a candidate-backed family-conditioned adjudicator was
implemented as
`exectv2_hybrid_family_conditioned_candidate_adjudicator`. It uses one shared
prompt template and event schema, but receives the current strongest candidate
source for the target family. The no-call candidate-passthrough mode is the
candidate-bundle ceiling.

| Candidate | Model/mode | Rows | Rx | Dx | SF | Inv | Gate read |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| candidate-backed v0.1 passthrough | no call | dev140 | 0.817 | 0.658 | 0.782 | 0.872 | bundle ceiling matches current comparators |
| candidate-backed v0.1 live | gpt-4.1-mini | dev25 | 0.961 | 0.660 | 0.754 | 0.878 | close; SF below comparator |
| candidate-backed v0.2 live | gpt-4.1-mini | dev25 | 0.961 | 0.688 | 0.839 | 0.878 | clears current comparators on dev25 |
| candidate-backed v0.2 diagnosis reparse | no call | dev25 | n/a | 0.800 | n/a | n/a | format-only parser repair; diagnostic |
| candidate-backed v0.2 live | gpt-4.1-mini | dev140 | 0.831 | 0.654 | 0.675 | 0.892 | reject; SF transfer fails |
| candidate-backed v0.3 live | gpt-4.1-mini | dev25 | 0.961 | 0.838 | 0.875 | 0.878 | clears all four on dev25 |
| candidate-backed v0.3 live | gpt-4.1-mini | dev140 | 0.817 | 0.657 | 0.697 | 0.876 | reject full-object re-emission |
| candidate-ID actions v0.4 passthrough | no call | dev140 | 0.817 | 0.658 | 0.782 | 0.872 | ceiling; current comparator reproduced |
| candidate-ID actions v0.4 live | gpt-4.1-mini | dev25 | 0.949 | 0.833 | 0.936 | 0.857 | matches slice ceiling; Inv below global comparator because slice ceiling is 0.857 |
| candidate-ID actions v0.4 live | gpt-4.1-mini | dev140 | 0.817 | 0.658 | 0.782 | 0.872 | matches current per-family prompts |

## Interpretation

The single-call event ledger is operationally viable but not competitive. The
candidate improves source-near discipline and makes deterministic attribution
cleaner, but it reproduces the capacity problem documented in the final
synthesis: one prompt cannot simultaneously carry medication regimen policy,
investigation performed/result policy, seizure-frequency temporal state, and
diagnosis concept hierarchy well enough to match the current family-specific
selectors.

The stronger `openai/gpt-4.1` run is especially informative: Prescription and
Investigations clear on dev25, and SF improves, but Diagnosis falls. That points
away from model capacity alone and toward decision-unit conflict inside the
single call.

The family-conditioned direct extractor improved the shape of the design but
did not solve transfer. On dev25 it only matched the Prescription comparator
(`0.824` vs current `0.817`). Diagnosis (`0.405` vs `0.658`),
SeizureFrequency (`0.429` vs `0.782`), and Investigations (`0.769` vs `0.872`)
remain below the current family-specific prompts. The dev5 success of v0.3 was
a small-sample false positive.

The candidate-backed prompt identifies the next viable architecture. The
candidate bundle itself exactly reproduces the current dev140 readout, proving
that the single design can carry enough family-specific information when
candidate extraction is upstream. However, live prompts that re-emit complete
mention objects still degrade on dev140, especially SeizureFrequency. The
failure mode is copy drift, not missing evidence: the model drops, rewrites, or
adds mentions while packaging events.

v0.4 fixes that failure mode by changing the shared prompt output from final
mention objects to candidate-ID actions only:

```json
{
  "candidate_actions": [
    {
      "candidate_id": "best_sf:M0",
      "action": "keep",
      "reason_code": "supported",
      "rationale": "Evidence is present."
    }
  ]
}
```

Deterministic code then copies selected candidate mentions verbatim and applies
the existing evidence/schema gates. Missing actions default to keep, and reject
actions are honored only when code can verify a narrow condition such as
`evidence_not_substring` or `wrong_entity`. This preserves the prediction-bearing
candidate source while giving one family-conditioned prompt a transparent audit
role.

## Selected Single Prompt Design

The viable design is a single reusable prompt template, not a single all-family
call and not a raw direct extractor. The current comparator-equivalent design is
candidate-backed and candidate-ID based:

```text
clinical letter
  + target_family profile
  + candidate_evidence_ledger for that family
  + family candidate bundle
      - draft mentions when a stronger family-specific source exists
      - structured event candidates when a deterministic or prior LLM stage owns recall
      - source spans with lane hints when no draft mention exists
  + family lane guide
  -> source-near keep/reject/split/merge decisions over candidate IDs
  -> deterministic copy of selected candidate mentions for the target family
  -> deterministic evidence/schema gates
  -> finite projection and safety gates
```

The same template is used for every key family. Only the declarative
`target_family` profile and candidate-bundle schema change.

Required shared prompt sections:

- `task`: review one clinical letter for one target family.
- `candidate_evidence_ledger`: exact source spans with candidate IDs, lane
  hints, and anchor hints.
- `candidate_bundle`: optional upstream draft mentions/candidate groups with
  source attribution. This is required for Diagnosis and SeizureFrequency,
  where the direct extractor is not competitive.
- `decision_procedure`: classify lane and emit candidate-ID decisions. Do not
  ask the model to rewrite final mention objects when candidate text/attributes
  are already present.
- `family_profile`: declarative rules for the family.
- `output_schema`: `{candidate_actions: [...]}` with `candidate_id`, `action`,
  `reason_code`, and `rationale`. Final mention objects are copied
  deterministically from candidate IDs.
- `self_audit`: flag only verifiable rejects such as absent evidence or wrong
  entity; do not rewrite mention objects.

Family profiles:

| Family | Decision lanes |
| --- | --- |
| Prescription | current regimen, rescue regimen, historical medication, future/titration plan, reject |
| Investigations | performed with result, performed without result, not performed, planned/repeat, reject |
| SeizureFrequency | active rate, seizure-free anchor, qualitative change/unknown, prior event, unlabelled event, reject |
| Diagnosis | patient-level epilepsy syndrome, named epileptic seizure type, context-only epilepsy discussion, symptom/non-epileptic event, reject |

## Promotion Gate

This family-conditioned template has now matched the current family-specific
readout on dev25/dev140 where the relevant slice ceiling supports it:

| Family | Current comparator |
| --- | ---: |
| Prescription | 0.817 |
| Diagnosis | 0.658 |
| SeizureFrequency | 0.782 |
| Investigations | 0.872 |

The ideal `>0.8` all-family result remains unsupported on the current evidence.
Diagnosis in particular remains bounded by the existing ceiling analysis unless
a new evidence source changes the prediction-bearing candidate set.

## Decision

Reject both direct variants as final architectures:

- a single all-family call;
- a direct-from-letter family-conditioned extractor.
- a candidate-backed prompt that re-emits full mention objects.

Keep the Gan-inspired event ledger, typed lanes, and render safety gates, but
use them as one family-conditioned adjudicator template over family candidate
bundles. The adjudicator must output candidate-ID actions with deterministic
copy-through of selected candidates. Full-object re-emission is rejected after
dev140 transfer failure.

This v0.4 action design is the current single prompt design that achieves
equivalent dev140 performance to the current prompts per family. It does not
solve the aspirational `>0.8` target for Diagnosis or SeizureFrequency because
it deliberately preserves the current candidate ceilings (`Dx 0.658`,
`SF 0.782`), but it satisfies the comparator-equivalence gate without copy drift.
