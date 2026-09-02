# Reconstruct ExECT rules-only for recognise / encode / select

Date: 2026-08-27
Status: follow-up brief; not a protocol and not a five-cell change
Owner: this file
For: the next session that rebuilds standalone rules, not a prompt tweak
Related: [inventory retune audit](exect_rules_only_inventory_retune_audit_2026-08-27.md),
[27 Aug patch](exect_rules_only_inventory_retune_2026-08-27.md),
[score definitions](../paper/score_definitions_2026-08-17.md),
[recognise then Select](../paper/exect_extract_vs_extract_and_select_2026-08-25.md),
[rule catalogue](../../paper/rule_catalogue.md)

## Why this exists

After the pipeline was split into recognise (formerly extract), encode,
and select, **LLM-led ExECT cells moved a lot**. The cited score
became 4-family inventory F1 without Diagnosis collapse. Cell 3
improved because the recognise prompt was allowed to be recall-first
and recorded Select rules were allowed to take precision.

Standalone rules were not rebuilt for that contract. They are still
mostly nine extractors plus identity dedupe: a Compact-era program
scored on a post-Compact measure. The 27 Aug patch proved the
direction on the margin. It is **not** the reconstruction.

The working hypothesis for the next session: if rules-only is
re-specified as the same three stages, with deliberate sequencing
(wide recognise, same-fact encode, precision Select), there is room
for a much larger lift than alias-and-collapse fixes — especially on
locked `test60`, where rules remain **0.7725** against Gemini cell 3
**0.8674**.

That lift is not in hand. Do not write it as a paper sentence.

## What we already know

### 1. The stage split changed what “good rules” means

The locked taxonomy (2026-08-21) is:

| Stage | Job |
| --- | --- |
| **Recognise** | Propose candidate facts and quoted spans. Prefer recall. Do not decide the final set. |
| **Encode** | Write an already-selected fact into the designed form (name, CUI, Rx slots, SF attributes). Same fact. |
| **Select** | Gate, drop, rewrite, reselect, or invent. This is where precision, parent/child inventory, and competing readings live. |

De-duplication belongs to Select, not to the scorer
([score definitions](../paper/score_definitions_2026-08-17.md)).

Cell 3 used that split. Gemini `test60`: recognise **0.8491** (P 0.836 /
R 0.863) → Select **0.8674** (P 0.873 / R 0.863). Recall held;
precision rose. Asking the model to recognise *and* filter in one
call lost holdout SeizureFrequency recall (**0.80 → 0.61**) and
finished at **0.8435**. Select in rules is doing real work. Bundling
it into the prompt does not replace it.

### 2. The scorer changed under the rules

Cited ExECT scoring is `clinical_inventory_unit_keys`: unique
Diagnosis concepts, **no most-specific collapse**. Compact/headline
(`clinical_headline_unit_keys`) is a retired ablation.

On `dev140` gold, Diagnosis 405 raw mentions → 289 collapsed headline
units vs **329** inventory units. The extra mass is mostly parents
that headline used to drop. Prescription and Investigations were
already per-occurrence on both scorers.

Rules-only was tuned when collapse rewarded “keep the most specific
phrase.” The Diagnosis recogniser still does that at match time:
longest-first `finditer` never emits nested `epilepsy` inside
`focal epilepsy`. Investigations used to keep one (modality, result)
pair. Mention identity still collapsed same-attribute repeats until
the 27 Aug patch.

The rule catalogue is explicit: **the rules-only row is a different
program**. Cell 3 encode/Select names (`encoding.*`, `selection.*`)
do not govern `exect_rules`.

### 3. The five-cell gap is a method comparison, not a Select ablation

Gemini `test60` select stops (4-family micro F1):

| Recognise / encode / select | F1 |
| --- | ---: |
| rules / rules / rules | **0.7725** |
| both / rules / rules | 0.8592 |
| LLM / rules / rules | **0.8674** |
| LLM / LLM / rules | 0.8636 |
| LLM / LLM / LLM | 0.853 |

On `dev140` the same rules row was already close to cell 3
(**0.8824** vs **0.8877**) *before* the 27 Aug patch. The unfair
number is holdout, and the family that falls over is
**SeizureFrequency** (rules headline-era holdout ~0.59 vs cell 3
**0.81**). Diagnosis on locked rules was not the weak family.

So “rules-only is worse because recall is low” is **directionally
true on holdout overall**, and **false as a Diagnosis-collapse
story**. Holdout headline P/R for rules was ~0.84 / **0.75** against
cell 3 **0.87 / 0.86**. Recall is the larger published gap. Frequency
is weak on both precision and recall.

### 4. Cell 3’s gains came from a ledger Select can still read

Inventory Select after LLM recognise can add a source ancestor,
drop a weak episode, restore a local heading, or refuse a one-call
filter. Those rules fire because the model ledger still contains the
wide set.

Replaying that same Select on the *old* rules ledger was almost a
no-op: two weak-episode drops, no keep-source. Parents and
rate-less states had already been discarded at extract.

### 5. Residual Diagnosis error is encode/Select-shaped, not occupancy-shaped

On `dev140` current-exact inventory (pre-patch):

- **70** Diagnosis FN, **57** FP.
- Only **2** FNs were “gold parent present, predicted child present.”
- **20** FNs were `focal epilepsy`; **36** FPs were generic `epilepsy`.

Letter mechanisms (development only): gold `focal-epilepsy` from
“epilepsy – probable focal”, “focal onset epilepsy”,
“localisation-related-epilepsy”, “symptomatic-structural-focal-epilepsy”.
Rules often emitted bare `epilepsy` or a more specific lobe name and
never wrote the inventory parent. Cell 3 already has
`encoding.diagnosis_standard_name` and
`selection.diagnosis_source_local_specificity` for that pattern.
Rules-only did not run them.

Occupancy recovery of nested spans found **zero** extra mentions.
The regex never produces the nested parent.

### 6. The 27 Aug patch is a first retrofit, not the rebuild

Accepted on `dev140` only; cited `test60` **0.7725** not replayed.

| Change | Inventory F1 |
| --- | ---: |
| Pre-patch rules | 0.8824 |
| Recall-first extract only (aliases + uncollapsed Inv) | 0.8853 |
| + Diagnosis encode and Diagnosis-only Select | **0.8949** |
| + rate-less SF anchors (then drop) | **0.7909** (rejected) |

Investigations **0.962 → 0.985** (FN 10 → 4). Diagnosis **0.803 →
0.826** (8 letter/family rescues, 0 harms vs that extract). Rx and
SF unchanged.

Applying the *full* inventory Select plus SF/Rx encode caused **four
exact-family regressions**. That is evidence the cell 3 rule pack
cannot be bolted onto today’s extractors. Sequencing has to be
redesigned, not copied.

## What we need to know

The next session should answer these before claiming a new rules
cell. `dev140` only until a frozen candidate exists. Do not inspect
`test60` rows.

1. **What is the rules-only recognise ledger supposed to contain?**
   Per family: which surfaces, hedges, heading aliases, repeated
   investigations, and SF states must remain visible for later
   stages? What is forbidden at recognise (negated, family-history,
   planned tests) vs deferred to Select?

2. **What is encode-only for a deterministic mention?**
   Which of the existing `encoding.*` rules are same-fact on a
   rules span, and which silently reselect (cause → syndrome,
   generic → specific)? The 27 Aug stack encoded Diagnosis only
   because SF/Rx encode harmed exact families.

3. **What is the Select sequence?**
   Order matters: keep-source after encode rewrite; weak-episode
   drop; investigation dedupe; SF state competition; Rx titration.
   Need an explicit order, each rule switchable, with
   leave-one-out and exact-family regression gates.

4. **Where is the holdout hole if we may not read letters?**
   Predeclare family P/R on a frozen `dev140` candidate, then one
   aggregate-only `test60` replay. The predicted failure mode is
   still SeizureFrequency. A development-only Diagnosis win will
   not close 0.77 vs 0.87.

5. **Can SF be recall-first without the 0.79 disaster?**
   Blind “keep every unassociated anchor” failed. Need a narrower
   recognise (section headings, named types, seizure-free with
   evidence) and a Select that drops unsupported states — the
   cell 3 SF pattern, not “emit all anchors.”

6. **Two rule programs, one vocabulary.**
   After reconstruction, can rules-only recognise / encode / select
   use the same authority names as the catalogue, or must they stay
   a separate namespace with a mapping? The paper already says they
   are different programs. A rebuild should decide whether that
   remains a feature or a debt.

7. **What must not change.**
   Scorer stays `clinical_inventory_unit_keys`. No holdout tuning.
   No mixing Compact/headline F1 with inventory F1. The cited
   five-cell rules number stays **0.7725** until a predeclared
   aggregate-only replay.

## What the early signs point at

**Architecture, not a missing alias list.** Cell 3 moved when
recognise stopped doing Select’s job and Select could still see
the candidates. Rules-only still decides keep/drop inside each
extractor. That is the mismatch.

**Diagnosis is an encode/Select problem on development.** Missed
`focal epilepsy` plus extra generic `epilepsy` is the same split
the LLM path already solved. The 27 Aug Diagnosis lift (+0.023 F1)
is the lower bound of that idea, not the ceiling.

**Investigations was a scorer-contract bug.** Per-occurrence gold
plus same-result collapse was free recall left on the table. That
class of bug may still exist in SF uniqueness and mention-identity
policies.

**SeizureFrequency is the reconstruction target for holdout.**
Development rules SF is already strong (~0.86). Locked rules SF
is the collapse. Rate-less emit-all is the wrong recall-first
move. A staged SF sub-pipeline already exists; it is precision-first
at associate-or-drop. That sub-pipeline needs the same three-stage
treatment as Diagnosis, not a new regex.

**Copying cell 3 Select wholesale will regress.** Measured. The
follow-up has to design a rules-only Select order against a
rules-only recognise ledger, then reuse cell 3 rules only where
the ledger shape matches.

**Development near-parity is not the story.** Rules **0.88–0.89** vs
cell 3 **0.89** on `dev140` can hide a 0.10 holdout gap. Any
rebuild that only chases development Diagnosis will look like
another 27 Aug patch.

## What the next session should do first

1. Read this brief, the [audit](exect_rules_only_inventory_retune_audit_2026-08-27.md),
   and the locked stage assignment — not the Compact rung numbers.
2. Write a reconstruction protocol with three independently
   stoppable programs (recognise registry, encode registry, Select
   sequence), inventory scoring, exact-family gates, no `test60`
   inspection.
3. Instrument a rules-only recognise ledger (pre-encode, pre-Select)
   so later stages have something to read — the missing object
   today.
4. Start with SeizureFrequency sequencing and Diagnosis Select
   order. Treat the 27 Aug Investigations fix as already landed.

Do not promote a new holdout number from that session unless the
protocol froze the candidate first.
