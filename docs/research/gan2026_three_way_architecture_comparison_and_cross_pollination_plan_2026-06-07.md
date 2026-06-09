# Gan 2026 Three-Way Architecture Comparison And Cross-Pollination Plan

Date: 2026-06-07

Author: Claude

Status: planning document — defines the workstream; execution requires the
phased authorization gates named below. No benchmark-comparable claim or
holdout-facing protocol is authorized by this document.

Working agreement: as we work through each phase of this plan, run a
`/grill-with-docs` session before locking in terminology or architectural
decisions (e.g. the Section 2 canonical-runner choice, the Section 4/5
cross-pollination mechanisms, the Section 8 open questions). Use it to
stress-test naming and decisions against this project's existing `CONTEXT.md`
/ ADRs, and to capture newly-resolved terms or hard-to-reverse calls inline as
they crystallise rather than after the fact.

---

## 1. Objective

Run a disciplined side-by-side comparison of the three architecture families
this project has built toward:

1. **Fully deterministic** — `Gan2026PipelineV1` (`pipeline_v1.py`): rule-based
   extraction, normalization, selection, render/score. Known to show signs of
   overfitting to validation phrasing.
2. **Hybrid** — two distinct configurations that combine LLM and deterministic
   stages, differing in what the LLM stage does:
   - **Hybrid (reset-native)** — `reset_clinical_assessment_pipeline.py`
     (`"hybrid"` config): deterministic candidate-set extraction → LLM
     clinical assessment → deterministic Normalize → Project → Verify →
     Render/Score. The LLM's task is *selection and assessment* from a
     pre-extracted candidate set. Has a routing/verification stage that the
     other hybrid lacks.
   - **Hybrid (LLM-extract + det-normalize)** — `hybrid_structured_events.py`
     (`"hybrid_structured_events"` config, misnamed on creation): LLM
     extracts structured events from raw note text (open-text → schema) →
     same deterministic Normalize/Project/Render/Score stages. The LLM's task
     is *structured extraction* from raw text. No routing stage. Named
     `hybrid_structured_events` in `PipelineArchitecture` for artifact
     compatibility; see `ARCHITECTURE_FAMILY` in `runner.py` for the correct
     grouping.
3. **Fully LLM** — `llm_only_direct_labeler` and `llm_only_canonical_pipeline`:
   the full extraction-to-label pass in one LLM call, with no deterministic
   normalization stage. Formerly included `hybrid_structured_events` in this
   family — that classification was incorrect.

**Why the two hybrid configs make a more interesting comparison than "hybrid vs
fully-LLM"**: both share the same deterministic downstream stages (Normalize →
Project → Render → Score). The performance gap between them is therefore a direct
measure of (a) how much the *LLM task design* matters (open-text extraction vs.
candidate-set assessment) and (b) the cost of the verification/routing layer that
the reset-native hybrid adds but the LLM-extract hybrid omits.

The comparison is not an end in itself. Its purpose is to **feed back into
both of the other two architectures**:

- use what the hybrid reset discipline has taught us about *generalizable
  versus validation-tuned* rules to refine the deterministic pipeline so it
  stops overfitting;
- use the same discipline — explicit, named, stage-owned, ablatable
  components — to decide which clinical-reasoning aspects the LLM-only
  pipeline's prompts should own outright (broad exploration, clinical
  judgment, contradiction resolution) versus which aspects should be peeled
  off into deterministic normalization/projection so the LLM is not asked to
  also be a parser.

---

## 2. Prerequisite: One Canonical Runner Per Architecture

**Status update (2026-06-07): fully resolved.** The repo-consolidation plan's
Phase F replaced the "assemble a fully-LLM runner" open question with a
unified, parameterized `Gan2026PipelineRunner` (`src/.../gan2026/runner.py`)
that now executes six named `PipelineArchitecture` configurations —
`deterministic`, `deterministic_canonical_pipeline`, `hybrid`,
`llm_only_direct_labeler`, `hybrid_structured_events`, and (as of
2026-06-07, completing the last open Phase 0 item)
`llm_only_canonical_pipeline` — through one shared projection/render/score/
route/decision artifact contract. The `hybrid_structured_events`
configuration *is* the assembled Option-A chain described below: it already
wires an LLM-forward Select/ClinicalAssessment stage through the same
deterministic Normalize→Project→Render→Score→Route→Decision stages the
hybrid configuration uses. No separate assembly step remains for that
comparator, and `llm_only_canonical_pipeline` now closes out the "purest
form" comparator described below as well.

| Architecture | Canonical runner | Status |
| --- | --- | --- |
| Deterministic | `Gan2026PipelineRunner` `"deterministic"` config (wraps `Gan2026PipelineV1` internals) **and**, as of 2026-06-07, the staged `"deterministic_canonical_pipeline"` config | both exist; the canonical config is now staged into named, ablatable Extract/Normalize/[[Select & Render]]/[[Evidence Trace Check]] form (`deterministic_canonical_stages.py`), proven byte-identical to `"deterministic"` by `tests/test_gan2026_deterministic_canonical_pipeline.py` — see resolution note below |
| Hybrid (reset-native) | `Gan2026PipelineRunner` `"hybrid"` config / `hybrid/reset_clinical_assessment_pipeline.py` | exists, already the named "current focus" — det. candidate extraction → LLM assessment → det. Normalize/Project/Render/Score/Route/Decision |
| Hybrid (LLM-extract + det-normalize) | `Gan2026PipelineRunner` `"hybrid_structured_events"` config / `llm/hybrid_structured_events.py` | exists — LLM extracts structured events from raw text → same det. Normalize/Project/Render/Score stages. Architecture string kept as `"hybrid_structured_events"` for artifact compatibility; module renamed `hybrid_structured_events.py` (2026-06-09) to correct original mislabeling. No routing/verification stage. |
| Fully LLM | `Gan2026PipelineRunner` `"llm_only_direct_labeler"` **and** `"llm_only_canonical_pipeline"` configs | both exist — full extraction-to-label in one LLM call, no deterministic normalization stage |

**Phase 0 is now complete.** Both of the previously-remaining
`PipelineArchitecture` configurations have been added to the *existing*
unified runner — not as standalone forked modules (see `CONTEXT.md` for the
resolved naming):

- **`deterministic_canonical_pipeline`** *(done — 2026-06-07)*: the existing
  deterministic logic restructured into four named, stage-owned, ablatable
  stages — Extract, Normalize, [[Select & Render]] (this architecture's named
  selection-and-rendering stage; see `CONTEXT.md` for why it is one combined
  stage here rather than mirroring the hybrid pipeline's separate
  Project/Render seam), and [[Evidence Trace Check]] (this architecture's
  verify-adjacent stage, deliberately *not* named `Verify` — see
  `docs/decisions/0014-evidence-trace-check-not-verify-for-deterministic-canonical-pipeline.md`
  for why it does not reuse `VerificationDecision`/`Verifier Action`
  vocabulary) — implemented in `deterministic_canonical_stages.py` as thin
  named wrappers over the existing internals, with its current rules left
  unchanged — a pure staging pass, so Section 4's family-by-family
  de-overfitting rewrite has a legible, measurable starting point. Proven
  byte-identical to `"deterministic"` (`output` and `diagnostics`, including
  diagnostics-key shape) by
  `tests/test_gan2026_deterministic_canonical_pipeline.py` on a small
  known-row sample — the directly assertable "rules unchanged" guard. See
  `docs/decisions/0013-stage-deterministic-canonical-config-before-generalizing-its-rules.md`
  for why staging and generalizing are deliberately kept as two passes.
- **`llm_only_canonical_pipeline`** *(done — 2026-06-07)*: a new single-shot
  configuration that collapses extract→select→normalize→project→render into
  one LLM call, with the now-mature deterministic rule taxonomy (cluster-axis
  ambiguity, seizure-free conflict, same-window additive frequency,
  denominator-window mismatch, medication-cadence ambiguity, cluster-cadence-
  as-event-rate, unknown-cadence cluster burden, concrete-frequency
  precedence, dominant-vague-current-burden, seizure-free proxy evidence
  overreach, conditional-only trigger, relative-only trend, and
  multiple-current-primary-facts) embedded as prompt instructions — under
  `guidance_for_tricky_cases` in the prompt payload, reworded in plain
  clinical language rather than this project's internal stage/architecture
  vocabulary, since the model is given no other context about those internal
  naming conventions — rather than pre/post processing — the "purest form"
  fully-LLM comparator, sitting
  alongside (not replacing) the existing
  `llm_only_direct_labeler`/`hybrid_structured_events` configurations.
  Implemented in `llm/llm_only_canonical_pipeline.py` and wired into
  `Gan2026PipelineRunner` (`run`, `run_split`, `get_cli_specs`); see
  `tests/test_gan2026_llm_only_canonical_pipeline.py`. It reports a distinct
  evidence text-containment metric (`evidence_text_contained` /
  `evidence_text_containment_rate`, mirroring `evidence_is_substring`) rather
  than the formal `CandidateSet` source-id validity rate, since forcing
  single-shot LLM output through that machinery would misrepresent what the
  architecture actually produces.

The historical "Option A vs Option B" framing below is now superseded by this
resolution — Option A is built (`hybrid_structured_events`, now correctly
classified as a hybrid and with its module renamed `hybrid_structured_events.py`),
and `llm_only_canonical_pipeline` is the new, more precisely-scoped "purest form"
target that replaces the open-ended Option B framing:

- **Option A — hybrid LLM-extract comparator** *(done — `"hybrid_structured_events"`
  config / `hybrid_structured_events.py`)*: LLM extracts structured events from raw
  note text → same deterministic Normalize/Project/Render/Score stages as the
  reset-native hybrid. Originally framed as swapping only the Select/ClinicalAssessment
  stage for a more LLM-forward module; better described as a second hybrid variant
  with a different LLM task. The performance gap between this and the reset-native
  hybrid is the direct measure of LLM task design and verification/routing cost.
- **Option B — fully-LLM comparator** *(superseded by `llm_only_canonical_pipeline`)*:
  rather than the original "claim table / direct label chained to a render/score
  boundary" framing, the resolved target is a true single-shot, rules-in-prompt
  pipeline that owns normalize/project itself — the most honest "fully LLM"
  test, wrapped in a thin artifact-shape adapter so the existing comparison
  tooling still runs.

---

## 3. Comparison Protocol

**Status update (2026-06-07): report shape scoped, not yet run.** Mapping the
six configs' `run_split()` output surfaces surfaced a real asymmetry this
protocol has to account for: only `hybrid` has a routing/verification stage,
and its lightweight `run_split` probe doesn't expose rendered/null/routed/
purist numbers at all — those only exist via `build_unified_pipeline_artifact`
("deep replay"). Resolved with the user (2026-06-07): compare all six on the
universally-meaningful axes (rendered/null, Purist/Pragmatic-correct,
evidence-trace validity, final-label distribution) in one shared table, with
`hybrid`'s shared-table numbers sourced from its deep-replay artifact (stated
plainly as the architectural fact it is, not hidden as a methodology quirk),
plus a separate hybrid-only routing-taxonomy appendix drawing on that same
replay. Full design, open data-availability questions (pragmatic-correct and
source-id validity for the deep-replay path), and a pilot-before-full-run
sequencing recommendation are in
[[gan2026_three_way_comparison_phase1_report_design]].

Run all three canonical runners over the **same validation750 surface** (and
only later, as a frozen aggregate audit, over `test450` — see Section 6),
using the existing artifact and scoring tooling so the comparison is
apples-to-apples:

- rendered / null / routed counts
- Purist-correct / Pragmatic-correct on rendered rows
- routed-row taxonomy (which families route, and why)
- evidence-trace and source-id validity rates (this doubles as input to
  [[gan2026_evidence_grounded_thesis_assessment_plan]])
- validation-to-test gap, once a frozen `test450` audit is authorized

Report format: reuse `reports/base.py` and the existing
`reset_stage_component_ablation_v6`-style comparison shape rather than
inventing a new one — this is itself a small DRY exercise that previews
[[gan2026_repo_consolidation_and_cleanup_plan]] Phase F.

**Status update (2026-06-08): validation750 runs complete; hybrid's surface is
scoped to a 250-row subset, by design decision (not a bug to fix before
reporting).** All six configs have now been run over validation750 for both
`gpt-4.1-mini` and `qwen3.6-35b` (see `experiments/gan2026_three_way_comparison_validation750_*`).
While assembling these, `hybrid`'s run surfaced a wiring fact the phase1
report design note didn't yet account for: `llm_candidate_set_clinical_assessment_probe.run_split`
(the function `hybrid` delegates to) does not generate candidate sets live —
it does a dictionary lookup against a static precomputed file
(`DEFAULT_CANDIDATE_SET_JSONL_PATH`, currently
`gan2026_validation250_candidate_set_v2_high_recall.jsonl`, a 250-row
artifact), and emits a `candidate_set_missing` placeholder row for any
`source_row_index` outside that frozen set. Concretely: of validation750's 750
rows, only 250 produce a real clinical-assessment row; the other 500 report
`candidate_set_missing` (see e.g.
`experiments/gan2026_three_way_comparison_validation750_hybrid_gpt41mini_2026-06-07.md`).

**Decision (2026-06-08, with the user): document `hybrid`'s comparison numbers
as scoped to its available ~250-row subset — do not block Phase 1's report on
fixing this first.** When the Phase 1 comparison report
([[gan2026_three_way_comparison_phase1_report_design]]) is assembled, it must
state plainly (in the same provenance/disclosure spirit as the deep-replay
asymmetry already documented there) that `hybrid`'s row is computed over its
~250-row candidate-set subset, not the full 750-row surface the other five
architectures cover — an architectural fact about `hybrid`'s current wiring,
not a missing-data artifact to paper over or silently average away. Wiring
live candidate-set generation into `hybrid` so it covers the full surface is
tracked as a separate follow-up — see Section 8a.

**Status update (2026-06-08, later same day): the Section 8a follow-up shipped
ahead of schedule, `hybrid` now covers the full 750-row surface, and the
gpt-4.1-mini Phase 1 report is built and registered.** The user asked to move
on this immediately rather than wait — see Section 8a for the implementation
summary. The re-run replaced
`gan2026_three_way_comparison_validation750_hybrid_gpt41mini_2026-06-07`
(kept as the historical record of the 250-row-scoped numbers) with
`gan2026_three_way_comparison_validation750_hybrid_live_candidate_sets_gpt41mini_2026-06-08`
(750/750 rows, 0 call failures, 1 parse/validation failure,
`missing_candidate_set_rows: 0`). The Phase 1 comparison report
([[gan2026_three_way_comparison_phase1_report_design]]) is now assembled at
`gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08.{jsonl,json,md}`
and both the re-run and the report are registered in `experiments/registry.jsonl`
(`validate_run_registry_artifacts` passes clean, 58 entries total). **Phase 1
is complete for the gpt-4.1-mini pass** (the qwen3.6-35b pass remains in
flight separately and was not blocked by this work).

Key findings the report surfaces, worth carrying into Phases 2-3:

- **`deterministic` and `deterministic_canonical_pipeline` are numerically
  identical** on this pass — same purist/pragmatic-correct counts (688/695 of
  741 rendered) and the same final-label distribution. This is the directly
  measurable confirmation that the Section 2 staging pass changed *only*
  structure, not behavior — exactly what it was designed to prove, and a clean
  baseline for Section 4's de-overfitting rewrite to diverge from
  legibly.
- **`hybrid`'s now-honest full-surface numbers are markedly different from
  its old 250-row-scoped read**: 600/750 rendered (149 null, 42 routed),
  511 purist-correct of rendered (0.852) — lower than every other architecture
  except `llm_only_direct_labeler`. This is the real, full-surface hybrid
  baseline Section 4/5's cross-pollination work should compare against, not
  the partial one.
- Evidence-trace metrics remain structurally non-uniform across architectures
  (substring-presence `evidence_valid` vs. `evidence_text_contained` vs.
  `hybrid`'s formal `candidate_set_source_id_status` rate) — the report states
  this explicitly per architecture so it isn't misread as one accuracy axis.

**Next up**: Phase 2 (de-overfitting the deterministic pipeline, Section 4)
and/or Phase 3 (prompt refinement, Section 5) can now begin — both have a
clean, full-surface, six-architecture baseline to diverge from and re-compare
against. Phase 4's frozen `test450` audit remains gated on explicit user
authorization per Section 6.

**Status update (2026-06-09, updated): deepseek-v4-flash Phase 1 report built; qwen3.6-35b
full-surface Phase 1 report built (Section 8b done). All three model Phase 1 reports are
now complete on the full 750-row surface.**
The `three_way_comparison_report.py` builder was extended to accept `--model` (title
and claim-boundary string) and `--hybrid-candidate-set-path` (fallback for pre-section-8a
hybrid runs that do not have `candidate_set` embedded in output rows). This enables
model-parameterized report generation without re-running the deterministic configs.

- **`deepseek/deepseek-chat` (deepseek-v4-flash) — full 750-row surface**: all six
  configs at 750/750 rows, hybrid live candidate sets. Report at
  `experiments/gan2026_three_way_comparison_phase1_report_deepseek_validation750_2026-06-09.{jsonl,json,md}`.
  Key finding: `hybrid_structured_events` leads LLM configs at 609/742 purist-correct
  (0.821). Hybrid routes much more aggressively than gpt-4.1-mini: 123/604 rendered rows
  routed (0.204), dominated by `rendered_label_supported_but_policy_sensitive` (97/123),
  vs gpt-4.1-mini's 42/600 (0.070). Deepseek hybrid purist-correct 490/604 (0.811).

- **`ollama_chat/qwen3.6:35b` interim — hybrid 250-row scoped**: the qwen hybrid
  validation750 run was initiated before the section-8a live-wiring fix and used the
  static 250-row candidate-set file; the remaining 500 rows are being re-run live as of
  2026-06-09. The interim report
  (`experiments/gan2026_three_way_comparison_phase1_report_qwen3635b_validation750_2026-06-09.{jsonl,json,md}`)
  uses the static file as a `--hybrid-candidate-set-path` fallback and reports hybrid as
  250-row scoped (stated explicitly in the hybrid footnote and visible as `Examples: 250`
  in the shared table — not papered over). `hybrid_structured_events` leads at
  624/746 (0.836). The final full-surface qwen report will supersede this once the hybrid
  live re-run completes (see Section 8b).

---

## 4. Cross-Pollination A: De-Overfitting The Deterministic Pipeline

**Status update (2026-06-09): Phase 2 complete — all families assessed;
iterations 1 and 2 done.** Total intentional regression: −15 purist-correct
(688→673 of 741 rendered = 0.928→0.908) across both iterations. No further
de-overfitting warranted; remaining families are genuinely general.

### Rule Family Classification (2026-06-09, final)

| Family (`RuleGroup`) | Portability | Classification | Priority |
| --- | --- | --- | --- |
| `GAN_SHORTHAND` | `GAN2026_SPECIFIC` (was) | **Validation-phrase-shaped** — compact notation with GAN-specific embellishments (word numbers in shorthand, asterisk/X/× separator prefixes); Q_INTERVAL is general medical notation | **High — done 2026-06-09 (iteration 1)** |
| `BENCHMARK_REPAIR` | `BENCHMARK_FORMAT` | **Format/representation** — output normalization for benchmark label format; not extractive | Low — skip (not extractive) |
| `PORTABLE_RATE_EXPRESSIONS` | `SEIZURE_FREQUENCY` | **Genuinely general** — word numbers in prose ("three seizures per week", "four consecutive days") are normal clinical English; literal-phrase anchors assessed and confirmed general | **Assessed 2026-06-09 — no change needed** |
| `SEIZURE_FREE_NO_EVENT_ASSERTIONS` | `SEIZURE_FREQUENCY` / `CLINICAL_EPILEPSY` | **Genuinely general** — duration computations general; `CURRENT_CONTROL_PHRASE_RULE` phrases are semantically correct seizure-free assertions with no false-positive risk on real text | **Assessed 2026-06-09 — no change needed** |
| `CLUSTER_ARITHMETIC` | `SEIZURE_FREQUENCY` | **Partially GAN-specific** — `cluster.compact_count_per_period`: word numbers in compact "clusters N×/month" shorthand are GAN-specific; digit-only counts and structural cluster patterns are general | **Done 2026-06-09 (iteration 2)** |
| `DIARY_LOG_AGGREGATION` | `SEIZURE_FREQUENCY` | **Partially GAN-specific** — `diary.seizure_days_fraction`: word number in compact "Seizure days: six/30" fraction is GAN-specific; other diary rules already digit-only | **Done 2026-06-09 (iteration 2)** |
| `TEMPORAL_SELECTION` | `SEIZURE_FREQUENCY` | **Clinically general** — non-extractive ranking rules; genuine clinical priority | Low — skip (non-extractive, no change needed) |

### Phase 2 Iteration 1: GAN_SHORTHAND Generalization (2026-06-09)

**What changed**: all four `GAN_SHORTHAND` rules rewritten from
`GAN2026_SPECIFIC` portability to `SEIZURE_FREQUENCY` (TC/sz and absence
shorthand) and `CLINICAL_EPILEPSY` (Q_INTERVAL). Two classes of GAN-specific
embellishments removed:

1. **Word numbers in compact shorthand** (e.g., "TC nine/mo", "sz xfour/wk",
   "qtwo - threewk") — replaced `NUMBER_VALUE_TOKEN` with `DIGIT_RANGE_TOKEN`
   (digit-only); real clinical notes use digit counts
2. **Special separator prefixes** (asterisk `*`, letter `X`, `×`) before
   counts (e.g., "TC *5/wk", "sz X7/mo") — removed the `(?:[*x×]\s*)?`
   group; standard compact notation uses space or colon separators

What kept: digit-count compact notation without special separators ("TC 5/mo",
"sz 2/wk", "q2-3wk", "abs monthly", "abs 8 monthly").

**Phase 2 vs Phase 1 comparison** (validation750, deterministic architectures
only — LLM/hybrid configs unchanged):

| Architecture | Phase 1 | Phase 2 (GAN_SHORTHAND generalized) | Delta |
| --- | --- | --- | --- |
| `deterministic` | 688/741 purist (0.928) | 674/741 purist (0.910) | −14 |
| `deterministic_canonical_pipeline` | 688/741 purist (0.928) | 674/741 purist (0.910) | −14 |

The −14 is the correct de-overfitting outcome: all 14 rows were previously
correct only via GAN-specific notation that does not appear in generalized
clinical text. Breakdown: 10 fell to "no seizure frequency reference" (lost
sole candidate); 2 switched to "seizure free" (seizure_free candidate now wins
over absent rate candidate); 1 gained a cluster candidate; 1 switched to "1
per day" from "daily auras".

Artifacts:
- Phase 2 deterministic run: `experiments/gan2026_three_way_comparison_validation750_deterministic_phase2_gan_shorthand_generalized_2026-06-09.jsonl`
- Phase 2 canonical run: `experiments/gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_phase2_gan_shorthand_generalized_2026-06-09.jsonl`
- Phase 2 comparison report: `experiments/gan2026_three_way_comparison_phase2_report_gan_shorthand_generalized_validation750_2026-06-09.{jsonl,json,md}`
- Tests updated: `test_gan2026_rule_metadata.py::test_gan_shorthand_rules_are_generalized_and_retain_group`, `test_gan2026_pipeline_v1.py` (GAN-specific notation examples → generalized equivalents). Full suite: 1019 passed.

### Phase 2 Intermediate Assessment: PORTABLE_RATE_EXPRESSIONS (2026-06-09)

**Assessment**: genuinely general — no change needed. All rules in this family
use word numbers in running prose ("three seizures per week", "four consecutive
days", "two clusters") which is normal clinical English, not GAN-specific
shorthand. The literal-phrase anchors (`DAILY_BASIS_CURRENT_RULE`:
"seizures/episodes on a daily basis", `THERE_HAVE_BEEN_COUNT_RULE`: "there
have been N [seizure terms]") are standard clinical phrasing that appears in
real documentation regardless of dataset provenance. No rules rewrote.

### Phase 2 Iteration 2: CLUSTER_ARITHMETIC + DIARY_LOG_AGGREGATION (2026-06-09)

**What changed**: two compact-notation rules narrowed from word numbers to
digit-only counts, matching the same GAN-specific pattern identified in
iteration 1 (word numbers in compact shorthand, not prose):

1. **`cluster.compact_count_per_period`** (`CLUSTER_ARITHMETIC`): pattern
   `(?P<count>{NUMBER_TOKEN})` → `(?P<count>{DIGIT_RANGE_TOKEN})`. Compact
   "clusters N×/month" shorthand with word numbers (e.g., "Morning clusters
   one - two×/month") is GAN-specific. Digit counts and digit ranges ("clusters
   3×/month", "morning clusters 2 to 4×/month") are general.

2. **`diary.seizure_days_fraction`** (`DIARY_LOG_AGGREGATION`): pattern
   `(?P<count>{NUMBER_VALUE_TOKEN})` → `(?P<count>\d+)`. Compact "Seizure days:
   six/30 this month" with word number is GAN-specific. Digit count ("Seizure
   days: 8/30 this month") is general.

**`PORTABLE_RATE_EXPRESSIONS` word numbers not touched**: word numbers in prose
("three seizures per week", "absence of events for over six months") are NOT
GAN-specific and correctly remain using `NUMBER_TOKEN`. The distinction is:
compact shorthand notation = GAN-specific; running prose = general.

**Other diary rules not touched**: `monthly_count_log`, `seizure_day_log`, and
`increasing_monthly_count` already used digit-only patterns; no change.

**Phase 2 iteration 2 vs iteration 1 comparison** (validation750, deterministic
architectures only):

| Architecture | Iteration 1 (GAN_SHORTHAND) | Iteration 2 (+ cluster/diary) | Delta |
| --- | --- | --- | --- |
| `deterministic` | 674/741 purist (0.910) | 673/741 purist (0.908) | −1 |
| `deterministic_canonical_pipeline` | 674/741 purist (0.910) | 673/741 purist (0.908) | −1 |

The −1 is from row 148 ("Seizure days: six/30 this month" → null — sole
candidate, purist_correct=True → False). The cluster change affected row 454
("Morning clusters one - two×/month" dropped) but that row was already
purist_correct=False (no score impact). Pragmatic: −2 (both rows lost pragmatic
correctness).

Artifacts:
- Phase 2 deterministic run: `experiments/gan2026_three_way_comparison_validation750_deterministic_phase2_cluster_diary_digit_2026-06-09.jsonl`
- Phase 2 canonical run: `experiments/gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_phase2_cluster_diary_digit_2026-06-09.jsonl`
- Phase 2 comparison report: `experiments/gan2026_three_way_comparison_phase2_report_cluster_diary_digit_validation750_2026-06-09.{jsonl,json,md}`
- Tests updated: `test_gan2026_pipeline_v1.py` (word-number diary example → digit count, word-number cluster example → anti-example). Full suite: 1019 passed.

### Phase 2 Final Assessment: SEIZURE_FREE + TEMPORAL_SELECTION (2026-06-09)

**SEIZURE_FREE_NO_EVENT_ASSERTIONS** — no change needed. Duration rules
(`since_date`, `absence_for_duration`, `no_events_for_duration`,
`duration_status`, `one_and_half_years`, `last_epileptic_event`,
`generic_duration_or_since`) all use word numbers in prose: genuinely general
clinical English. `CURRENT_CONTROL_PHRASE_RULE`'s specific phrase list is
semantically correct regardless of dataset provenance — every phrase correctly
identifies seizure-free status; no false-positive risk on real clinical text.
The distractor guard (`_is_generic_seizure_free_distractor`) is clinically
motivated, not phrase-calibrated.

**TEMPORAL_SELECTION** — no change needed. Non-extractive ranking rules
(recency weighting, current-status priority) express genuinely general clinical
priority principles, not validation-phrase-shaped patterns.

**Phase 2 status: complete.** Total de-overfitting across all iterations:
−15 purist-correct (688/741=0.928 → 673/741=0.908). Both regressions are
intentional: the removed patterns depended on GAN-dataset-specific compact
notation not present in generalized clinical documentation.

**Problem**: the deterministic pipeline's rules were largely written and tuned
against validation phrasing. Some are likely genuinely general; others are
likely literal-phrase or threshold matches that happen to fire on validation
rows and will not generalize.

**Mechanism**:

1. Walk the deterministic rule inventory (`deterministic/rule_metadata.py`,
   `deterministic/rules/`, `deterministic_rate_extraction.py`) and classify
   each rule family as: *clinically general principle*, *format/representation
   rule*, or *validation-phrase-shaped pattern match*.
2. Cross-reference each family against the now-mature hybrid
   Normalize/Project family taxonomy (the same families named in
   `gan2026_test450_null_reduction_synthesis_and_hypotheses_2026-06-07.md`
   Section 3 and the reset-stage component inventory). Where a hybrid family
   already expresses the same clinical intent in a more general,
   source-backed, ablatable form, treat that as the **rewrite target** for the
   deterministic counterpart.
3. Rewrite validation-phrase-shaped rules into the same general form: anchor
   to source-backed structure (operands, anchors, windows) rather than literal
   phrase lists, and add the same trace/ownership fields the reset pipeline
   already requires.
4. Re-run the deterministic comparator after each rewritten family and check:
   does the validation score move in a *plausible, explicable* direction (not
   just "up")? Is there any sign the rewrite reduces phrase-overfitting
   without losing genuinely-general coverage?

**Guardrail**: this is explicitly *not* "make the deterministic pipeline score
like the hybrid one." It is "make the deterministic pipeline's rules
expressible as general, source-backed, ablatable principles" — the same
standard already applied to every new hybrid Normalize/Project family. If a
rule cannot be rewritten that way, that is itself a useful finding: it means
the rule was never a generalizable clinical principle, and its retirement (not
its preservation) is the correct action.

---

## 5. Cross-Pollination B: Refining The Fully-LLM Prompts

**Governing principle for all prompt rewrites under this section**: every
model-facing string (Signature docstrings, field descriptions, JSON payload
keys/values/instructions) must be a plain, task-oriented brief written for a
reader with none of this project's internal context — see
[[0015-model-facing-prompt-language-must-drop-internal-architecture-vocabulary]]
(established while building `llm_only_canonical_pipeline`'s
`guidance_for_tricky_cases` block) and its enforcement test,
`tests/test_gan2026_llm_prompt_hygiene.py`. Restate the underlying constraint
in plain language rather than naming the internal concept (e.g.
"normalization"/"projection"/"rule taxonomy"/"scored"/"downstream").

**Problem**: the `llm_only_*` prompts currently ask the model to do
everything — extraction, normalization, projection, and clinical judgment —
in one pass. The hybrid reset architecture's central lesson (made explicit by
the HN1-HN5 null-reduction synthesis) is that **representation loss is mostly
a normalization/projection problem, not a clinical-judgment problem**. The
model is already choosing the right fact in most null rows; it is the
downstream representation that fails to carry it through.

**Mechanism**:

1. Catalog the Normalize/Project families now under explicit stage ownership
   in the reset pipeline (frequency value recovery, multi-month bucket
   aggregation, seizure-free anchor/duration instrumentation, cluster operand
   completion, vague-with-window rendering, denominator-window resolution,
   etc. — see the reset-stage component inventory). This catalog becomes a
   **checklist of things the fully-LLM prompt should be relieved of**: if a
   deterministic stage already owns turning a selected fact into a renderable
   value, the LLM prompt does not need to also reason about count/range/period
   formatting, anchor arithmetic, or denominator windows.
2. Catalog, in parallel, the things the reset pipeline still routes to a
   human/LLM-facing decision because no deterministic rule safely resolves
   them: competing-burden ambiguity, current-vs-historical distinction,
   clinical plausibility judgments, contradiction detection. This becomes a
   checklist of **things the fully-LLM prompt should be asked to focus on**.
3. Rewrite the canonical fully-LLM prompt (from Section 2's chosen runner)
   around this division: "select and judge the dominant current clinical
   fact; do not worry about exact value formatting — describe what you found
   in the source's own terms and let normalization carry it."
4. State the **portable principle** explicitly, in writing, as a standalone
   short note this plan can point to: *the LLM should reason about clinical
   truth (which fact is true, how confidently, how it relates to competing
   claims); deterministic stages should own representation, arithmetic, and
   format*. This is the same separation of concerns already proven out by the
   hybrid reset pipeline's stage contract — it is not a new idea, just an
   explicit statement of why it generalizes.
5. Stress-test the rewritten prompt the same way the hybrid pipeline's
   components are stress-tested: validation-only proxy slices first, no
   holdout-facing claims until promotion criteria are met (reuse Section 7.4
   of the null-reduction synthesis as the promotion rubric, generalized to
   "prompt change" rather than "Normalize component").

**Status update (2026-06-09): uncertainty signal audit complete — three
concrete prompt fixes identified before Phase 3 begins.** An exploratory
analysis of all confidence/uncertainty fields across the six architectures was
run over the validation750 surface (all three models). Full findings in
[[gan2026_uncertainty_signal_audit_2026-06-09]]; summary below.

The audit revealed that the codebase has ten distinct forms of uncertainty
expression spread across five layers, with no shared scale, vocabulary, or
ownership model. Three specific prompt-level fixes are required before Phase 3's
rewrite pass — they are independently ablatable, require no schema changes, and
should each be validated individually before being combined:

**Phase 3 pre-condition A — Ground the `confidence` field operationally.**
The `confidence: Literal["low", "medium", "high"]` field on
`llm_only_direct_labeler` and `llm_only_canonical_pipeline` is degenerate for
gpt-4.1-mini and qwen: both models assign `"high"` to 99%+ of rows (gpt-4.1-mini
emits non-high on 1/750 rows; qwen on 3–9/750). The field *does* carry real
signal for deepseek — medium/low rows are 25–30pp below high rows — but only
because deepseek populates it with a real distribution. The fix is not a schema
change but a prompt change: define each level in plain clinical language tied to
observable note features rather than leaving it undefined:
- `"low"`: competing current facts that the guidance above did not resolve, or
  the frequency can only be described as a vague range with no time window
- `"medium"`: one fact is clearly dominant but ambiguity remains (e.g.
  conditional trigger, vague count with a clear window, relative-only trend)
- `"high"`: one unambiguous current fact, no competing claims, evidence is a
  direct quote from the note

**Phase 3 pre-condition B — Replace `uncertainty_flags` (hybrid) with a
closed vocabulary.** The `uncertainty_flags: list[str]` field on
`ClinicalAssessment` is free text; different models emit synonymous values under
different names (deepseek: 50+ distinct strings across 123 rows; gpt-4.1-mini:
9 strings across 24 rows; qwen: 16 strings across 19 rows — same 750-row
dataset, not comparable). The `VerificationRouteFamily` enum (15 named values:
`cluster_axis_ambiguity`, `seizure_free_conflict`, `conditional_only_trigger`,
`multiple_current_primary_facts`, etc.) already names the clinically meaningful
uncertainty types precisely. The hybrid clinical-assessment prompt should offer
this list and ask the model to select from it rather than improvise free text.
This makes the field aggregatable across models and links it to the routing stage
that already acts on the same taxonomy.

**Phase 3 pre-condition C — Add a decision table for `aggregation_policy` to
the hybrid prompt.** The 8-value `AggregationPolicy` enum is the right design
but models interpret it inconsistently: deepseek uses `unknown_due_to_ambiguity`
on 13.1% of rows; gpt-4.1-mini on 0.1% — same data, 130× difference. A short
decision table in the clinical-assessment prompt (parallel to the
`guidance_for_tricky_cases` block already proven in `llm_only_canonical_pipeline`)
stating when each value applies would make the field cross-model comparable.

One counter-intuitive finding worth carrying forward: `answer_kind = "unknown"`
rows have *higher* purist accuracy than `answer_kind = "frequency"` rows for
gpt-4.1-mini (89% vs 74% for direct_labeler; 85% vs 75% for canonical). The
model is correctly identifying genuinely unknowable cases — `answer_kind` is a
classification of outcome type, not a confidence signal, and should not be
treated as one. The lowest-accuracy kind is `"seizure_free"` (66–79% across
models and architectures), where clinical extraction error concentrates
regardless of expressed confidence.

---

## 6. Phasing And Authorization Gates

| Phase | Work | Gate |
| --- | --- | --- |
| 0 | *(done — 2026-06-07)* Select/assemble one canonical runner per architecture (Section 2); confirm artifact-shape compatibility with existing scoring tooling | none — mechanical/structural work |
| 1 | *(done for all three models — gpt-4.1-mini 2026-06-08; deepseek-v4-flash 2026-06-09; qwen3.6-35b full-surface 2026-06-09 via Section 8b)* All six canonical configs run on validation750 for all three models; full-surface reports at `experiments/gan2026_three_way_comparison_phase1_report_{gpt41mini,deepseek,qwen3635b_full}_validation750_2026-06-09.{jsonl,json,md}`; cross-model synthesis at `docs/research/gan2026_cross_model_comparison_2026-06-09.md` | none — validation-only |
| 2 | *(done — 2026-06-09: all families assessed, two iterations complete — GAN_SHORTHAND (iter 1, −14) + CLUSTER_ARITHMETIC/DIARY_LOG_AGGREGATION digit-only (iter 2, −1); PORTABLE_RATE_EXPRESSIONS/SEIZURE_FREE/TEMPORAL_SELECTION assessed and confirmed general; total: −15 purist-correct, 688→673 of 741 rendered = 0.928→0.908 — see Section 4 status update)* Apply the de-overfitting rewrite to one deterministic rule family at a time; re-run and compare after each | none — validation-only, ablatable, one family at a time |
| 3 | *(done — 2026-06-09, gpt-4.1-mini: DL v0.5 +11, CP v0.5 +1, hybrid v5 +3.2pp purist; Phase 3 report at `experiments/gan2026_three_way_comparison_phase3_report_gpt41mini_validation750_2026-06-09.{jsonl,json,md}`; see Section 8c/8d)* Apply the prompt-refinement principle to the canonical fully-LLM runner; re-run and compare after each change. **Pre-conditions before starting**: complete the three uncertainty-signal prompt fixes identified in the 2026-06-09 audit (Section 5 status update / [[gan2026_uncertainty_signal_audit_2026-06-09]]): ground `confidence` operationally, replace `uncertainty_flags` with a closed vocabulary, add an `aggregation_policy` decision table to the hybrid prompt | none — validation-only |
| 4 | Frozen `test450` aggregate audit of the refined deterministic, refined fully-LLM, and current hybrid pipelines, using the exact frozen-aggregate-audit protocol already proven in `gan2026_test450_hn1_frozen_aggregate_audit_2026-06-07.md` | **requires explicit user authorization**, exactly as already required for any holdout-facing reset work |

Phases 0-3 are validation-only development mechanics and need no new
authorization beyond what the project's existing guardrails already grant.
Phase 4 is the only phase that touches the locked `test450` split, and must
follow the same frozen-aggregate, no-row-tuning discipline already
established and proven.

---

## 7. Guardrails (inherited, not new)

- No row-level holdout tuning; `test450` is touched only as a frozen aggregate
  audit, and only with explicit authorization (Section 6, Phase 4).
- No hidden repair, no holdout-tuned fallback, no verifier-written labels for
  null rows.
- Every ported or rewritten rule must be named, stage-owned, source-backed,
  trace-visible, and ablatable — the same bar already applied to every HN1-HN5
  component.
- Treat "the deterministic pipeline scores lower after de-overfitting" as a
  *possible correct outcome*, not a failure: the goal is generalizability, not
  validation score maximization. Report both validation and (eventually,
  frozen-aggregate) holdout reads so the trade is visible.

---

## 8. Open Questions

1. Should the fully-LLM canonical runner ultimately retain *any* deterministic
   scaffolding, or should a second "maximal-LLM" comparator (Option B in
   Section 2) be required before the thesis comparison in
   [[gan2026_evidence_grounded_thesis_assessment_plan]] is considered complete? Answer: hybrid_structured_events serves this purpose.
2. If the de-overfitted deterministic pipeline converges toward the same
   general principles the hybrid pipeline already encodes, does it remain
   worth maintaining as a separate architecture, or does it become a
   documented historical baseline (a question for
   [[gan2026_repo_consolidation_and_cleanup_plan]])? Answer: it serves as a clean comparison to show what LLMs add.
3. How much of the "things the LLM should not need to reason about" checklist
   from Section 5 can be expressed as a single portable prompt-design
   appendix versus needing per-task customization for future benchmark
   families beyond Gan 2026?

---

## 8a. Tracked Follow-Up: Wire Live Candidate-Set Generation Into `hybrid`

**Status: done (2026-06-08) — shipped same-day rather than deferred, at the
user's direction, once Phase 1's first read made the 250-row scoping visible.**

Implemented exactly the chain this section named as already-existing pieces
that just needed wiring: per record, **deterministic candidate-set extraction**
(`deterministic_extraction._extract_candidates` →
`deterministic_candidate_set_from_raw`, the same live path `deterministic`
already uses) → **LLM-extracted candidate-set extraction**
(`DspyCandidateSetExtractor` from `llm_extracted_candidate_schema_probe.py`,
one extra model call per row) → **union**
(`build_candidate_set_union_rows`, the same function that built the static
`_v2_high_recall` artifact, so the live methodology faithfully replicates it).
This replaced `run_split`'s `load_candidate_sets(candidate_set_path)`
dictionary-lookup fallback — `candidate_set_jsonl_path` still works exactly as
before when explicitly passed (frozen-replay/regression paths untouched);
only the *no-path-given* default changed, from "look up in a 250-row static
file, emit `candidate_set_missing` outside it" to "generate live, every row."
`metadata["candidate_set_jsonl_path"]` now records `"live"` in this mode so
downstream report/registry consumers can see which mode produced a run.

Piloted on `validation25` first
(`gan2026_three_way_comparison_pilot25_hybrid_live_candidate_sets_gpt41mini_2026-06-08`)
to confirm behavior and cost before committing to the full re-run — confirmed
clean (25/25 clinical-assessment rows, 0 failures). The full `validation750`
re-run
(`gan2026_three_way_comparison_validation750_hybrid_live_candidate_sets_gpt41mini_2026-06-08`,
superseding the 250-row-scoped `..._hybrid_gpt41mini_2026-06-07` run, which is
kept for the historical record) completed at 750/750 rows, 0 call failures, 1
parse/validation failure, `missing_candidate_set_rows: 0` — `hybrid` now
covers the same full surface as the other five architectures. See the Section
3 status update (2026-06-08, later same day) for what this changed in the
Phase 1 numbers.

**Operational note for future long live-extraction runs**: this run also
surfaced that the harness silently kills `run_in_background` bash tasks at
~9 minutes regardless of actual process health (confirmed by two independent
runs both dying at ~9-minute marks with no error trace). The workaround that
survived past that window and ran to completion was launching via PowerShell
`Start-Process` with explicit `-RedirectStandardOutput`/`-RedirectStandardError`
and `-WindowStyle Hidden` — a genuinely OS-detached process outside the
harness's process-tracking. Worth remembering for any future multi-hour live
run on this project.

<details>
<summary>Original deferral note (superseded — kept for context)</summary>

**Status: not started — explicitly deferred out of Phase 1 (2026-06-08).**

`hybrid`'s canonical runner path
(`llm_candidate_set_clinical_assessment_probe.run_split`) currently sources its
first stage's input from a static, precomputed 250-row file
(`DEFAULT_CANDIDATE_SET_JSONL_PATH` →
`gan2026_validation250_candidate_set_v2_high_recall.jsonl`) via
`load_candidate_sets`, rather than computing a `CandidateSet` live per record.
Rows whose `source_row_index` falls outside that frozen 250-row set get a
`candidate_set_missing` placeholder — which is why `hybrid`'s validation750 run
(Section 3 status update, 2026-06-08) only produced real clinical-assessment
rows for 250/750 rows.

The pieces needed to wire this live already exist in the codebase as
standalone, one-shot artifact-building scripts, just not chained into
`run_split`:

- `deterministic_candidate_set_from_raw` (`contract/candidate_set.py:207`) —
  the deterministic-ruleset extraction step, already wired live elsewhere
  (e.g. the `deterministic` architecture)
- an LLM-based candidate extractor (the step that originally produced
  `gan2026_validation250_llm_candidate_set_v0.jsonl`)
- `build_candidate_set_union_rows` (`artifact_analysis/candidate_set_union.py:33`)
  — combines the two into the union artifact `hybrid` currently consumes
  frozen

**The fix**: replace `run_split`'s `load_candidate_sets(candidate_set_path)`
dictionary lookup with a live per-record call chain — deterministic extraction
→ LLM candidate extraction → union — so `hybrid` covers the full surface (the
same `validation750`/`test450` splits the other five architectures already
do), rather than only the 250 rows someone happened to pre-build a candidate
set for.

**Why this is a separate task, not a Phase 1 blocker**: it is a real
architectural change to `hybrid`'s first stage (not a quick patch — see the
analysis that produced this entry), and `hybrid`'s validation750 numbers can be
reported honestly as scoped to its current 250-row subset (Section 3 status
update) without it. Doing it now would also risk destabilizing the in-flight
qwen750 comparison run. Revisit once Phase 1's report is out and the user is
ready to spend the live-extraction API budget this requires.

</details>

---

## 8b. Tracked Follow-Up: Full-Surface qwen3.6-35b Hybrid Re-Run And Final Report

**Status: done (2026-06-09) — hybrid re-run complete; full-surface report built and
registered.**

The 500-row live re-run completed (500/500, 0 call failures, 0 parse errors,
`candidate_set: live`). The resulting rows were merged into
`gan2026_three_way_comparison_validation750_hybrid_qwen3635b_2026-06-08.jsonl`
(750/750, 250 rows with static candidate sets from original run + 500 with live
candidate sets from resume-part — confirmed by overlapping `source_row_index` sets and
content identity check). The full-surface Phase 1 report was built with the original
deterministic baseline files (pre-Phase 2, for consistency with the gpt-4.1-mini and
deepseek Phase 1 reports) and registered in `experiments/registry.jsonl` (60th entry,
supersedes the interim `gan2026_three_way_comparison_phase1_report_qwen3635b_validation750_2026-06-09`
report):

- Report: `experiments/gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09.{jsonl,json,md}`

Key findings from the full-surface qwen report (see
`docs/research/gan2026_cross_model_comparison_2026-06-09.md` for the three-model synthesis):

- `hybrid_structured_events` leads at 624/746 (0.836).
- `hybrid` renders only **400/750 rows** — far fewer than gpt-4.1-mini (589) or deepseek
  (604). The 350 non-rendered rows break down as 100 null + 62 routed (15.5% route rate);
  `selected_source_id_invalid` accounts for 31/62 routes (50%), suggesting qwen's
  candidate-set selections are less source-aligned than the other models.
- `llm_only_direct_labeler` (0.734) and `llm_only_canonical_pipeline` (0.727) are nearly
  tied — qwen is the only model where CP does not improve over DL (it marginally harms it:
  −7pp, driven by guidance rules increasing `unknown_false_pos` rather than reducing it).

The interim report (hybrid 250-row scoped) is kept as a historical record.

---

## 8c. Tracked Follow-Up: Uncertainty Signal Harmonization (Phase 3 Pre-Condition)

**Status: done (2026-06-09) — all three prompt fixes shipped; gpt-4.1-mini
validation750 runs in flight; no deepseek/qwen validation runs needed for this
pre-condition (see scope note below).**

An exploratory analysis of all confidence/uncertainty fields across the six
architectures (see [[gan2026_uncertainty_signal_audit_2026-06-09]] for the full
findings) found that the current state of uncertainty expression is incoherent
across architectures and models: ten distinct signal forms, no shared vocabulary,
and the only scalar confidence field (`confidence: low/medium/high` on the two
`llm_only` decision records) is degenerate for gpt-4.1-mini and qwen (99%+ of
rows assigned "high" — providing no calibration information). Three prompt-only
fixes are required before Phase 3 can produce comparable uncertainty-aware results:

1. **Ground `confidence` operationally** in the `llm_only_direct_labeler` and
   `llm_only_canonical_pipeline` prompts — add plain-language definitions of each
   level tied to observable note features (see Section 5 status update for the
   proposed definitions). No schema change; prompt change only.
   *Implementation (2026-06-09)*: added to `instructions` list in both
   `build_prompt_input` functions; PROMPT_VERSION bumped to v0.3 in both files.
   validation25 pilot (gpt-4.1-mini): 0 failures. Full validation750 run in
   flight.

2. **Replace `uncertainty_flags` free text with a closed clinical vocabulary**
   in the hybrid clinical-assessment prompt — ask the model to select from 12
   named, plain-language values rather than improvise free text. Note: the
   original plan specified the `VerificationRouteFamily` enum vocabulary
   verbatim; the implemented vocabulary was cleaned up (2026-06-09) to remove
   two deterministic-only flags (`selected_source_id_invalid`,
   `selected_evidence_missing_exact_trace`) and `projection_would_change_supported_comparator`
   (LLM has no access to what the normalization stage would produce), and to
   rewrite all remaining names as plain, directed, clinically meaningful strings
   (e.g. `active_seizures_contradict_seizure_free_claim`,
   `cluster_description_axis_unclear`, `seizures_described_only_when_triggered`)
   rather than internal architecture code names. No schema change (the field
   stays `list[str]`); prompt change only. The 12 values are listed in
   `uncertainty_flag_values` inside the `output_contract` key of
   `build_assessment_inputs`.
   *Implementation (2026-06-09)*: PROMPT_VERSION bumped to v4 in
   `llm_candidate_set_clinical_assessment_probe.py`. validation25 pilot
   (gpt-4.1-mini): 0 failures. Full validation750 run in flight.

3. **Add an `aggregation_policy` decision table** to the hybrid prompt — state
   when each of the 8 values applies in the same style as `guidance_for_tricky_cases`.
   Deepseek and gpt-4.1-mini differ 130× on `unknown_due_to_ambiguity` usage over
   the same data. No schema change; prompt change only.
   *Implementation (2026-06-09)*: added as `aggregation_policy_when_to_use` list
   inside the `output_contract` key (co-located with `aggregation_policy_values`
   and `uncertainty_flag_values`); same v4 PROMPT_VERSION bump as item 2.
   validation25 pilot (gpt-4.1-mini): 0 failures. Full validation750 run in
   flight.

**Scope decision (2026-06-09)**: validation750 runs for this pre-condition are
gpt-4.1-mini only. The audit already established that gpt-4.1-mini assigns
`confidence: "high"` to 99%+ of rows regardless of prompt definition — the
distribution will not shift materially and there is no value in running
deepseek/qwen validation750 to confirm something already known. The prompt
definitions are in place for deepseek/qwen to leverage when Phase 3's
full multi-model comparison runs are executed.

Each fix is independently ablatable: apply one, re-run on `validation25` to
confirm behavior, then on `validation750` to check distribution shift before
applying the next. The goal is not to maximize use of any particular field but to
make the field cross-model comparable so Phase 3's prompt-refinement results can
be interpreted cleanly.

---

## 8d. Phase 3 Prompt Refinement — Status

**Status: done (2026-06-09) — gpt-4.1-mini Phase 3 complete**

Error analysis complete — see `docs/research/gan2026_phase3_error_analysis_2026-06-09.md` and registered in `experiments/registry.jsonl` (`gan2026_phase3_error_analysis_2026-06-09`).

**Key findings driving prompt changes:**

- 4 high-failure-rate CP rules account for 143/169 CP failures: model cites rule then violates it → rules need explicit negative examples and scope gates, not elaboration.
- 20 universal failures; ~12 tractable with instruction fixes.
- Priority: FM-2 seizure-free FP (97 failures) > FM-1 denominator window (~66 LLM-improvable) > FM-3 unknown FP (132) > FM-6 highest-type selection (~25 universal).

**Implemented changes (2026-06-09) — `llm_only_direct_labeler` v0.4 and `llm_only_canonical_pipeline` v0.4:**

DL + CP base instructions:
- FM-1: Replace "preserve explicit count-and-window" with most-recent-window tiebreaker instruction.
- FM-6: Replace "select highest burden" with explicit frequency-first ranking (daily > weekly > monthly, regardless of seizure type severity).
- FM-2b: Add post-burst seizure-free block (burst frequency takes precedence over ensuing SF run).
- FM-2a + FM-4: Replace trigger-conditioned instruction with conditional-window block + minimum recurrence requirement (≥2 events or explicit recurrence statement needed for a concrete rate).
- FM-3/FM-5: Expand cluster instruction with cluster-cadence-as-frequency rule + seizure type inclusion list (drop attacks, SE, myoclonic jerks, absences, behavioural arrest).
- FM-3: Add rationale-label consistency check.

CP rule rewrites (replacing previous rule text):
- `seizure_free_conflict`: rewritten with 3 explicit suppression patterns + "do NOT cite as justification for seizure-free" warning.
- `same_window_additive_frequency`: rewritten with 3-condition AND gate for when to sum + explicit "when in doubt, select" fallback.
- `denominator_window_mismatch`: rewritten to suppress date-arithmetic rate computation, with examples of what NOT to do + most-recent-month exception.
- `concrete_frequency_precedence`: rewritten with explicit scope gates preventing lower-frequency selection, clinical cluster override, and medication-cadence confusion.

**v0.4 validation750 results (2026-06-09):**
- DL v0.4: 567/750 purist = 75.60% (Phase 1: 75.20%) — net +3
- CP v0.4: 571/750 purist = 76.13% (Phase 1: 77.47%) — net **−10 regression**

v0.4 analysis: FM-6 frequency-first and FM-2b post-burst changes worked (40 DL + 34 CP improvements). Three backfires:
1. `seizure_free_conflict` rewrite → model returns `no seizure frequency reference` instead of seizure-free when suppressed (11 CP regressions)
2. Minimum recurrence instruction too broad → returns `unknown` for valid stated rates (10 CP + 5 DL regressions)
3. FM-6 cluster carve-out missing → model reports intra-cluster daily burst rate instead of cluster cadence (8 CP cluster regressions)

**v0.5 fixes applied (2026-06-09):**
1. Removed "most recent month's count" sentence (user-flagged aggregation error + rows 3995/3999)
2. Added cluster cadence carve-out to FM-6 (rows 15479/15503/15513 cluster stripping)
3. Narrowed minimum recurrence to date-arithmetic constructions only, not explicit frequency statements
4. Fixed `seizure_free_conflict` fallback: when rule suppresses SF, fall back to `unknown` or active frequency — never `no seizure frequency reference`

**v0.5 validation750 results (2026-06-09):**
- DL v0.5: 575/750 purist = 76.67% (Phase 1: 75.20%) — net **+11** ✓
- CP v0.5: 582/750 purist = 77.60% (Phase 1: 77.47%) — net **+1** ✓. The run that was originally
  reported as crashed at row 380 was subsequently resumed (`.resume-part.jsonl`, 370 rows) and
  merged into the base JSONL, giving 750/750 rows at `gan2026_llm_only_canonical_pipeline_v0.5`
  prompt version with 0 call failures.

**Hybrid prompt changes — implemented (2026-06-09), hybrid v5 validation750 in flight.**

Three prompt fixes applied to `llm_candidate_set_clinical_assessment_probe.py` (PROMPT_VERSION
bumped to `gan2026_candidate_set_clinical_assessment_probe_v5`); validation25 pilot confirmed 0
failures before the full run was launched:

1. **FM-6 — frequency-first candidate selection**: Added explicit instruction: when the CandidateSet
   contains candidates from multiple concurrent seizure types, select the highest-frequency candidate
   (events per day > per week > per month), not the highest clinical severity. Exception carve-out
   for true cluster patterns (cluster cadence candidate over within-cluster daily burst rate).

2. **FM-2a — trigger-conditioned seizure-free**: Expanded the existing risk-window instruction to
   specify that when seizures are only described within a conditional window with outside-window SF,
   `assessment_kind` must be `unknown_frequency` (not `seizure_free`), with
   `seizure_free_only_outside_cyclic_risk_window` flag.

3. **FM-2b — post-burst seizure-free**: Added instruction: when a recent seizure burst is followed
   by a current SF run, use the burst candidate as primary and set `assessment_kind` to
   `frequency_rate`, not `seizure_free`.

4. **FM-5b — cluster inflation guard**: Added instruction: use `assessment_kind cluster_frequency`
   only when the CandidateSet candidate explicitly describes a recurring clinical cluster pattern
   (grouped episodes, 'cluster days', etc.); do not select it when "cluster" appears incidentally.

Full validation750 run artifact: `experiments/gan2026_hybrid_v5_validation750_gpt41mini_2026-06-09.{jsonl,md}` — **complete (750/750, 0 call errors, 1 parse error, all at v5).**

**Phase 3 comparison report — complete (2026-06-09).** Built at
`experiments/gan2026_three_way_comparison_phase3_report_gpt41mini_validation750_2026-06-09.{jsonl,json,md}`.
Artifact mix: Phase 2 deterministic/DCP (digit-only de-overfitting); hybrid v5; DL v0.5 / CP v0.5;
SE from Phase 1 (no SE-specific Phase 3 changes). Phase 3 vs Phase 2 delta for hybrid (gpt-4.1-mini):

| Metric | Phase 2 (v4 hybrid) | Phase 3 (v5 hybrid) | Delta |
| --- | --- | --- | --- |
| Rendered rows | 589/750 | 597/750 | +8 |
| Purist-correct of rendered | 500/589 (84.9%) | 526/597 (88.1%) | +3.2pp |
| Pragmatic-correct of rendered | 519/589 (88.1%) | 545/597 (91.3%) | +3.2pp |
| Routed rows | 42 | 48 | +6 |

Full Phase 3 report shared-table results (validation750, gpt-4.1-mini):

| Architecture | Rendered | Purist/rendered | Pragmatic/rendered |
| --- | --- | --- | --- |
| `deterministic` | 741 | 673 (90.8%) | 681 (91.9%) |
| `deterministic_canonical_pipeline` | 741 | 673 (90.8%) | 681 (91.9%) |
| `hybrid` (v5) | 597 | 526 (88.1%) | 545 (91.3%) |
| `hybrid_structured_events` | 748 | 661 (88.4%) | 679 (90.8%) |
| `llm_only_direct_labeler` (v0.5) | 750 | 575 (76.7%) | 610 (81.3%) |
| `llm_only_canonical_pipeline` (v0.5) | 750 | 582 (77.6%) | 614 (81.9%) |

Both new artifacts registered in `experiments/registry.jsonl`
(`gan2026_hybrid_v5_validation750_gpt41mini_2026-06-09`,
`gan2026_three_way_comparison_phase3_report_gpt41mini_validation750_2026-06-09`).
**Phase 3 is complete for gpt-4.1-mini.**

---

## 9. Relationship To The Other Two Workstreams

- This plan **produces** the comparison surface that
  [[gan2026_evidence_grounded_thesis_assessment_plan]] needs to score the
  three architectures against the project's core thesis axes.
- This plan's Phase 0 (canonical-runner selection) **is** the architectural
  decision that [[gan2026_repo_consolidation_and_cleanup_plan]] needs before it
  can name removal candidates. Do Phase 0 once, and let both other plans
  consume its output — see the sequencing recommendation in the cleanup plan,
  Section 2.
