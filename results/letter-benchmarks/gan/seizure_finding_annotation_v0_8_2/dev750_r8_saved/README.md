# Claim representation review: saved R8 development letters

The [canonical annotation guide](../../../../../docs/research/gan2026/seizure_finding_annotation_v08.md)
owns the rules. This result records their application to Gan 2026 **synthetic
dev750** and the next questions for owner review. No model was called and no
locked-test letter was inspected. The saved R8 prompt and its 714 usable
projected inventories remain unchanged; 36 invalid inventories remain invalid.

## Coverage and result

The deterministic [all-letter audit](claim_representation_audit.json) processed
all 750 source IDs, checked each gold quotation against the letter, recorded
source-aligned gold/R8 differences, and wrote a local per-letter JSONL under
`runs/seizure_finding_annotation_v0_8_2/dev750_r8_saved/`. Two projected R8
quotations are not exact substrings, including letter 704. Flags identify
review candidates; they are **not** automatic errors. In particular, 62
letters have more than one seizure-free finding, 54 have a qualitative finding
alongside some numeric finding, and 87 gold cluster measurements have a label
that does not itself say `cluster`. Different subtypes and observation windows
explain some of these. The audit also aligns residual pairs by exact source
overlap: 163 aligned measurement mismatches, 54 subtype mismatches, 74 event
label mismatches, 46 timing mismatches and 38 seizure-status mismatches. These
counts overlap; they do not sum to the whole-finding errors.

Twenty-one source letters have **29 explicit, source-checked edits** in
[`revise_findings_v082.py`](../../../../../scripts/benchmarks/revise_findings_v082.py):
27 duplicate or unscored gold findings removed, one longest seizure-free gap
added, and one event label changed to `convulsive activity`. The local
`claim_adjudications.jsonl` retains the before/after finding, source ID/hash,
quotation and reason for each. The v0.8.1 reference is preserved.

| Saved R8 versus development gold | v0.8.1 | v0.8.2 |
| --- | ---: | ---: |
| Gold findings | 1,575 | 1,549 |
| Matched | 1,019 | 1,017 |
| Extra R8 findings | 422 | 424 |
| Missed gold findings | 556 | 532 |
| Precision | 70.7% | 70.6% |
| Recall | 64.7% | 65.7% |

This comparison measures a **changed target and scorer**, not a new model
result. Some removed gold findings had matched R8 findings, so they become
extras. The source text, raw model response and v0.8.1 score have not changed.
The v0.8.2 scorer ignores a co-stated `since` anchor only when both sides give
the same seizure-free duration; it still checks source overlap, event and
timing. Reproduce the source triage and corrected replay with:

```bash
.venv/bin/python scripts/benchmarks/audit_claim_representation_v082.py
.venv/bin/python scripts/benchmarks/revise_findings_v082.py
```

Use the workbench **Labels → v0.8.2 claim units** to inspect these letters.

## Batch A: what does a stated total subsume?

The approved rule is clear for letter [14146](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=14146): **three** generalised tonic-clonic seizures, including one after missed doses and two without a clear trigger, is one count. The most recent event date remains separate. Letter [5696](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=5696) likewise gives **three** events over four months, then divides them into two morning and one evening event. The intermittent description and the 2+1 breakdown are context. Letter [5528](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=5528) describes the same single short event in a summary and again with its last-month timing; the latter carries the scored count. These are corrected in v0.8.2.

The harder counterexample is [5995](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=5995): the diary contains generalised convulsions, one absence **cluster** with three brief events inside it, and zero months. Its old mixed-type exception remains. A joint total would require deciding whether the three brief events are in addition to the cluster and whether the zero months establish a separate seizure-free interval. **Question:** should mixed-type diaries retain only per-type counts plus the cluster measurement, with zero months as context, or should they also receive one overall event total when the arithmetic is unambiguous?

## Batch B: when do repeated absence statements add a new finding?

Letter [8355](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=8355) says no definite events for over a year, a diary with no events since June last year, and no clinically evident seizures for 12+ months. These describe one continuous interval; v0.8.2 retains one duration finding. [17003](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=17003) repeats no generalised convulsions for twelve months as one year in the history and impression; it too is one finding. [9190](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=9190) differs: focal impaired-awareness events or convulsions have not occurred since late February, while auras have not occurred since early April. Those event scopes and anchors differ, so both remain. Its later broad “no clinical seizures” summary and narrower unresponsiveness statement are still review candidates. **Question:** when a broad absence summary follows specific, differently dated subtype absences, should the broad summary ever be another scored finding, or only context for the specific claims?

## Batch C: what exactly is counted in a cluster?

[8969](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=8969) states weekly **clusters**, roughly six events each; the gold label preserves that unit while R8 says only `events`. [10481](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=10481) says four clusters this month, each with two to three focal impaired-awareness seizures; R8 says `clusters of focal impaired-awareness seizures`, preserving both unit and subtype. The existing gold splits a monthly-cluster finding from a four-cluster/size finding, despite their shared evidence. [11118](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=11118) says “Cluster days twice this month; typically six seizures in 24 h.” Gold separates two seizure days and six per cluster; R8 combines these in one cluster finding. [15442](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=15442) merely says a day with two tonic seizures, but the current gold uses a `cluster` measurement. **Question:** should `cluster` require the source to explicitly identify a cluster or recurring cluster cadence? For a cluster day, should the count of affected days and seizures per cluster be one structured finding or two distinct measurements?

## Batch D: possible events and clinical scope

[8805](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=8805) gives a dated brief confusion episode without collapse but does not establish that it was a seizure. The owner ruled this **unscored possible event**; v0.8.2 removes it. [4919](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=4919) explicitly calls a past aura-like episode “possible,” without convulsion or impaired awareness; it is also removed. [8355](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=8355) has R8’s occasional `head-fog` despite no loss of awareness, automatisms or confusion; gold correctly excludes it. In [743](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=743), R8 additionally calls waking disoriented on a sofa “possible unwitnessed events.” **Question:** is the intended boundary that an uncertain symptom remains unscored unless the clinician explicitly treats it as a seizure or links it to the patient's established seizure phenotype?

## Already settled label distinctions to preserve

- [3999](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=3999): R8 identifies the monthly measurement but loses the stated focal impaired-awareness subtype. Report measurement and subtype separately in the diagnostic.
- [5551](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=5551): “several episodes per day, predominantly focal” measures all episodes; the generalised weekly breakthroughs have a separate rate.
- [8805](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=8805): device absence is for `convulsive activity`; the rescue-measures log corroborates it.
- [704](http://localhost:3000/workbench?dataset=ganR8&version=v082&letter=704): an incidental `brief` adjective need not split an event label, but R8's non-exact concatenated quote still fails source evidence.

The remaining flagged letters are retained in the per-letter audit for the next
batch adjudication. This review establishes candidate groups and corrects the
clear cases; it does not claim clinical validation or that every flagged
semantic ambiguity has been resolved.
