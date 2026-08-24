# ExECT encode-rule development on dev140

Date: 2026-08-22  
Status: implemented and verified on development data; not promoted to holdout  
Protocol: [exect encode-rule development protocol](exect_encode_rule_development_protocol_2026-08-21.md)  
Primary artifact: [`summary.json`](../../../experiments/exectv2_encode_rule_development_20260821/summary.json)

## Answer

The deterministic ExECT encode stack was substantially underdeveloped. The
frozen candidate adds seven independently switchable rules in four clinical
areas and raises exact clinical-fact micro-F1 on the saved Gemini
`exect_llm_only` `dev140` mentions from **0.8000 to 0.8570**. The saved Gemini
LLM encoder reaches **0.8176** on those same raw mentions and the same scorer.

The candidate changes 308 mentions and 49 letter/family key sets. Among the
changed sets, 42 improve and seven are score-neutral; none worsens. Twenty-four
previously non-exact letter/family outputs become exact, and no
comparator-exact output becomes non-exact. All changed mentions retain exact
source evidence.

| Arm | Clinical fact F1 | Diagnosis | Investigations | Prescription | SeizureFrequency |
| --- | ---: | ---: | ---: | ---: | ---: |
| Existing deterministic encode | 0.8000 | 0.6448 | 0.9438 | 0.9277 | 0.7712 |
| Saved Gemini LLM encode | 0.8176 | 0.6745 | 0.9438 | 0.9453 | 0.7799 |
| New deterministic encode | **0.8570** | **0.7608** | **0.9513** | **0.9576** | **0.8050** |

These are exact multiset micro-F1 values from
`clinical_headline_unit_keys`, computed per letter and family. No new model
call was made. `test60` was not loaded or inspected.

## What was missing

### 1. Diagnosis names and source-local specificity

Rule: `encoding.diagnosis_standard_name`

The prior stack mainly attached CUIs when the model phrase already matched a
known name. It did not consistently write the closed Diagnosis name already
stated by the mention. In isolation, the rule raises Diagnosis F1 from
**0.6448 to 0.7608**.

The accepted repairs include:

- abbreviations and incomplete heads: `TLE` → `temporal lobe epilepsy`,
  `complex partial` → `complex partial seizures`, `focal` in an explicit
  probable-focal diagnosis → `focal epilepsy`;
- old or variant names: `secondarily generalised seizures` → `secondary
  generalised seizures`, `focal dyscognitive seizures` → `dyscognitive
  seizures`;
- benchmark head altitude: `symptomatic structural epilepsy` → `symptomatic
  structural focal epilepsy`, and explicitly possible/probable generalised
  epilepsy → `generalised epilepsy`;
- harmless modifier cleanup in a compound fact: `with occasional secondary
  generalisation` → `with secondary generalisation` without deleting the
  simple-partial sibling fact.

The rule does not map a finding or cause to a syndrome. Focal cortical
dysplasia → focal epilepsy and hippocampal sclerosis → temporal lobe epilepsy
remain semantic revision operations. A single-event guard also prevents the
plural benchmark alias from rewriting source evidence that states one event.

### 2. Prescription regimen slots and dosage-form names

Rules:

- `encoding.prescription_local_slots`
- `encoding.prescription_formulation_name`
- `encoding.prescription_standard_name`

The old formatter trusted malformed model attributes even when one local
regimen stated an unambiguous dose and cadence. It also searched shared
evidence too broadly, so a rescue cue for one drug could overwrite scheduled
sibling drugs. The local-slot rule alone raises Prescription F1 from **0.9277
to 0.9526**; the cumulative Prescription result is **0.9576**.

Representative repairs:

- EA0012: `Zonisamide 150 mg BD` with model `DrugDose=1500` → 150 mg;
- EA0072 and EA0092: `Lamotrigine 50mg bd` with model `DrugDose=500` → 50 mg;
- EA0150: local `bd` remains twice daily for levetiracetam and lamotrigine even
  though their shared sentence says clobazam is for seizure clusters;
- `carbamazepine CR` and equivalent controlled/extended/modified/prolonged/
  sustained-release suffixes → base `carbamazepine` when the base drug is known.

The dose repair requires exactly one explicit dose/unit pair. Ranges and
multi-dose text remain unchanged. Local rescue tails override a scheduled token
inside the same phrase, so `Clobazam 10-20mg bd for seizure clusters` remains
as-required and does not turn the range endpoint into a point dose.

Standard-name rendering writes ordinary regimen text as the resolved generic
drug name but preserves rescue, future-plan, and weight-based wording because
downstream component diagnostics use those cues. This rendering is exact-score
neutral in isolation after the strict review, but it removes dependence on
regimen prose for ordinary drug names without erasing clinically relevant
context.

### 3. Seizure-frequency type, zero state, and lower bounds

Rules:

- `encoding.sf_local_evidence`
- `encoding.sf_standard_name`

The prior SF encoder normalized counts and periods but often left a generic or
non-standard event name, failed to use one unambiguous named type in the local
evidence, and could not represent explicit recurrence without an exact count.
The local-evidence rule alone raises SF F1 from **0.7712 to 0.7962**; the
cumulative result is **0.8050**.

Accepted behavior includes:

- generic `seizure`/`episode` → the one unambiguous multiword seizure type in
  that mention's evidence; ambiguous multi-type evidence is unchanged;
- `absence` → `typical absences` only when explicitly stated, even when a GTC
  is also mentioned;
- `tonic clonic` → `generalised tonic clonic seizures` and `episode` →
  `seizures` under the closed name list;
- zero-state text → `seizure free` only when the evidence explicitly says so
  and does not instead anchor a `last seizure`;
- `has had further ... seizures` with no count →
  `LowerNumberOfSeizures=1`, which records the source-supported lower bound
  without inventing a point count.

One-word ambiguous types such as bare `focal`, uncertain type phrases, remote
zero-state clauses, and evidence naming several distinct types are excluded.

### 4. Investigation result repair

Rule: `encoding.investigation_local_result`

The prior stack could preserve `Normal` even when the selected test mention
contained an explicit abnormal finding. The new rule raises Investigations F1
from **0.9438 to 0.9513** by making an already-selected test abnormal when its
own modality-local clause contains an unnegated abnormal result.

The modality and negation guards prevent three observed false readings:

- `no epileptiform correlate` is not abnormal;
- an MRI finding does not alter an EEG mention, or vice versa;
- `no acute pathology` is not an abnormal CT result.

## Ablation

| Rule alone | Overall F1 | Target-family F1 |
| --- | ---: | ---: |
| `encoding.diagnosis_standard_name` | 0.8403 | Diagnosis 0.7608 |
| `encoding.prescription_local_slots` | 0.8066 | Prescription 0.9526 |
| `encoding.prescription_formulation_name` | 0.8013 | Prescription 0.9327 |
| `encoding.prescription_standard_name` | 0.8000 | Prescription 0.9277 |
| `encoding.sf_local_evidence` | 0.8053 | SeizureFrequency 0.7962 |
| `encoding.sf_standard_name` | 0.8019 | SeizureFrequency 0.7799 |
| `encoding.investigation_local_result` | 0.8013 | Investigations 0.9513 |
| All seven | **0.8570** | — |

The cumulative result is not the sum of isolated deltas: name rendering,
attribute completion, and CUI projection can act on the same mention.

## No-call transfer audit

After freezing the rules on Gemini, the candidate was replayed on every saved
dev140 raw-output distribution available for `exect_llm_only` and
`exect_llm_pre_post`. It improves all nine distributions. No changed
letter/family set is worse and no comparator-exact set regresses.

| Saved raw distribution | Baseline | Candidate |
| --- | ---: | ---: |
| LLM-only DeepSeek | 0.8110 | 0.8582 |
| LLM-only Gemini | 0.8000 | 0.8570 |
| LLM-only GPT-5.6 Luna | 0.7932 | 0.8433 |
| LLM-only Grok | 0.8168 | 0.8670 |
| LLM-pre-post DeepSeek | 0.7985 | 0.8469 |
| LLM-pre-post Gemini | 0.8189 | 0.8629 |
| LLM-pre-post Gemma | 0.6689 | 0.7151 |
| LLM-pre-post GPT-5.6 Luna | 0.8108 | 0.8577 |
| LLM-pre-post Grok | 0.8151 | 0.8719 |

Eight sources parse all 140 rows. The saved Gemma file has four pre-existing
parse failures (EA0056, EA0082, EA0111, EA0176); both arms receive the same
empty parsed mentions for those rows. Its absolute score is therefore not
directly comparable to cleanly parsed sources, but its within-source rule delta
remains a like-for-like replay.

Machine results are in
[`transfer_summary.json`](../../../experiments/exectv2_encode_rule_development_20260821/transfer_summary.json)
and
[`transfer_changes.jsonl`](../../../experiments/exectv2_encode_rule_development_20260821/transfer_changes.jsonl).

## Exhaustive residual ownership

The frozen Gemini candidate leaves 214 exact error units: 155 false negatives
and 59 false positives across 143 non-exact letter/family pairs. Every unit was
inspected against the raw extracted mentions, exact evidence, candidate keys,
and gold keys.

| First owner | Residual units | Why encode must stop |
| --- | ---: | --- |
| Extract | 60 | The required fact or slot is absent from the saved raw mentions |
| Select/revision | 104 | Requires add, split, dedupe, temporal/ownership resolution, or a semantic decision |
| Scorer/gold convention | 50 | Multiplicity, fragment/altitude, scorer behavior, or source-gold conflict |
| Safe encode remaining | **0** | — |
| Unresolved | **0** | — |

The ledger is
[`residual_classifications.jsonl`](../../../experiments/exectv2_encode_rule_development_20260821/residual_classifications.jsonl),
with totals in
[`residual_classification_summary.json`](../../../experiments/exectv2_encode_rule_development_20260821/residual_classification_summary.json).

## Strict-review rejection

Transfer inspection exposed an overfit version of prescription standard-name
rendering: it standardized `Midazolam as per rescue plan` only when that row had
one rescue medicine, but preserved the same wording when rescue siblings were
present. The distinction depended on batch multiplicity, not the fact. It was
removed. The final rule always preserves rescue context. In the historical
pre-boundary replay this lowered the candidate from 0.8682 to 0.8674 and turned
EA0121 back into a documented scorer/convention residual; it removed a
non-portable score-specific exception.

## Scorer contract and claim boundary

The saved later-stage Gemini comparison previously reported 0.8545 using
`clinical_headline_scores`, including hierarchy-aware asymmetric Diagnosis
matching. That permissive scorer has been removed from every four-family result
and Diagnosis-headline path, and the historical 0.8545 value must not be cited
as a current result. The canonical reported scorer is exact per letter and per
family using `clinical_headline_unit_keys`; hierarchy and cross-family matching
remain in explicitly diagnostic reports only. The LLM encoder has a real
positive effect on shared raw rows,
but the aligned gain is 0.0176 F1, not the larger gap obtained by comparing
unlike scorers.

This is development evidence from inspected `dev140` rows. The transfer audit
tests portability across saved model distributions on the same development
split; it is not independent validation, clinical validation, or holdout
generalization. `test60` remains sealed.

The accepted rules are the rule-encode stop for the six-model roster
row on filtered extract (`exect_llm_extract_filtered`, protocol-time
`exect_llm_only`), then rule encode and rule select. They are not the
later-stage LLM encode ledger used by cited cell 4 (Gemini only, living
extract). All figures above use `clinical_headline_unit_keys`; they are
development evidence, not the paper's cited 4-family micro F1 five-cell
grid. Cited holdout select stops:
[cells 3–5](exect_gemini_inventory_cells_3_5_protocol_2026-08-23.md),
cell 2
[both-extract](exect_both_extract_on_inventory_protocol_2026-08-23.md).
`exect_llm_pre_post` is both-extract; `exect_llm_extract_filtered` is
the retired Compact ablation.

## Authority correction

After this result, Diagnosis qualifier overwrite was moved out of encode.
`focal epilepsy` plus a probable temporal modifier is now
`selection.diagnosis_specificity_hierarchy`: a portable select rewrite on the
stated epilepsy hierarchy, not an exact heading match and not same-fact
encode. The current 0.8570 encode result above excludes that remap. The
historical 0.8674 value included it and must not be cited as a pure encode stop.
Finding-to-syndrome maps were already out of encode.

SF generic-type retarget and the inferred `LowerNumberOfSeizures=1` from
`has had further … seizures` are also select:
`selection.sf_named_type_from_evidence` and
`selection.sf_explicit_recurrence_lower_bound`. Encode keeps only the explicit
`seizure free` closed name and the closed SF type list. The 0.8570 encode
figure above still includes those SF remaps until a fresh encode replay.
