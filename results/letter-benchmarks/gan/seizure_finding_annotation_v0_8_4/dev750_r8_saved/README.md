# Cluster units and explicit seizure link: saved R8 development replay

This is an additive reference and scorer revision over the [v0.8.3 saved-R8
comparison](../../seizure_finding_annotation_v0_8_3/dev750_r8_saved/README.md)
for Gan 2026 **synthetic dev750**. All 750 development letters were rechecked;
the same 714 saved R8 inventories are usable. The 36 invalid inventories, raw
R8 output, prior references and locked split are unchanged. No model was called.

`scripts/benchmarks/revise_findings_v084.py` is the repeatable producer. Its
local adjudication record under
`runs/seizure_finding_annotation_v0_8_4/dev750_r8_saved/` contains **22
source-backed edits across 18 letters**, each with source ID/hash, evidence,
reason and before/after values. The versioned `finding_v084_v1` scorer treats
`cluster.occurred_at` as unscored context; cluster count, size, cadence, event
label, timing, evidence overlap and applicable observation period still matter.
The [annotation guide](../../../../../docs/research/gan2026/seizure_finding_annotation_v08.md)
owns the intended rules.

| Saved R8 versus development gold | v0.8.3 | v0.8.4 |
| --- | ---: | ---: |
| Gold findings | 1,530 | 1,524 |
| Matched | 994 | 994 |
| Extra R8 findings | 447 | 447 |
| Missed gold findings | 536 | 530 |
| Precision | 69.0% | 69.0% |
| Recall | 65.0% | 65.2% |

The six fewer missed findings come from changing the reference inventory,
including three pairs of split cluster-day/size findings, one duplicate cluster
restatement, one unlinked uncertain spell and one ten-day absence. **No R8
prediction improved.** Some letters gain and others lose whole-finding matches
because the event label now names the cluster unit; the net matched count is
unchanged. The workbench view is
`http://localhost:3000/workbench?dataset=ganR8&version=v084`.

## Source examples

- [16645](http://localhost:3000/workbench?dataset=ganR8&version=v084&letter=16645)
  has one August cluster of three seizures. [16757](http://localhost:3000/workbench?dataset=ganR8&version=v084&letter=16757)
  has one April run of six within half an hour. The occurrence date is retained
  for review and omitted from cluster scoring. [16772](http://localhost:3000/workbench?dataset=ganR8&version=v084&letter=16772)
  literally says “a run of one seizure”; it retains one cluster containing one
  seizure, rather than inferring events absent from the source.
- [11109](http://localhost:3000/workbench?dataset=ganR8&version=v084&letter=11109),
  [11118](http://localhost:3000/workbench?dataset=ganR8&version=v084&letter=11118)
  and [11131](http://localhost:3000/workbench?dataset=ganR8&version=v084&letter=11131)
  each now have one cluster finding with count two, their stated seizures per
  cluster day, and `this month` as the observation period. The separate weekly
  isolated-event rate in 11109 remains. [3827](http://localhost:3000/workbench?dataset=ganR8&version=v084&letter=3827)
  retains distinct historical cluster size and current cluster-day count.
- [6738](http://localhost:3000/workbench?dataset=ganR8&version=v084&letter=6738)
  drops the six-to-eight-week rate of “blank moments”: concern for reduced
  awareness does not explicitly link them to seizures. The named possible
  absences in [3528](http://localhost:3000/workbench?dataset=ganR8&version=v084&letter=3528)
  and established focal auras in [8144](http://localhost:3000/workbench?dataset=ganR8&version=v084&letter=8144)
  remain in scope.
- [15513](http://localhost:3000/workbench?dataset=ganR8&version=v084&letter=15513)
  drops “none since” a seizure ten days earlier under the owner-selected
  two-week minimum. Its last-seizure and two-events-that-day findings remain.
- [11197](http://localhost:3000/workbench?dataset=ganR8&version=v084&letter=11197)
  retains one structured travel-cluster finding from the narrative and removes
  its repeated header claim.

The within-cluster span question remains open. For example, 16757 retains
`within half an hour` in `period`, and the current scorer still compares it.
This differs from the observed cluster count's window (`this month` in 11118),
which identifies what was counted. No broad within-cluster period change is
claimed here.
