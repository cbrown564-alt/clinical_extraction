# ExECT rules-only gated SeizureFrequency rewrite candidate

Date: 2026-08-27  
Status: candidate design; development only  
Protocol: [gated SF rewrite protocol](exect_rules_only_sf_gated_rewrite_protocol_2026-08-27.md)  
Context: [three-stage reconstruction](exect_rules_only_three_stage_reconstruction_2026-08-27.md), [test60 aggregate replay](exect_rules_only_three_stage_test60_aggregate_2026-08-27.md)  

## Problem statement

The rules-only three-stage reconstruction established that standalone rules can reach **0.9167** on `dev140` and **0.8018** on `test60`. However, the holdout replay revealed that SeizureFrequency remains the binding weakness of standalone rules (**0.6131** vs Gemini cell 3 **0.8082**).

Inspection of `dev140` SF residuals demonstrates that:
1. Recall on development is high (direct-vs-ledger gold unit recall is 0.867 → 0.879).
2. The dominant errors are **named-type identity misattributions** (e.g. rate attached to generic noun `seizures` when the clinical sentence describes `generalised tonic clonic seizures` or `focal motor seizures`).
3. Attempting to solve this by **promotion** of unassociated anchors from the ledger degrades precision, producing spurious `(type, unknown)` units (M3 dropped SF F1 to 0.845).

## Proposed candidate architecture: gated SF rewrite

The candidate specifies three targeted rules for SeizureFrequency identity reconciliation within the Select stage:

```
+-------------------------------------------------------------+
| 1. Recognise Ledger                                         |
|    - Direct rate-bearing mentions (emitted by pipeline)     |
|    - Deferred named-type anchors (kept in ledger)           |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| 1. Recognise Ledger                                         |
|    - Direct rate-bearing mentions (emitted by pipeline)     |
|    - Deferred named-type anchors (kept in ledger)           |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| 2. Encode Stage (Same-Fact Normalization)                   |
|    - Diagnosis standard names & categories                  |
|    - R2: Typo-Tolerant Lexicon Match (`encoding.sf_typo_lexicon_tolerance`) |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| 3. Select Stage (Gated SF Precision & Rewrites)             |
|    - R1: Local Named-Type Alignment (`selection.sf_local_named_type_alignment`) |
|    - R3: Multi-Clause Anchor Disambiguation (`selection.sf_multiclause_association`) |
|    - S2: SF Seizure-Free Positive-Count Drop                |
|    - W1: Weak Episode Drop                                  |
+-------------------------------------------------------------+
```

### Component R1: Local Named-Type Alignment (`selection.sf_local_named_type_alignment`)
- **Stage**: Select
- **Authority**: `rewrite` (concept remap / specificity altitude)
- **Mechanism**: Inspects selected SF mentions with generic CUI (`C0036572` / bare `seizure(s)`). If the sentence containing the evidence contains an unassociated named-type anchor (e.g. `generalised tonic clonic seizures`, `focal motor seizures`, `complex partial seizures`) and no other selected mention claims it, rewrites the mention's text and CUI attributes to the specific named type.
- **Guard**: Must not fire if the sentence already has an explicit rate mention for that named type.

### Component R2: Typographical Normalization (`encoding.sf_typo_lexicon_tolerance`)
- **Stage**: Encode
- **Authority**: `dialect` / `encode` (same-fact surface standard name)
- **Mechanism**: Normalizes surface spelling and near-miss typographical variants (e.g. `generlised tonic clonic` -> `generalised tonic clonic`) into canonical ontology entries without changing clinical finding or multiplicity.

### Component R3: Multi-Clause Association Disambiguation (`selection.sf_multiclause_association`)
- **Stage**: Select
- **Authority**: `reselect` (competing clause attribute ownership)
- **Mechanism**: In conjoined clauses with multiple seizure types and count attributes (e.g. *"three generalised tonic clonic seizures and more of his typical absences"*), ensures the integer count is assigned to the matching adjacent noun phrase.

## Gating criteria

To be accepted into a future three-stage candidate:
- Must pass Gate A on `dev140`: micro F1 ≥ 0.9167, SF F1 > 0.8640, zero comparator-exact regressions.
- Every rule must show isolated positive improvement and negative leave-one-out effect.
- Any holdout evaluation requires a separate, predeclared aggregate-only replay protocol.
