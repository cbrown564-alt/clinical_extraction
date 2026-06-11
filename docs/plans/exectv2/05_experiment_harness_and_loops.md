# Satellite 05 — Experiment Harness & Loops

Parent: [[00_overarching_implementation_plan]] · Phases 2–6 (cross-cutting)
Status: **operational for SF (Phases 2–5).** The split, loader, registry
integration, resume, per-architecture dev runners, and the shared three-way
comparison report builder are all built and have carried the SF runs for all
three families; the remaining harness work is only the Phase 6 all-9 extension
(see §8). Dev-split only until the Phase 7 audit.

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

### 5a. Resume is a foundational runner requirement

**Every runner that does expensive incremental per-record work must be
resumable.** A long live run (an LLM sweep over hundreds of records, a slow local
model) must survive interruption — a crash, a killed background process, a
powered-off machine — without re-spending completed work. This is not optional
polish; it is a baseline property of a runner.

The shared implementation is `core/run_resume.py` (task-neutral, tested in
`tests/test_core_run_resume.py`):

- Runners checkpoint a newline-delimited JSON artifact every N records, where
  each row carries a stable per-record key (`letter_id`) and the checkpoint is a
  **full rewrite** of every record processed so far — so any checkpoint is a
  valid, self-consistent prefix.
- On `--resume`, `read_completed` returns the finished rows + key set; the runner
  skips those records, processes only the remainder, and `merge_rows` stitches
  old + new back into split order. No record is recomputed, lost, or duplicated.

Wired into `run_deterministic_sf` is unnecessary — it completes the dev split in
one sub-second pass with no per-record cost — but every LLM-backed runner
(`run_llm_only_sf` single-pass/per-entity, `run_hybrid_sf`) takes `--resume` and
reports `n_resumed` in run metadata. Gan 2026's older `.resume-part.jsonl`
merge-on-`source_row_index` pattern is the same idea predating the core lift.

## 6. `/loop` and automation

The dev-split iterate→score→report cycle is a natural `/loop` target for
unattended multi-iteration runs (self-paced), and the run-and-register step can
be scheduled. Keep holdout/test runs out of any automation — they are manual,
authorized, one-shot.

## 7. Deliverables & exit criteria

- ~~`runner.py`~~ → three per-architecture dev runners (see §8 for why the single
  unified class was not built), split manifest + loader, per-run report
  emission, registry integration — **DONE for SF**
- A green `validate_run_registry_artifacts` with ExECTv2 entries — **DONE**
  (4 LLM-only + 2 hybrid rows registered)
- Shared three-way comparison report builder — **DONE**
  (`reports/three_way_comparison.py`)
- Exit: any architecture can be run on `dev` for SF (Phase 2–5) through one
  command, producing a registered artifact and a report — **MET for SF** via
  `runners/run_{deterministic,llm_only,hybrid}_sf`; all-9 (Phase 6) inherits the
  same runners once per-entity rules/prompts land.

## 8. Implementation status (2026-06-11)

What is built and exercised by real SF runs, and where reality diverged from the
plan above. The divergences are recorded, not hidden — the Gan 2026
asymmetry-handling lesson (§1) applied to the harness itself.

**Splits (§2) — DONE.** Seeded 140-dev / 60-test manifest at
`data/ExECTv2 (2025)/splits/exectv2_split_v1.json` (+ `dev_v1.json` /
`test_v1.json`), loaded by `load_letters_for_split(split)` in
`exectv2/data.py`. `load_letters` (full 200) is reserved for the Phase 7 frozen
audit; all development reads go through `dev`. The loader also applies the D16
gold-`text` := `CUIPhrase` repair for SF/Diagnosis at load time, so every
architecture scores against the same corrected gold.

**Runners (§1) — built as three per-architecture CLIs, not one parameterized
class.** The plan called for a single `ExectPipelineRunner(architecture=...)`
mirroring `Gan2026PipelineRunner`. In practice the three families do not share a
`run(letter)` signature cleanly enough to justify the unification: the
deterministic family is a pure-Python staged pipeline with no per-record cost or
parse-failure surface, while the two LLM families carry model/mode/temperature/
max-tokens/resume/validity-rate machinery. Forcing them into one class would have
been the *hidden-asymmetry* anti-pattern the plan warns against. Instead the
shared contract is the seam:

- `runners/run_deterministic_sf.py` — sub-second full-dev pass, three match
  configs (`phrase_only` / `sf_semantic` / `sf_benchmark`), row-level error list.
- `runners/run_llm_only_sf.py` — `--config {single_pass,per_entity}`,
  `--model`, `--mode {live,prompt-only}`, `--pilot N`, `--resume`.
- `runners/run_hybrid_sf.py` — candidate-set + clinical-assessment route, same
  model/mode/pilot/`--resume` surface.

All three load via `data.py`, emit `PredictedLetter` through the shared
`contract/`, and score through the shared `scoring.py` (`score_entity` with the
SF configs) — so the artifact contract and score axes are uniform across
families even though the runner entry points are separate. The `entities`
generalization (SF-only now, all-9 in Phase 6) lives in the contract/scoring
layer, not the runner shells, so Phase 6 extends the same three commands.

**Resume (§5a) — DONE for every LLM-backed runner.** `core/run_resume.py` is
wired into `llm/llm_only_single_pass.py`, `llm/llm_only_per_entity.py`, and
`hybrid/clinical_assessment.py`; `run_llm_only_sf` and `run_hybrid_sf` both take
`--resume` and report `n_resumed`. `run_deterministic_sf` is deliberately not
resumable (single sub-second pass, no per-record cost), exactly as §5a allows.

**Registry (§3) — DONE for all three families.** Six ExECTv2 rows are registered
and pass `validate_run_registry_artifacts`: LLM-only single-pass and per-entity
(each × `gpt-4.1-mini` and `qwen3.6:35b`, full dev 140), plus the hybrid
candidate-assessment runs — `gpt-4.1-mini` full dev 140
(`exectv2_hybrid_dev140_gpt41mini_20260611`) and the `qwen3.6:35b` run, which
stopped at 50 of 140 letters and is registered **honestly as partial**
(`exectv2_hybrid_dev50partial_qwen3635b_20260611`, `row_count=50`,
`decision=historical`) rather than mislabelled as a full read. All carry
call/parse-failure counts, candidate/keep/route counts, and the six shared score
axes. The deterministic family is deliberately unregistered (§5a) and recomputed
live by the report (below).

**Reports (§4) — per-run reports and the three-way comparison builder both
DONE.** Each runner emits a per-architecture per-entity `.md` alongside its
`.jsonl` (PRF1 under each match config, validity rates, error rows). The
**shared three-way comparison report** is built:
`reports/three_way_comparison.py` renders one model-parameterized table
(rules / llm_only / hybrid on the six universal axes: phrase_only / sf_semantic /
sf_benchmark × per-item/per-letter F1) against the published SF cell (0.66/0.68).
It reads the llm_only/hybrid rows from the registry and computes the rules row
live (the §5a asymmetry — stated in the report's Provenance block, not hidden),
defines the `ARCHITECTURE_FAMILY` grouping map (§1), and excludes partial runs
from the comparison body with a coverage-gap note. The first artifact is
`experiments/exectv2_three_way_comparison_sf_dev_gpt41mini_20260611.md` — on dev,
hybrid leads every axis (phrase_only 0.585/0.781, the only per-letter to clear
the 0.68 SF target; sf_benchmark 0.327/0.578), with rules second on attributes
(0.362/0.575) and LLM-only strongest on bare phrase recall but weakest on
attributes. The all-9 benchmark-vs-0.87/0.90 table reuses the same builder with
`entity` parameterized (Phase 6). Tests: `tests/test_exectv2_three_way_comparison.py`.

**Loop discipline (§5) — followed.** The Phase 2–3 SF work moved one change at a
time (rule families, prompt blocks), piloted on ≈25 dev letters, ran full dev,
and required each move to be explicable; per-statement emission (D8) is the
worked example of a change measured net-negative and reverted rather than kept
for a dev-score bump. Long live LLM runs used the detached `Start-Process`
pattern. The recorded SF reads are summarized in the registry-row descriptions
and in satellites 02/03/04.

**Open items (carry into Phase 6):**

1. ~~Register the hybrid dev140 runs (§3).~~ **DONE** — gpt-4.1-mini full + qwen
   partial-50 registered.
2. ~~Build the shared three-way comparison report builder (§4).~~ **DONE** —
   `reports/three_way_comparison.py` + first dev artifact.
3. Complete the qwen hybrid dev140 run so the qwen three-way is comparison-grade
   (today its hybrid cell is the registered partial-50, excluded from the table).
4. At Phase 6, extend the three runners to `entities=all-9` and call the same
   comparison builder with `entity` parameterized for the all-9
   benchmark-vs-0.87/0.90 table (contract/scoring already entity-parameterized;
   only per-entity rules/prompts are new work).
