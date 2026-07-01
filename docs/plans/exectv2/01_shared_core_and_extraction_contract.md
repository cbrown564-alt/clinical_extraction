> **Status: HISTORICAL** — design record only. See [`ACTIVE_ROADMAP.md`](../ACTIVE_ROADMAP.md) and [`recent_plan_rationalisation_2026-06-25.md`](../recent_plan_rationalisation_2026-06-25.md).

# Satellite 01 — Shared Core & ExECTv2 Extraction Contract

Parent: [[00_overarching_implementation_plan]] · Phase 1
Status: **COMPLETE** — 2026-06-09. All deliverables shipped; exit criteria met; 1057 tests green.

## Purpose

Define the one shared extraction contract every ExECTv2 architecture emits and
the scorer consumes, decide what is lifted into `core` (or a shared epilepsy
layer) vs. kept task-specific, and wire the Gan 2026 normalization model in for
reuse. This is the architectural spine; getting it right is what makes the three
pipelines cheap and the DRY claim true.

## 1. Package layout

```
src/clinical_extraction/
  core/
    scoring.py            # DONE — task-neutral PRF1
    pipeline.py           # reused: Pipeline, PipelineResult
    evidence.py           # reused: substring + repair
    validation.py         # reused: ValidationResult/Issue
    schemas.py            # reused: EvidenceSpan, FinalExtraction
  tasks/
    shared/epilepsy/      # NEW shared layer — cross-task, cross-dataset epilepsy logic
      normalization.py    #   count/range × period × anchor → rate (lifted from gan2026)
      seizure_free.py     #   seizure-free assertion detection (lifted/adapted)
      terms.py            #   seizure terminology, ILAE seizure types
    epilepsy_phenotyping/
      exectv2/
        data.py           # DONE — loader
        scoring.py        # DONE — label-based entity scoring
        contract/         # NEW — prediction schema + entity registry
          prediction.py   #   ExectPrediction = predicted ExectLetter + per-mention evidence/trace
          entities.py     #   entity + attribute registry (the 9 entities, attribute vocab)
          validate.py     #   schema validation gate over predictions
        deterministic/    # satellite 02
        llm/              # satellite 03
        hybrid/           # satellite 04
        runner.py         # satellite 05
        reports/          # satellite 05/07
```

**Decision: introduce `tasks/shared/epilepsy/`.** `architecture.md` allows a
shared layer below `core` for things that are epilepsy-general but not
clinical-extraction-general. Seizure-frequency normalization and seizure-free
detection are exactly that: reused by both Gan 2026 and ExECTv2, but not by a
hypothetical non-epilepsy task. `core` stays strictly task-neutral.

## 2. The extraction contract

Every architecture produces, per letter, a set of predicted entity mentions in
the **same `ExectLetter` shape the scorer already consumes**, enriched with the
transparency fields the thesis requires.

```python
# contract/prediction.py
class PredictedMention(BaseModel):
    entity: str                      # one of the 9 registered entities
    text: str                        # the phrase the model/rules selected
    attributes: Mapping[str, str]    # feature values (NumberOfSeizures, TimePeriod, ...)
    evidence: str                    # exact source substring supporting the mention
    evidence_span: EvidenceSpan | None
    rationale: str                   # why this mention/these features
    confidence: Literal["low","medium","high"] | None
    uncertainty_flags: tuple[str, ...]   # closed vocabulary (see satellite 07)
    component_owner: str             # which stage/rule produced it (attribution)

class PredictedLetter(BaseModel):
    letter_id: str
    mentions: tuple[PredictedMention, ...]
    diagnostics: Mapping[str, Any]
```

An adapter turns `PredictedLetter` → `ExectLetter` (drop transparency fields) so
`score_entity()` is unchanged. This keeps scoring stable while predictions carry
the full evidence trail (component-evidence-attribution contract,
`docs/design/component_evidence_attribution_architecture.md`).

## 3. Entity & attribute registry

`contract/entities.py` is the single source of truth for the nine entities and
their legal attributes, derived from the gold corpus (not hand-guessed):

- Birth History, Diagnosis, Epilepsy Cause, Investigations, Onset, Patient
  History, Prescription, **Seizure Frequency**, When Diagnosed.
- For each: the attribute keys observed in gold, their value vocab where closed
  (e.g. `TimeSince_or_TimeOfEvent ∈ {During, Since}`,
  `MRI_Results ∈ {Normal, Abnormal, ...}`), and which attributes are
  free/continuous (counts, dates).

**Build step**: a one-shot profiling script over `load_letters()` emits the
observed attribute schema per entity (we already did this for SeizureFrequency:
263 mentions, the full attribute set, `NumberOfSeizures="0"` ×92). Commit the
profile as `docs/research/exectv2_gold_schema_profile_<date>.md` so the registry
is auditable and annotation noise (stray `DiagCategory`/`Certainty` on a couple
of SF mentions) is documented, not silently inherited.

## 4. Schema validation gate

`contract/validate.py` runs over every `PredictedLetter` and returns a
`ValidationResult` (reused `core` type):

- entity ∈ registry
- attribute keys ∈ entity's legal set; closed-vocab values legal
- required-shape checks (e.g. a rate mention has either a count or a
  range, and a period)
- evidence present and (separately) evidence-is-substring check via
  `core/evidence.py`

Validity rate and repair rate are first-class reported metrics
(reliability_thesis §3.1). Repairs are limited to semantically-neutral fixes
(the existing evidence repair ladder); no clinical-fact invention.

**Closed-vocab policy (post-review).** Because the gate validates *predictions*,
physical-unit/binary/scale vocabs are widened to their full legal domain
(`Negation`, `*_Results`, `*_Performed`, `Certainty`, `AgeUnit`, `TimePeriod`),
not the values that happen to occur in the 200-letter gold — otherwise a
correct-but-unseen prediction would be marked invalid and validity-rate would
measure the gold's incidental value distribution. Semantic categoricals stay
observed-only. A drift guard (`tests/test_exectv2_contract.py`) re-derives the
schema from `load_letters()` and asserts entity/attribute sets match the
registry exactly while closed vocabs cover gold; the profile is regenerable via
`experiments/profile_exectv2_gold_schema.py`.

## 5. Normalization reuse (the transfer test)

The Gan 2026 normalizer maps selected facts to a comparable rate. ExECTv2's SF
attributes (`NumberOfSeizures`, `Lower/UpperNumberOfSeizures`, `TimePeriod`,
`NumberOfTimePeriods`, anchors, `FrequencyChange`) encode the **same** structure.

Plan:

1. Identify the task-neutral normalization core in
   `tasks/seizure_frequency/gan2026/contract/label_parser.py` and the
   normalization semantics doc (`gan2026_normalization_semantics.md`).
2. Lift the count/range × period → rate logic into
   `tasks/shared/epilepsy/normalization.py`, with Gan 2026 importing the lifted
   module and a test proving its outputs are byte-identical to before the lift
   (ADR-0013-style guard).
3. ExECTv2 provides a thin adapter: gold/predicted SF attributes →
   the shared normalizer's input. This adapter is the only SF-specific glue.

The success signal for the whole thesis: this lift is small and the adapter is
thin. If it is not, that is itself a finding about where the task-1 abstraction
was over-fit to Gan 2026 — document it.

## 6. Deliverables & tests

- `contract/prediction.py`, `contract/entities.py`, `contract/validate.py`
- `tasks/shared/epilepsy/{normalization,seizure_free,terms}.py` with Gan 2026
  re-pointed at the lifts + unchanged-behavior tests
- `exectv2_gold_schema_profile_<date>.md`
- Adapter `PredictedLetter → ExectLetter`; round-trip test
- Schema-validation tests incl. gold-as-prediction validates clean
- Reuse ledger in [[00_overarching_implementation_plan]] §5 updated

## 7. Exit criteria

- A trivial stub predictor emitting gold mentions as `PredictedLetter` passes
  schema validation and scores 1.0 via the adapter + `score_entity`.
- Gan 2026 full suite still green after the normalization/seizure-free lifts.
- Entity/attribute registry matches the committed gold profile exactly.
