# Protocol: gated SeizureFrequency rewrite candidate on `dev140`

Date: 2026-08-27  
Status: predeclared before implementation  
Target: SeizureFrequency holdout gap (rules 0.6131 vs cell 3 0.8082)  
Context: [three-stage reconstruction](exect_rules_only_three_stage_reconstruction_2026-08-27.md), [test60 aggregate replay](exect_rules_only_three_stage_test60_aggregate_2026-08-27.md)  
Artifact target: `experiments/exect_rules_only_sf_gated_rewrite_20260827/summary.json`

## Primary question

Can a precision-gated SeizureFrequency rewrite rule—reconciling named-type identity on already-selected rate-bearing facts without unassociated anchor promotion—improve `dev140` SeizureFrequency inventory F1 above **0.8640** (overall **0.9167**) without comparator-exact regressions?

This addresses the binding holdout weakness identified in the 2026-08-27 three-stage replay: Diagnosis transferred (+0.0247 F1), but SeizureFrequency remained stalled at **0.6131** (recall **0.5676** vs cell 3 **0.7973**).

## Core research safeguard: rewrite vs promotion

The three-stage reconstruction established a crucial negative finding:

1. **Promotion (rejected, M3):** Unassociated named-type anchors in the ledger promoted via `sf_supported_state_promotion` produced spurious `(type, unknown)` false positives, dropping SF F1 from 0.856 to 0.845. Blanket anchor emission is even worse (0.7909).
2. **Rewrite (candidate under design):** Modifies the seizure-type identity (phrase, CUI, standard name) of an *already-selected* mention that carries verified frequency/date/seizure-free state attributes, matching it to the most specific named-type anchor in its local evidence window.

Under this protocol:
- **No mention is created from a rateless anchor alone.**
- **Every rewritten mention retains its existing frequency state and verbatim letter evidence.**
- **The rule action is strictly `rewrite`, never unverified `add`.**

## Data, split, and inspection boundaries

- **ExECTv2 `dev140` only** (140 development letters). Row, letter, and error inspection permitted.
- **`test60` is sealed and locked.** It is never loaded, never scored, and never inspected.
- **Cited five-cell rules row stays 0.8018** until a separate, predeclared aggregate-only replay is approved by document owners.

## Comparator (fixed)

The accepted three-stage configuration (`ACCEPTED_THREE_STAGE_CONFIG`):
- Recognise: D1 service context exclusion, D2 secondary-to retention, D3 focal onset alias.
- Encode: Diagnosis standard name and category.
- Select: D1 local specificity, D2 heading phenotype, keep source ancestor, S2 seizure-free positive count drop, W1 weak episode drop.
- Baseline `dev140` score: Overall F1 **0.9167**, SeizureFrequency F1 **0.8640** (143 TP, 23 FP, 22 FN).

## Candidate design specifications

The candidate introduces an explicit, gated SF identity reconciliation stage in Select:

### 1. Same-sentence named anchor binding
When a selected SF mention is anchored to a generic noun (`seizure`, `seizures`, `episodes`) or coarse category, but the same sentence contains an unassociated named-type anchor (`generalised tonic clonic seizures`, `focal motor seizures`, `typical absences`):
- Verify sentence-level span alignment.
- Verify that no sibling rate-bearing mention in the sentence already claims the named anchor.
- Rewrite the selected mention's text, CUI, and CUIPhrase to the specific named type.

### 2. Typographical and near-miss named surface normalization (Encode: `encoding.sf_typo_lexicon_tolerance`)
Spelling and typographical variants on clinical text (e.g. `generlised tonic clonic seizure` in EA0079) are mapped to canonical vocabulary in Encode (`dialect` / `encode` authority) before evaluation, standardizing the same finding without modifying clinical event selection.

### 3. Multi-clause anchor attribution (Select: `selection.sf_multiclause_association`)
In compound sentences describing multiple seizure types and rates (e.g. EA0184: *"three generalised tonic clonic seizures and more of his typical absences"*), resolve clause boundaries so counts attach to the nearest preceding/following named noun rather than falling to default ordering.

## Acceptance gates (all mandatory)

1. Aggregate `dev140` 4-family inventory micro F1 ≥ **0.9167**.
2. SeizureFrequency family F1 ≥ **0.8640**.
3. Zero comparator-exact letter/family regressions on `dev140`.
4. Zero added rateless mentions (no unassociated anchor promotion).
5. Isolated positive delta and negative leave-one-out effect on the combined candidate.
6. Verbatim evidence retention on 100% of rewritten mentions.

## Claim boundary

Development mechanism design only. No claim of holdout generalization or paper score revision is made.
