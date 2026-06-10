# Satellite 05 — Experiment Harness & Loops

Parent: [[00_overarching_implementation_plan]] · Phases 2–6 (cross-cutting)
Status: planning. Dev-split only until the Phase 7 audit.

## Purpose

Provide the one runner, registry, and reporting surface all three ExECTv2
architectures share, and the disciplined loop for running experiments and
feeding results back into the pipelines. Reuse the Gan 2026 machinery; do not
reinvent it.

## 1. Unified runner

One `ExectPipelineRunner` mirroring `Gan2026PipelineRunner`, parameterized by an
`ExectArchitecture` literal:

```
"rules"             | "llm_only_single_pass" | "llm_only_per_entity"
"hybrid"            | "hybrid_structured_events"
```

- `run(letter) -> PipelineResult[PredictedLetter]`
- `run_split(split, architecture, model=...) -> artifact rows`
- One shared artifact contract across architectures (the
  asymmetry-handling lesson from Gan 2026: if one family exposes extra stages,
  document the asymmetry in the report rather than hiding it).
- `ARCHITECTURE_FAMILY` mapping for correct grouping in reports.
- An `entities` parameter so SF-only (Phase 2–5) and all-9 (Phase 6) runs use the
  same runner.

## 2. Splits

ExECTv2 ships no split; the benchmark used all 200. We define our own (mirror
`docs/design/gan2026_split_protocol.md`):

- A seeded manifest `data/ExECTv2 (2025)/splits/exectv2_split_v1.json` with
  `dev` and `test` (e.g. 140/60, stratified so SF-bearing letters are
  represented in both), plus per-split files.
- A loader `load_letters_for_split(split)` in `data.py`.
- **Develop only on `dev`.** `test` is held out; the **full-200 frozen audit** is
  the benchmark-comparable headline number (satellite 06), run once, authorized.

## 3. Run registry

Reuse `experiments/registry.jsonl` + `validate_run_registry_artifacts`. Every
ExECTv2 run is registered with: architecture, model, prompt version, split,
entity scope, artifact paths, call/parse failure counts, and metadata
(candidate-set mode = live, etc.). Registry validation must stay green.

Artifact naming follows the project ontology
(`contribution_thesis.md`): `exectv2_<architecture>_<entityscope>_<split>_<model>_<promptver>_<date>.{jsonl,md}`.

## 4. Reports

Reuse `reports/base.py` and the three-way comparison report shape. Build:

- per-architecture per-entity report (per-item/per-letter F1, validity rates,
  error list)
- the **three-way comparison report** (rules / llm_only / hybrid) on a shared
  table of universally-meaningful axes, with a model-parameterized title
- overall (all-9) benchmark comparison table vs the published 0.87/0.90

## 5. The experiment loop (discipline)

Each iteration, per architecture/entity:

1. Change one thing (a rule family, a prompt block) — named and ablatable.
2. Pilot on ≈25 dev letters → confirm 0 unexplained failures.
3. Run the full `dev` split.
4. Compare to the previous dev read; require the move to be **plausible and
   explicable**, not merely "up".
5. Register the run; update the report; write a short status note in the relevant
   satellite (inline status-update style, like the Gan 2026 three-way plan).
6. Only combine changes after each is independently validated.

Operational notes (inherited):

- Long live LLM runs: launch via PowerShell `Start-Process` detached
  (`-RedirectStandardOutput/Error`, `-WindowStyle Hidden`) to survive the
  harness's ~9-minute background-task kill.
- Use `uv run` for all commands (project memory: uv workflow).
- Resume-and-merge pattern for interrupted runs (write `.resume-part.jsonl`,
  merge into base), as used in Gan 2026 Phase 3.

## 6. `/loop` and automation

The dev-split iterate→score→report cycle is a natural `/loop` target for
unattended multi-iteration runs (self-paced), and the run-and-register step can
be scheduled. Keep holdout/test runs out of any automation — they are manual,
authorized, one-shot.

## 7. Deliverables & exit criteria

- `runner.py`, split manifest + loader, report builders, registry integration
- A green `validate_run_registry_artifacts` with ExECTv2 entries
- Exit: any architecture can be run on `dev` for SF (Phase 2–5) and all-9
  (Phase 6) through one command, producing a registered artifact and a report.
