# ExECT paper scoring is not our comparison

Date: 2026-08-24
Status: paper source. Not a new scorer and not a results table.

## The short answer

The 2024 ExECT annotation paper scores a mention-level, CUI-and-features
match designed so a GATE extractor could be checked automatically. This
project scores a four-family clinical-fact inventory. Those are different
objects. Rescoring our cells on the paper metric is not a worthwhile
comparison: we do not ask the model to extract certainty or negation, and
we do not treat every annotated attribute as part of the task.

## What the ExECT paper scores

Fonferko-Shadrach et al. (2024) validate against a gold built to look
like the original ExECT pipeline (Fonferko-Shadrach 2023, thesis 3.1).
The published overall is the unweighted mean of nine entity F1s, at
mention level and at letter level.

A mention is correct on the strict view when it has a non-empty UMLS CUI
and the full evaluated attribute bundle. Certainty is scored for
Diagnosis and Patient History. Negation is scored for Patient History
only. Phrase and CUI-only views exist, but the cited system number
(0.87 per item, 0.90 per letter) is the all-features mean across all
nine types, including sparse families and Patient History.

That metric answers: did the extractor emit the same coded mention the
annotators were told to write for GATE.

## How our scoring differs

Our cited ExECT score is 4-family micro F1
(`clinical_inventory_unit_keys`): diagnoses, seizure-frequency facts,
prescriptions, and investigations. Repeats of the same diagnosis or
frequency state in a letter are one fact. Prescription and investigation
occurrences stay separate after key filtering. CUI identity is not
required. Certainty and negation are not in the scored unit.

The four families are the clinically central follow-up facts with enough
gold support for a stable comparison. Birth history, cause, onset, and
when diagnosed are too sparse. Patient History was left out because it
mixes comorbidities, generic seizure mentions, and events whose boundary
with diagnosis and frequency was already uncertain in the annotation
work.

That measure answers: did the submitted inventory recover the important
facts.

## Why a paper-metric comparison is not worthwhile

The inventory extract prompt does not ask the model for certainty or
negation. Encode may later fill convention defaults. Scoring those
fields as if they were extracted clinical judgements measures work we
did not request.

ExECT is the outlier here. Later epilepsy-letter systems ask for the
facts that change cohort membership or outcome: epilepsy or seizure
type, current anti-seizure medicines, seizure frequency or control
(Xie et al. 2022, 2023; Fang et al. 2025; Holgate et al. 2025; Gan et
al. 2026). They do not treat mention-level certainty codes, negation
flags, and the rest of a GATE feature bundle as the headline object.

We followed that later literature: recover the important facts and the
attributes that define them (who, what drug or test, what rate), with
quoted evidence. We did not adopt ExECT's complete mention-and-feature
identity test as the method comparison.

The published views remain in the repo as a historical measurement
family. They are not a results column and should not be used to
reinterpret the five-cell grid.

## Claim boundary

Internal scoring rationale. Not a reproduction of the 2024 benchmark.
Not a claim that omitted ExECT fields are clinically meaningless.
Holdout remains aggregate-only.
