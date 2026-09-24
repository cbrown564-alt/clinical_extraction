# R9 scored-concept development audit

This is an **exploratory dev750 rescore**, not an accepted paper endpoint or a
holdout result. It reuses the 750 first responses, the 1,219 compact v0.3
reference claims, exact evidence, and the v3 window rule. No model call,
response repair, reference edit, or test450 inspection occurred. The prompt is
`one_shot_frequency_v2_measurements_r9`, revision
`compact_primary_finding_v03_candidate`; the model is DeepSeek V4.1 Flash.
The row policy includes all 750 Gan 2026 synthetic development letters,
including `row_ok=False`; invalid responses contribute misses. The scorer is
`finding_compact_concepts_v01`, the dictionary is `compact_scored_terms_v01`,
and `score.json` holds source, prediction, code, and projection hashes. Reproduce
with `.venv/bin/python scripts/benchmarks/score_compact_concepts_v01.py` in a
fresh output directory. Local scored reference claims, flagged claims, and
per-letter pairs are under
`runs/one_shot_frequency_v2_measurements_r9/dev750/concepts_v01_final_candidate/`.

## Scored terms

The raw reference and response retain literal event labels and restrictions.
The separate projection scores declared event scope, a finite list of explicit
seizure types, and restrictions that change the counted or observed population.
It does not infer a type from a diagnosis elsewhere in the note. The dictionary
includes focal preserved/impaired/progression, focal-to-bilateral tonic-clonic,
generalised tonic-clonic, unclassified tonic-clonic, absence, myoclonic,
myoclonic absence, tonic, atonic/drop, spasm, aura and status. An untyped
`brief nocturnal episode` remains an untyped event; **brief** is unscored while
the sleep population is scored. Combined populations that cannot be fully
represented by the dictionary retain their literal label until review.

The scored restriction examples include sleep versus awake, observed by a
device, corroborated by a diary, witnessed or recognised events,
electrographic-only events, and a longest seizure-free gap. Timing or triggers
that merely describe an already counted event stay in evidence. The rule is
deliberately narrow and its flagged cases require source adjudication.

## What the saved responses show

| Scorer on the same responses | Matches | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Frozen literal v2 | 202 | 15.43% | 16.57% | 15.98% |
| Window-corrected v3 | 282 | 21.54% | 23.13% | 22.31% |
| Scored-concept candidate | 447 | 34.15% | 36.67% | 35.36% |

The candidate gains 165 matches in 147 letters versus v3, with no letter
losing a match. This is a scorer change, **not** a model improvement. The 1,062
source-aligned pairs remain unchanged. Among the 615 source-aligned near
misses, disagreements include event 307, window 282, measurement value 174,
phase 77, restriction 76, counted unit 61, status 43 and measurement kind 25;
these overlap. Whole-claim matching still requires agreement on every scored
component and overlapping exact source evidence.

## Source checks and failure attribution

These source IDs are selected mechanism checks, not a prevalence sample.

| Cause | Source IDs | Source-backed finding |
| --- | --- | --- |
| Model error | 6094, 6319 | R9 turns an unclassified event population into `overall seizures`; 6094 also adds a last-event claim not explicitly stated as such. The scope mismatch remains scored. |
| Model error | 467, 8805, 15992 | R9 broadens a focal progression to generic focal onset; omits diary corroboration of the device-observed absence; and splits a seven-event daytime total into four and three instead of stating the total. These remain misses. |
| Reference policy inconsistency | 2374, 6029, 9103, 9815 | `morning` duplicates the named myoclonic population; `after a night shift` describes the last event's trigger rather than its denominator; `during sleep` and `on ambulatory EEG` duplicate the event population already named in the label. The projection scores the population once. The frozen reference is untouched. |
| Optional literal wording | 4026, 12403, 17110 | `brief absence episode` and `absence episode` share the absence type; `clusters of drop attacks` and `drop attacks` share the drop type and cluster counted unit; `clusters of absence seizures` and `absence seizure clusters` share the absence type and cluster measurement. |
| Material qualifier retained | 2609, 9215 | Night and daytime populations remain distinct even when the restriction repeats the event label. A reported-or-recognised absence does not become a global seizure-free claim. |
| Still requires adjudication | 3846, 8949 | A hot-line kitchen rate may be conditional on that workplace exposure; a combined focal population needs its component types preserved. Neither example justifies a blanket restriction or label relaxation. |

The projection flags **340 reference claims** for follow-up: 230 have a
nonempty literal restriction with no scored code, 118 are named populations
without a standard type, and 23 are combined populations the dictionary cannot
fully map (categories overlap). Many ignored restrictions appear to be triggers
or incidental time descriptions, but this has not been established for all 230.
The 35.36% candidate F1 must not replace the frozen paper comparison until
those cases are source-adjudicated and the scored dictionary is frozen.
