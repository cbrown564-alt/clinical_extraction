# R9 compact source-policy review, second scored-term candidate

This is a **development audit** of the same 750 Gan 2026 synthetic dev750
first responses. It includes `row_ok=False`, uses the frozen compact v0.3
reference of 1,219 claims and the unchanged R9 DeepSeek V4.1 Flash prompt
`one_shot_frequency_v2_measurements_r9` revision
`compact_primary_finding_v03_candidate`. There are no model calls, format or
semantic repairs, reference edits, or test450 inspection. Invalid responses
contribute reference misses. The raw reference, raw responses, v2 and v3 scores,
and v1 scored-term candidate remain available. `score.json` records the
dataset, split, row policy, scorer, model/prompt metadata, replay/repair policy,
and hashes. Reproduce with
`.venv/bin/python scripts/benchmarks/score_compact_concepts_v02.py` using a
fresh output directory.

The source-selected [review comparison](../../../../../../runs/one_shot_frequency_v2_measurements_r9/dev750/concepts_v02_source_audit/source_review_comparison.jsonl)
holds 39 reference claims, source IDs and hashes, origin IDs, exact quotations,
paired R9 predictions, component agreement and decisions. These are mechanism
checks, not a representative sample. The
local scored reference, remaining review queue, and per-letter pairs are in
`runs/one_shot_frequency_v2_measurements_r9/dev750/concepts_v02_source_audit/`.

## Decisions supported by source review

The reference's `restriction` field often holds information that the compact
guide says should remain in evidence. The scorer should distinguish four cases:

1. **A population limit is scored.** No events *when sleep was adequate*
   (3356), no myoclonic jerks *on waking* (6131, 14187), no clusters
   *requiring emergency care* (13721), and no *clear-cut* events while warning
   features continue (9250) cannot become global absence claims. A rate
   stated *on workdays* (4116), *on the hot line* (3846), or only during
   *brief periods* (16574) cannot become a continuous unrestricted rate.
2. **A repeated qualifier is scored once.** `Morning` beside `morning
   myoclonic jerks` (2374), `during sleep` beside `events during sleep`
   (9103), and `on ambulatory EEG` beside `electrographic events` (9815)
   repeat the event population. The literal wording remains in the evidence.
3. **Incidental context is unscored.** `After a night shift` describes one
   last seizure (6029). `Off ASMs` and `drug-free remission` describe treatment
   state, not the event count (8938, 8949). The two convulsions in 3846
   occurred at work, but their observed count is not a workday denominator.
4. **Broad but distinct events need stable codes.** A convulsion and a
   convulsive event are the same broad phenotype. Jerks and staring spells
   are different populations in 2513. The note in 6180 explicitly calls
   `collapses with limb-jerking` convulsive events. An incidental `brief`
   remains optional (4026), and cluster word order is optional when the
   counted unit and measurement already express the cluster (12403, 17110).

The v2 dictionary encodes the narrow source-supported distinctions above.
Compared with v1, it rejects two previously credited whole claims: R9 omitted
the workplace condition on the 3846 rate and the waking limit on the 14187
absence. The other field changes do not change whole-claim matches. It also
maps broad convulsive wording and keeps jerks distinct from staring.

Separate R9 errors remain under either dictionary. It asserts an overall
seizure population for unclassified events (6094, 6319) and drops the explicit
focal preserved-to-impaired progression (467). The original 39-case audit
also labeled 15992 a model aggregation error. **Correction (24 September):**
seven is the owner-approved derived total of four December plus three January
awake events, and R9's prompt forbids arithmetic. Its omission is a
prompt/reference policy mismatch, as documented in the
[subsequent source check](../concepts_v03_policy_candidate/README.md#diary-arithmetic-correction).
The saved JSONL retains its original decision for reproducibility; this
correction supersedes that attribution.

| Replay | Matches | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Original literal v2 | 202 | 15.43% | 16.57% | 15.98% |
| Window-corrected v3 | 282 | 21.54% | 23.13% | 22.31% |
| Scored-term v1 candidate | 447 | 34.15% | 36.67% | 35.36% |
| Scored-term v2 candidate | 445 | 34.00% | 36.51% | 35.21% |

The same 1,062 source-aligned pairs remain. The 617 aligned near misses after
v2 include event disagreements in 307 pairs, window in 282, measurement value
in 174, and restriction in 92; components overlap. These are aggregate
diagnostics, not a count of adjudicated model errors. The two rejected matches
show why accepting every v1 gain would overstate performance.

## Decisions still needed before a new dev750 call

The v2 review queue flags **270 reference claims** (overlapping categories):
198 literal restrictions without a scored code, 73 named labels without a
standard type, and 19 combined populations with an unmapped component. The
remaining restrictions are mostly positive-event timing, triggers, treatment
context, cluster size restatements, or qualifiers already expressed in another
field. Six are on absence claims. These have not all received source review.

Three policy questions affect the endpoint and should be settled on dev750
sources before freezing a scorer:

- **Conditional qualitative claims:** `occasional` clusters only around
  missed meals or curtailed sleep (2023, 4592, 6321), and convulsions only
  *if* a cluster is prolonged (10996). The current finite dictionary does not
  consistently represent the condition. Decide which conditions define a
  separately scored population and how to encode them without an unlimited
  trigger vocabulary.
- **Broad event mixtures:** `loss of awareness or convulsions` (9215) and
  `prolonged or status episodes` (17146) contain a standard type plus an
  unclassified component. The v2 scorer conservatively retains their literal
  combined label. Decide whether a small broad-phenotype code set is enough
  or whether these mixtures stay literal and outside the primary score.
- **Source contradictions and observation scope:** the day-to-day eight-month
  absence and recent flight event in 6077 coexist in one note; 5092 says no
  *observed clinical* seizures. The scorer should not infer global absence.
  The source review records these as open cases rather than silently choosing
  one interpretation.

The compact v0.3 reference is unchanged. The v2 score is still **provisional**;
it must not replace the frozen paper result or justify a new full model run.
