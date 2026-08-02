# Decision 0047 canonical orchestrator parity

Date: 2026-08-01
Status: complete; clean-checkout reproduction passed

This is the verification owner for the decision-0047 canonical pipeline
orchestrator refactor. It records implementation parity, not new clinical or
model-performance evidence.

Machine artifacts:

- [full parity summary](../../experiments/canonical_orchestrator_parity_0047.json)
- [permitted-development replay](../../experiments/canonical_orchestrator_development_parity_0047.json)

## Result

All gates pass in both the working tree and a fresh checkout.

- The six canonical methods emit the stage order declared by their manifests.
- Gan rules-only, LLM-only, and LLM-with-rules each pass exact dev750
  compatibility checks. The two model methods replay saved GPT-5.6 Sol raw
  outputs and compare prediction, evidence, parse, repair, scoring, and row
  trace fields.
- ExECT rules-only passes exact all-nine dev140 adapter parity. ExECT LLM-only
  preserves the saved Sol four-family clinical facts, attributes, evidence,
  rationale, and confidence while making typed ownership metadata explicit.
  ExECT LLM-with-rules passes selected-policy dev140 assembly determinism and
  exact-evidence checks.
- The retained historical verifier reproduces all six reference cells.
- Four public aggregate-only test60/test450 artifacts contain no row
  identifiers, note text, raw output, predictions, or gold rows.
- All selected research, replay, and operational wrappers tested by the
  delegation suite call task-local canonical entry points. Private
  `_legacy_run_split` functions remain reachable only from the parity harness
  until the clean-checkout gate is accepted.
- Generated architecture documents match their manifests and callables.
- A fresh checkout of commit `46fec88a` passes 1,488 tests; Ruff passes; mypy
  passes 350 source files.

## Operational-policy disposition

Decision 0045 `default` / `default` is the sole active ExECT policy for research
and operational use. The pre-refactor operational path unconditionally enabled
`diagnosis_resolution_candidate=True`; it is classified as historical policy
drift rather than behavior this refactor must preserve.

On saved GPT-5.6 Sol dev140 outputs, the historical candidate changes 3 of 140
letters relative to the selected policy: two historical additions and one
historical removal. The artifact stores only a hash of the changed row IDs.
This is development-only policy characterization, not structural parity,
holdout evidence, or clinical validation.

## Commands

```powershell
.venv\Scripts\python.exe scripts\check_canonical_orchestrator_development_parity.py --check
.venv\Scripts\python.exe scripts\check_locked_aggregate_safety.py
.venv\Scripts\python.exe scripts\check_retained_evidence_manifest.py
.venv\Scripts\python.exe scripts\verify_reference_evidence.py
.venv\Scripts\python.exe scripts\build_architecture_docs.py --check
.venv\Scripts\python.exe scripts\check_canonical_orchestrator_parity.py --check
.venv\Scripts\python.exe -m pytest -q --basetemp .tmp\pytest-0047-full
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m mypy src
```

The pytest cache warning is environmental: the sandbox cannot write the
repository `.pytest_cache`. Tests use an explicit workspace-local base temp
directory; no test is skipped or failed.

## Clean-checkout result

The artifact checks and full repository checks pass from a fresh detached
checkout of commit `46fec88a`, using the repository environment and a writable
external pytest base-temporary directory. Retained Git LFS objects were
available. The verification harness also now canonicalizes text line endings,
including the supervisor source handoff manifest, so equivalent Windows
checkouts do not produce false hash drift.

No model calls or locked-row inspection were used. Exact textual evidence does
not establish semantic support or clinical validity.
