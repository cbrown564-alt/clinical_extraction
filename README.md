# Clinical Extraction

Python pipelines that combine deterministic rules and language models to turn
clinical notes into structured data.

The repository supports loading data, extracting clinical facts, normalizing
values, validating evidence, scoring predictions, and analysing errors. It is
also the research code for a paper about which pipeline component improves a
clinical result and where each method fails.

Repository cleanup, engineering repair, pipeline fixation, and clean-checkout
verification are complete. The active work fills the remaining paper evidence
gaps. Gan 2026 holdout evidence remains locked. See
[project status](PROJECT_STATUS.md) for current results and limits.

## Current work

The repository contains two tasks:

- **Gan 2026** extracts one current seizure-frequency label from each letter.
  Its 450-row test split is locked; only saved aggregate results may be used.
- **ExECTv2** extracts diagnosis, seizure frequency, prescriptions, and
  investigations from de-identified letters. Its 140-row development split
  remains available for research.

The main scores are Gan Purist accuracy and ExECT de-duplicated clinical fact
recovery (`clinical_headline`). The ExECT score is an internal research metric,
not the published strict benchmark. Paper-derived normalized-phrase, CUI, and
full-attribute views are also available for explicit benchmark comparison.

Current state, as of 2026-07-15:

- The retained evidence index selects six no-call reference runs. The five
  largest replay files are content-addressed Git LFS objects.
- All 1,209 tests, Ruff, and mypy pass. CI runs all three checks. A separate
  Python 3.11 checkout reproduced the hashes, split restrictions, and six runs.
- Retained evidence index v3 records the source commit and exact dependency,
  prompt, scorer, split, repair, model, runbook, and CI versions.
- The Markdown manuscript and IEEE source use only selected evidence. The
  compiled three-page PDF has been visually checked.
- The Gan efficiency audit records a 15/450 Purist gain for V12 at three cold
  model passes per note rather than one; unmatched cost and latency claims were
  rejected because the old runs lack telemetry.
- The ExECT rules-only no-call dev140 replay reports macro item F1 of 0.5687 for
  normalized phrase, 0.7144 for CUI, and 0.6020 for all features. This is a
  development metric result, not reproduction of the original ExECT system.
- The historical ExECT `v08` and three-model rows do not meet the final
  model-led family boundary: Prescription was deterministic-only and Seizure
  Frequency included an independent extractor union. Decision 0040 now has
  durable corrected configurations and a verified aggregate-only replay with
  `state_profile`, attribution, evidence, schema, and regression records.
  Nonzero deterministic regressions keep the historical rows unpromoted.
- A frozen aggregate-only test60 replay found model-reported confidence
  uninformative for routing review across the three historical model outputs;
  no confidence-based review policy was adopted.
- One bounded Prescription study and one separate Diagnosis-guard study both
  improved dev140 aggregates but failed their predeclared mechanism gates. No
  further rule iteration is planned. A frozen joint replay composes those
  implemented components without interaction and is now the disclosed fallback:
  172 rescues, 3 regressions, and 153/160 current-policy rescues retained,
  compared with 161, 9, and 143/160 for the previous fallback.
- A no-call GPT-4.1-mini ablation found that the one-call Diagnosis
  architecture lowers final Diagnosis F1 from 0.8727 to 0.8542, with 3 rescues
  and 11 regressions. The same study exposed a first-140 versus manifest-dev140
  runner defect. Affected runs were stopped, and resume validation now prevents
  their partial artifacts from being reused. Decision 0041 accepts this
  quality tradeoff and selects one structured call per letter.
- The fixed hosted ExECT panel is complete on dev140 and aggregate-only test60.
  Test60 clinical-headline F1 is 0.7572 for GPT-4.1-mini, 0.7950 for GPT-5.6
  Luna, 0.8047 for GPT-5.6 Sol, and 0.7881 for thinking DeepSeek V4 Flash.
  Next work is the local Qwen 3.6:35B and Gemma 4 26B conditions and evidence
  freeze.

Use the [short reading paths](docs/THREAD_MAP.md) to find the relevant files.

## Method names

Current commands use three plain names:

- `rules`: deterministic rules produce the clinical interpretation;
- `llm`: the model produces the clinical interpretation;
- `llm_with_rules`: the model extracts or selects facts and deterministic code
  can normalize, select, or repair them.

Older long identifiers and version codes remain in saved filenames because
replay hashes and research provenance depend on them. The
[naming guide](docs/reference/plain_language_glossary.md) maps those identifiers
to their plain descriptions.

## Design principles

- Keep task boundaries clear enough to support more datasets later.
- Prefer small modules that expose where a failure occurred.
- Separate extraction from final clinical selection.
- Keep label normalization compatible with the author-provided scorer.
- Store evidence spans and rationale with final labels.
- Use tested scripts and selected saved outputs for reproducible analysis.
- Treat deterministic rules as named, testable components.
- Separate general clinical rules from seizure-frequency, dataset-specific,
  and benchmark-format rules.

## Repository layout

```text
src/clinical_extraction/
  core/                         Shared pipeline, schema, evidence, and validation code.
  tasks/seizure_frequency/
    gan2026/                    Gan loader, labels, scoring, pipeline, and analysis.
docs/
  design/                       Current software and data decisions.
  decisions/                    Reasons for active behavior.
  experiments/                  Human-readable selected evidence.
  plans/                        Ordered work.
  research/                     Thesis, manuscript, annotation source, and cleanup record.
  runbooks/                     Repeatable procedures.
experiments/                    Selected machine-readable outputs and run records.
tests/                          Data, scoring, and behavior checks.
```

## Start here

- [Project status](PROJECT_STATUS.md)
- [Active roadmap](docs/plans/ACTIVE_ROADMAP.md)
- [Documentation navigation](docs/NAVIGATION.md)
- [Retained evidence index](docs/experiments/retained_evidence_manifest.md)
- [Regeneration instructions](docs/REGENERATION.md)

## Setup

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
```

macOS or Linux:

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
```

Use the repository environment for all Python commands. For local Ollama runs,
start with one row, then five, then 25. Record the model route and API base in
the run metadata.
