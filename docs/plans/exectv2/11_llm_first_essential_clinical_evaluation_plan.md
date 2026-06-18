# ExECTv2 LLM-First Essential Clinical Evaluation Plan

Date: 2026-06-18
Status: EXECUTED (analysis-only, no model calls) — see [Execution Results](#execution-results).
Readout: `docs/experiments/exectv2/key_entities/exectv2_llm_first_essential_evaluation_2026-06-18.md`;
machine JSON `experiments/exectv2_llm_first_essential_evaluation_dev140_20260618.json`;
code `reports/llm_first_essential_evaluation.py` + `runners/run_llm_first_essential_evaluation.py`.

## Purpose

This plan resets the ExECTv2 evaluation frame around the core research question:

> Can an LLM-first system identify the right clinical details for the important
> ExECTv2 families, with deterministic code limited to evidence validation,
> guideline projection, CUI attachment, benchmark formatting, and scoring?

The current benchmark-surface work has usefully exposed projection and
annotation-format gaps, but it has also blurred three different questions:

1. Did the model find the right clinical fact and supporting evidence?
2. Can deterministic adapters project guideline conventions such as certainty
   and CUI from that fact?
3. Can the final rendered output reproduce the exact original ExECTv2
   annotation bundle?

This plan separates those questions so the primary architecture can be judged on
LLM-owned clinical extraction rather than on benchmark-format artifacts.

## North Star

The target architecture is:

```text
one LLM call reads the letter
  -> emits source-grounded clinical facts/components
  -> deterministic code validates evidence
  -> deterministic code projects certainty, CUI, and benchmark formatting
  -> evaluation reports clinical component quality first,
     benchmark reproduction second
```

Deterministic-heavy systems remain important baselines. They should not be
treated as the end goal when they own candidate generation or clinical
selection.

## Scope

The essential clinical target families are:

| Family | LLM-owned clinical details | Deterministic-owned projection |
| --- | --- | --- |
| Prescription | Medication name, dose, dose unit, frequency, current/rescue/future/previous status, evidence | `DrugName` casing, CUI, benchmark phrase rendering |
| SeizureFrequency | Seizure type, active/seizure-free/unknown state, count/range, period/unit, temporal anchor, evidence | Accepted attribute grammar, CUI, scorer-specific state rendering |
| Diagnosis | Diagnosis concept, specificity, assertion evidence | Certainty/negation when guideline-derived, CUI |
| EpilepsyCause | Cause concept and causal evidence | Certainty/negation when guideline-derived, CUI |
| Investigations | Modality/test, performed/planned status, result, EEG type, evidence | CUI and benchmark result phrase |

BirthHistory, Onset, PatientHistory, and WhenDiagnosed remain in all-nine
benchmark reports, but they should not drive the primary LLM-first architecture
decision.

## Direct Hypotheses To Test

### Certainty

Certainty should be treated as a deterministic guideline-projection candidate,
not as a primary LLM extraction target, unless the audit proves otherwise.

Required checks:

- Translate the annotation guidelines into explicit certainty projection rules
  per entity where possible.
- Run those rules over gold or already-correct LLM evidence to estimate the
  projection ceiling.
- Compare raw LLM certainty, deterministic projected certainty, and
  certainty-dropped clinical scoring.
- Report certainty-only loss separately from clinical-detail loss.

Promotion rule:

If deterministic certainty projection is reliable enough on evidence-correct
rows, certainty is removed from the LLM burden and reported as an adapter layer.

### CUI

CUI should be deterministic. The model should not emit or reason about
identifiers.

Required checks:

- Build a CUI projection ledger with these buckets:
  - `one_to_one`: clinical phrase/component maps cleanly to one CUI.
  - `result_conditioned`: CUI depends on result, such as normal vs abnormal EEG.
  - `gold_inconsistent`: same clinical concept maps to conflicting CUIs.
  - `missing_mapping`: deterministic table lacks a projection.
- Strip model-supplied `CUI` and `CUIPhrase` before scoring any LLM-first run.
- Attach CUI only after clinical facts have been selected.
- Report CUI-only benchmark loss separately from clinical-detail loss.

Promotion rule:

No LLM-first claim may depend on model-supplied CUI. CUI is benchmark-format
projection unless it changes the selected clinical concept, in which case the
run is hybrid or diagnostic.

## Evaluation Contract

Every LLM-first candidate should report this layer ladder:

| Layer | Owner | Question |
| --- | --- | --- |
| `raw_llm_facts` | LLM | Did the model find the right clinical facts and evidence? |
| `evidence_validated` | deterministic validator | Are selected evidence spans exact or source-near enough? |
| `certainty_projected` | deterministic adapter | Can guideline certainty/negation be projected from selected evidence? |
| `cui_projected` | deterministic adapter | Can ontology identifiers be attached deterministically? |
| `benchmark_rendered` | deterministic adapter | Can the original ExECTv2 scorer key be reproduced? |

Ownership rule:

If deterministic code introduces or chooses a medication, seizure-frequency
state, diagnosis, cause, or investigation that the LLM did not extract, that
row is no longer `llm_first`. It should be reported as `hybrid` or
`rules_only`, depending on the prediction-bearing owner.

## Essential Clinical Scorer

Create an `essential_clinical_components` surface that evaluates the LLM-owned
details directly:

| Family | Primary score units |
| --- | --- |
| Prescription | Medication identity, dose, dose unit, frequency, regimen status |
| SeizureFrequency | Seizure type plus frequency state, numeric/range operands, denominator, temporal anchor |
| Diagnosis | Diagnosis concept/specificity plus asserted evidence |
| EpilepsyCause | Cause concept plus causal assertion evidence |
| Investigations | Modality/test plus performed/planned/result/type components |

The primary score should ignore CUI. Certainty should be excluded from the
primary LLM score unless the certainty audit shows it is a genuinely
model-owned clinical interpretation rather than a guideline projection.

## Candidate Architectures To Re-evaluate

Replay existing artifacts under the new framework before running new model
calls:

| Candidate | Role |
| --- | --- |
| Deterministic all-9 | `rules_only` baseline and projection machinery |
| Single structured key-family prompt | closest current `llm_first` candidate |
| Family-specific verifier/adjudicator runs | `hybrid` or specialist comparator |
| Candidate-ID action prompt | candidate-backed `hybrid` comparator, not LLM-first |
| Best-of benchmark-overall run | benchmark-reproduction comparator only |

This replay should answer whether the existing single structured prompt already
extracts the right essential details after certainty/CUI/formatting are removed
from the LLM burden.

## New Single-Call LLM-First Candidate

If replay does not answer the question, build one new single-call candidate with
a compact structured schema:

```text
{
  medications: [
    {
      name,
      dose,
      dose_unit,
      frequency,
      regimen_status,
      evidence
    }
  ],
  seizure_frequency_events: [
    {
      seizure_type,
      state,
      count_low,
      count_high,
      period,
      period_unit,
      temporal_anchor,
      evidence
    }
  ],
  diagnoses: [
    {
      concept,
      specificity,
      assertion_evidence,
      evidence
    }
  ],
  epilepsy_causes: [
    {
      cause_concept,
      causal_evidence,
      evidence
    }
  ],
  investigations: [
    {
      modality,
      performed_status,
      result,
      eeg_type,
      evidence
    }
  ]
}
```

The schema should not ask for CUI. Certainty should stay outside the
model-owned headline and be reported through the deterministic guideline-rule
projection audit.

## Experiment Ladder

Use the standard development ladder:

| Stage | Purpose | Promotion condition |
| --- | --- | --- |
| `dev25` | Schema, evidence, and catastrophic-error smoke | zero systemic parse/schema failure; interpretable evidence |
| `dev50` | Early clinical signal | no unresolved output-contract failure; useful residual taxonomy |
| `dev140` | Primary development comparison | component scores, evidence gates, projection ledgers, baseline comparison |
| full 200 | Frozen benchmark-comparable audit only | explicit authorization and predeclared locked protocol |

Do not use dev25 target-clearing results as architecture promotion evidence.
The previous ExECTv2 loop showed dev25 can be over-optimistic.

## Required Reports

### 1. Essential Clinical Scorer Specification

Defines the component keys, ignored projection fields, evidence policy, and
per-family scoring units.

### 2. Certainty Projection Audit

Answers:

- Which certainty/negation decisions are guideline-mechanical?
- What score is achieved by deterministic projection over gold or evidence-correct rows?
- How much apparent benchmark loss is certainty-only?

### 3. CUI Projection Audit

Answers:

- Which mappings are one-to-one, result-conditioned, inconsistent, or missing?
- How much benchmark loss is CUI-only?
- Does any CUI mapping require clinical selection beyond the LLM-provided fact?

### 4. LLM-First Single-Call Report

Answers:

- Does one LLM call recover the essential clinical details?
- Which families clear the clinical target?
- Which errors are candidate misses versus wrong detail selection versus evidence failures?

### 5. Baseline And Hybrid Comparator Report

Compares:

- LLM-first single-call candidate.
- Deterministic baseline.
- Current hybrid verifier/adjudicator candidates.

The report must state ownership: `rules_only`, `llm_first`, or `hybrid`.

### 6. Benchmark Projection Gap Ledger

Separates:

- clinical-detail miss;
- evidence miss;
- certainty/negation projection miss;
- CUI projection miss;
- phrase/rendering benchmark-format miss.

## Success Criterion

The refocused investigation succeeds when it can answer, without ambiguity:

> Does an LLM-first structured extractor recover medication details, seizure
> frequency details, diagnoses, epilepsy causes, and investigations at a level
> comparable to the original benchmark's clinical intent, once certainty, CUI,
> and benchmark formatting are handled as deterministic projection layers?

If yes, the next task is to harden the projection adapters and write the frozen
benchmark-rendering protocol.

If no, the next task is not another benchmark-surface tweak. It is an
error-led redesign of the LLM-first clinical schema or prompting strategy for
the failing families.

## Claim Language

Supported after this plan is executed:

> The primary LLM-first evaluation measures clinical-detail recovery before
> deterministic certainty, CUI, and benchmark-format projection.

Supported only if shown by replay or new runs:

> A single-call LLM-first extractor recovers the essential ExECTv2 clinical
> details at benchmark-comparable clinical quality.

Not supported without layer-specific evidence:

> A high benchmark-rendered score proves the LLM found the right clinical facts.

Not supported:

> Deterministic candidate generation is incidental implementation detail in an
> LLM-first architecture.

## Immediate Next Steps

1. Implement or document the essential clinical component scorer.
2. Produce the certainty projection audit.
3. Produce the CUI projection audit.
4. Replay existing single structured, deterministic, and hybrid artifacts under
   the new ownership-aware layer ladder.
5. Decide whether a new single-call LLM-first run is necessary after replay.

## Execution Results

Executed 2026-06-18, analysis-only, no model calls. All five immediate next
steps are done by replaying existing artifacts over one canonical `dev` (140
letter) gold:

- `rules_only` = generated deterministic all-9 (`run_all9_on_letters`).
- `llm_first` = single all-entities LLM pass
  (`experiments/exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.jsonl`,
  filtered to dev).
- `hybrid` = candidate-set + verify
  (`experiments/exectv2_hybrid_all_entities_dev140_gpt41mini_20260617.jsonl`).

New code (no edits to established scorers):
`reports/llm_first_essential_evaluation.py` (artifact loader, ownership ladder,
certainty audit, CUI 4-bucket audit, per-architecture assembly) and
`runners/run_llm_first_essential_evaluation.py` (driver + six-section readout),
with `tests/test_exectv2_llm_first_essential_evaluation.py`.

### Findings against the two direct hypotheses

**Certainty is now audited as a deterministic guideline-rule projection layer.**
Certainty-only benchmark loss is **+0.003 F1 (4 TP)** measured on CUI-projected
predictions, so the observed residual is certainty/negation rather than missing
CUI. The completed audit applies ExECT v9 List 2 certainty triggers, default
affirmed negation, and the PatientHistory febrile-negation exception over gold
rows. Projection coverage is complete for guideline-owned fields; certainty
accuracy is Diagnosis `0.81`, EpilepsyCause `0.95`, Onset `0.94`,
PatientHistory `0.82`, WhenDiagnosed `0.91`, and BirthHistory `1.00`.
Negation accuracy is `0.99`–`1.00`. This supports keeping certainty outside the
primary LLM-owned headline while preserving it as a benchmark-format adapter.

**CUI is benchmark-format projection, with finite-lexicon limits exposed.** The
single LLM pass emits no CUI, so its raw benchmark F1 is 0.000; deterministic
projection recovers it to 0.101 versus the 0.115 CUI-free semantic surface
(residual 0.014). In-sample projection over gold (CUI stripped then re-attached)
reaches coverage 0.75 and **correctness 0.944**, with 365 `missing_mapping`
mentions across 184 concepts concentrated in the long tail. No LLM-first claim
depends on model-supplied CUI, and missing mappings are now reported explicitly
rather than hidden inside one-to-one/gold-inconsistent concept counts.

### Essential clinical-recovery headline (primary CUI-free)

| Architecture | Ownership | Recovery F1 |
| --- | --- | ---: |
| deterministic_all9 | `rules_only` | 0.604 |
| hybrid_all_entities | `hybrid` | 0.550 |
| llm_only_all_entities (single pass) | `llm_first` | 0.422 |

The corrected primary headline aggregates only the five essential families
(Prescription, SeizureFrequency, Diagnosis, EpilepsyCause, Investigations),
strips CUI from gold and predictions before scoring, and uses concept-only
Diagnosis/EpilepsyCause recovery so `Certainty`/`Negation` do not drive the
LLM-owned score. BirthHistory, Onset, PatientHistory, and WhenDiagnosed remain
diagnostic/all-nine context only.

The single all-entities pass matches or beats rules on Prescription concept
recovery, Investigations, and Diagnosis concept identity, but **collapses on
SeizureFrequency (0.012)** and EpilepsyCause (0.000). The SF collapse is genuine,
not just a CUI scoring artifact: the single pass does not emit the structured
count attributes that define SF state.

> Scorer note: the SeizureFrequency state key uses CUI as the seizure-type
> identity when present, and all gold SF mentions carry one. The primary
> essential headline is therefore computed on a CUI-free copy of gold and
> predictions; a separate CUI-projected companion score is reported for continuity
> with the legacy scorer (`rules_only` 0.613, `hybrid` 0.566, `llm_first` 0.422).

Evidence validation is now included in the readout. The single all-entities
artifact carries exact source-substring evidence for 743/743 emitted essential
mentions, so the current failure is clinical-detail selection/coverage rather
than evidence citation absence. The coarse error taxonomy reports 563
candidate misses, 362 wrong-detail selections, and 0 evidence failures; these
categories are diagnostic and can overlap.

### Step 5 decision

A *new* single-call run is **not** the next step. The single all-entities pass is
already shown to be the wrong shape for SeizureFrequency and the low-frequency
atomic entities, so a fresh general single call would repeat the known failure.
The error-led redesign the plan calls for is: keep the single LLM pass for the
families it already recovers (Prescription, Investigations, Diagnosis concept),
and route SeizureFrequency to the structured event/state schema the specialist
SF candidates already use. Certainty and CUI stay outside the primary LLM-owned
headline and are now reported as deterministic projection layers with their own
audit limitations.
