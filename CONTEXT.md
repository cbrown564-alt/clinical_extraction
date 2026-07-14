# Clinical Extraction glossary

This glossary covers the two retained research tracks. It defines project
language only; implementation and evidence ownership live in the documents
linked from [`docs/NAVIGATION.md`](docs/NAVIGATION.md).

## Tasks and evaluation surfaces

**Gan 2026** — the focused seizure-frequency task over synthetic clinical
letters. `validation750` is the development surface. `test450` is a locked,
author-uninspected holdout and may be cited or compared only in aggregate.

**ExECTv2** — broad epilepsy phenotyping over de-identified clinical letters.
`dev140` is row-inspectable development data. `full200` combines `dev140` with
held-out `test60`; it is a development-inclusive aggregate audit, not an
independent holdout, and `test60` rows are not a development surface.

**Purist** — Gan's strict accepted-label score and primary holdout metric.

**Pragmatic** — Gan's controlled lenient equivalence score; a secondary
readout, never a replacement for Purist.

**Clinical headline** — ExECT's de-duplicated clinical-fact recovery composite
over Diagnosis, SeizureFrequency, Prescription, and Investigations. It is not
the published strict phrase/CUI/full-attribute benchmark surface.

**Strict benchmark surface** — ExECT mention matching over normalized phrase,
CUI, and the complete non-ignored attribute bundle. It remains separate from
clinical-headline recovery.

## Architecture families

**Rules-only** — deterministic logic produces the prediction-bearing clinical
interpretation.

**LLM-only** — an LLM produces the prediction-bearing interpretation.
Deterministic code may perform format-preserving schema and label handling but
must not introduce or select the clinical fact.

**Hybrid** — deterministic and model-mediated components both contribute
semantic behavior; their ownership and effects must remain separately
attributable.

**Reference cell** — one retained rules-only, LLM-only, or hybrid configuration
for one task. The retained evidence matrix contains exactly six cells: three
families across Gan and ExECT.

**Operational control** — the bounded configuration used as the practical
reference, distinct from a ceiling comparator or negative comparator.

**Ceiling comparator** — a higher-cost configuration retained to bound quality,
not automatically the operational choice.

## Pipeline and evidence terms

**Extracted candidate** — a source-near fact proposed before clinical selection,
normalization, projection, verification, rendering, or scoring.

**Selected clinical fact** — the clinically relevant fact chosen from available
candidates, or an explicit abstention. It remains upstream of benchmark
projection and scoring.

**Normalization** — parsing and canonicalization that preserves the already
selected fact. A step that changes the selected event, state, category,
timeframe, denominator, or clinical meaning is a deterministic semantic rule,
not normalization.

**Projection** — conversion of a selected clinical fact into a task or
benchmark representation. Projection credit must remain distinct from clinical
recovery.

**Evidence verification** — checking that claimed support is valid against the
source. A score-inert replay does not prove this gate is unnecessary; rejection
and repair challenges are also required.

**Component attribution** — a record of which model or deterministic stage
created, changed, rejected, or rendered a fact.

**Replay** — evaluation from retained outputs without new model calls. A replay
demonstrates reproducibility of saved evidence, not fresh model behavior.

**Retained evidence** — the smallest hashed source, configuration, artifact,
and test set required by a surviving claim or reference cell. The manifest in
`docs/experiments/retained_evidence_manifest.json` owns the exact set.

## Rule portability

Deterministic semantic rules use one of five portability categories:

- `general`
- `clinical_epilepsy`
- `seizure_frequency`
- `gan2026_specific`
- `benchmark_format`

The category describes the rule's intended transfer boundary, not the module
where it happens to be implemented.

## Claim boundaries

**Implemented** means the behavior exists. **Verified** means named checks pass.
**Validated** means the stated evaluation supports the result. **Promoted**
means a canonical owner authorizes the paper or operational claim.

**Internal adjudication** is permitted development-side analysis of annotation
or scoring behavior. It is not independent clinical validation.

**Frozen architecture** means the exact prompt/program, model policy, scorer,
split, repair policy, configuration, and evidence closure are recorded before
new model calls.

For fuller plain-language definitions, see
[`docs/reference/plain_language_glossary.md`](docs/reference/plain_language_glossary.md).
