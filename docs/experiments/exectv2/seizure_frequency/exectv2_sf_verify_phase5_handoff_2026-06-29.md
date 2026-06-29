# ExECTv2 SF Verify — Phase 5 implementation + audit handoff (2026-06-29)

**Audience:** a developer picking this up with fresh eyes.
**Branch:** `exectv2v2-gepa-single-model-plateau-2026-06-28`.
**Status:** all code changes below are in the **working tree, UNCOMMITTED**. The Phase 5
runs have **not** produced results yet — a full run was started and deliberately killed when
the audit (below) found bugs. Nothing has been re-smoked or run at scale since the audit fixes.

Read these first for context (do not re-derive):
- Plan: `docs/plans/exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md` (Phase 5 is §5; the
  execution history through Phase 3b is §6b/§6c).
- Error analysis that motivated Phase 5: `docs/experiments/exectv2/seizure_frequency/exectv2_sf_verify_error_analysis_2026-06-29.md`.
- Metric decision: `docs/decisions/0037-sf-state-profile-is-primary-clinical-metric.md`
  (**`state_profile` is the primary SF metric**, `clinical_headline` is change-blind/secondary).

---

## 1. What Phase 5 is trying to do

Push the **LLM-only** GEPA route on SeizureFrequency as far as possible **without** the
deterministic SF projection fallback (`sf_state_projection.py` / `rules/change.py`). Phase 3b
already reached 0.781 overall / 0.779 SF state_profile *with* that deterministic fallback; Phase 5
asks whether GEPA-evolved producers + a better feedback signal can get there on their own.

The lever is **feedback precision**, not more retrieval or more rules. The SF verify error
analysis decomposed the LLM-only plateau (P2 mini: 0.741 state_profile / 0.597 clinical_headline)
into four root causes:

| Cat | Share | Error |
| --- | ---: | --- |
| A | 28% | per-type multiplicity (gold tags one type with rate AND a separate qualitative change; model emits one) |
| B | 31% | over-emission on non-epileptic / unconfirmed events (confirmed-diagnosis gate not followed) |
| C | 20% | temporal confusion (a historical dated rate read as current seizure-free) |
| D | 11% | empty predictions (generation failures) |

**Gate (kill-criterion, from plan §5):** LLM-only SF `state_profile ≥ 0.80` AND
`clinical_headline SF ≥ 0.65` on dev140. The feedback lever is judged on beating the best
non-deterministic SF run (P2 mini **0.741** state_profile) by **≥ +0.03** (≈ 0.771). Phase 3b's
0.779/0.650 (WITH deterministic projection) is the comparison line, **not** the gate. Final eval
is full dev140; the frozen test split is untouched.

---

## 2. The architecture you are working inside

**Program** (`gepa/program_sf_verify.py`, `SfVerifyExtractor`): a focused SeizureFrequency-only
two-stage DSPy program.
- **S0 generate** (`SeizureFrequencyGenerateSignature`): letter → structured `events_json`.
- **S1 verify** (`SeizureFrequencyVerifySignature`): letter + draft events → completed/corrected
  `events_json` (recall-additive: ADD missed facts, remove only unsupported; do not merely prune).
- `forward` runs S0→S1, maps events → ExECTv2 SF clinical-facts via `events_to_sf_facts`, and emits
  `clinical_facts_json` so the existing dedup parser/adapter/scorers are reused unchanged.
- GEPA evolves BOTH instructions jointly (its `build_program` deepcopies the student and mutates
  only `signature.instructions` — so per-stage LMs and demos are preserved through optimization).

**The event schema** (`EVENT_SCHEMA`, after the audit): each event has `applies_to`, `kind ∈
{frequency_rate, cluster_frequency, seizure_free, changed}`, `evidence`.

**The state round-trip (verified correct):**
`kind` → `KIND_TO_STATE` → fact `state` → `_seizure_state_attributes` (facts.py) → ExectAnnotation
attributes → `frequency_state_faithful` → state. Concretely:
- `frequency_rate` / `cluster_frequency` → `active_rate` → `{NumberOfSeizures: "1"}` → `active-rate`
- `seizure_free` → `{NumberOfSeizures: "0"}` → `seizure-free`
- `changed` → `{FrequencyChange: "Same"}` → `changed` (faithful treats ANY FrequencyChange as changed)

**The metric** (`build_sf_verify_metric`): scores SF `state_profile` F-beta (recall_beta=1 ⇒ F1)
minus a length penalty. **Critically, `state_profile` is TYPE-AGNOSTIC** — it scores the per-letter
*set* of the 4 states (`seizure-free / active-rate / changed / unknown`), ignoring the seizure type
and per-type multiplicity. This is the single most important fact about the system and the source of
the worst bug below. The feedback is the per-(seizure_type, state) diff with category-specific
reasons (Phase 5's lever).

---

## 3. What I built (Phase 5 infrastructure)

1. **Feedback redesign** in `build_sf_verify_metric` — moved from letter-level de-duplicated state
   sets to **per-(seizure_type, state)** keyed facts, with a reason attached per error category
   (Cat A multiplicity + the FC=Same false-change boundary; Cat B over-emission gated on epilepsy
   diagnosis status; Cat C temporal). Scoring is unchanged so any lift is attributable to feedback.
2. **Per-stage LMs + demos** in `SfVerifyExtractor` — `generate_lm` / `verify_lm` (e.g. reasoner
   extractor + gpt-4.1-mini verifier) and `generate_demos` / `verify_demos`. Verified both survive
   GEPA `build_program` (deepcopy + instruction-only mutation).
3. **Hand-curated demos** (`gepa/sf_verify_demos.py`) — 4 compact illustrative examples (one per
   convention), attached to BOTH stages. Generate demos show correct extraction; verify demos show
   the recall-additive correction.
4. **Parametrized launcher** (`experiments/gepa_sf_verify_phase5_exectv2.py`):
   `--extraction-model` / `--verify-model` / `--with-examples`, `change_precision_weight=0.0`
   (feedback-only), minibatch=8, 1000 metric calls, final eval on full dev140.
5. **Overnight orchestrator** (`experiments/run_sf_verify_phase5_matrix.ps1`) — runs the 4-run
   matrix sequentially (feedback-only first), `-Smoke` flag for a tiny wiring check.

### The 4-run matrix (decision 2026-06-29: extraction = deepseek-reasoner for all four)

| run-id (suffix `_20260629`) | extraction | verify | examples |
| --- | --- | --- | --- |
| `…p5_reasoner_reasoner_fb` | deepseek-reasoner | deepseek-reasoner | no |
| `…p5_reasoner_mini_fb` | deepseek-reasoner | gpt-4.1-mini | no |
| `…p5_reasoner_reasoner_ex` | deepseek-reasoner | deepseek-reasoner | yes |
| `…p5_reasoner_mini_ex` | deepseek-reasoner | gpt-4.1-mini | yes |

Reflection LM is `deepseek/deepseek-reasoner` for all four. (This differs from the plan's original
A0/A2 which used deepseek-chat extraction; A0 chat/chat was dropped because H-model already refuted
chat as a keyer — see plan §6b.)

---

## 4. The audit (why the first full run was killed)

After a clean smoke (all 4 arms exit 0, wiring validated), a deeper review found the feedback had
grown **type-aware** while the metric stayed **type-agnostic**, plus schema drift. Findings:

### Correctness bugs — FIXED

1. **Cat-B diagnosis contradiction.** "no confirmed epilepsy diagnosis" was emitted on letters that
   *did* state a probable / `?`-qualified epilepsy diagnosis (gold convention excludes SF for those,
   but the letter clearly says "epilepsy"). The reasoner spent huge reasoning traces trying to
   reconcile the contradiction. **Fix:** `_epilepsy_dx_status` returns `confirmed` (definite,
   Certainty 5, affirmed, epilepsy category) / `uncertain` (epilepsy dx but not definite) / `absent`;
   the Cat-B reason is chosen accordingly and is no longer self-contradictory.

2. **Per-type feedback vs type-agnostic scoring — the serious one.** Cat A multiplicity, Cat A FP,
   and Cat B over-emission compared *per seizure type*, but `state_profile` scores only the per-letter
   *set of states*. Demonstrated: a prediction scoring **`state_profile P=1.00` (a true positive)**
   was told *"OVER-EMISSION … only count seizures from the confirmed diagnosis"* — i.e. the feedback
   instructed the model to DELETE a correct fact, purely because it emitted generic `seizures` where
   gold used a specific type. (GEPA's valset score-gating prevents this from corrupting the *final*
   selected program, but it wastes the optimization budget on misleading proposals and caused the
   reasoning spiral.) **Fix:** every per-type callout is now gated on the letter-level `missed` /
   `spurious` state sets — the only thing the type-agnostic score actually penalizes:
   - Cat A multiplicity: only "ADD" states that are in `missed`.
   - Cat A FP: only fire when `changed` is in `spurious` (no gold type has changed).
   - Cat B over-emission: only flag pred types absent from gold that carry a state in `spurious`.

### Redundancy / incoherence — FIXED

3. **`change_direction` was dead** — present in schema + seed + every demo, but `events_to_sf_facts`
   never reads it. Removed everywhere.
4. **`unknown` is always wrong** — gold has **zero** unknown states (dev distribution: active-rate
   118 / seizure-free 93 / changed 52 / unknown 0). The schema offered it and the seed instructed it,
   so any `unknown` was a guaranteed precision hit. Removed from the schema enum + seed (kept a
   `KIND_TO_STATE` fallback for robustness); the seed now says "no usable signal → don't emit."
5. **`clinical_headline` leaked into per-example feedback** — we optimize `state_profile`, but the
   feedback printed `clinical_headline F1`, producing contradictions like "CORRECT … clinical_headline
   F1=0.000." Removed from feedback (still in the run summary JSON).
6. **Cat-A-FP wording overbroad** — gold genuinely contains `FrequencyChange="Same"` scored as
   `changed` (6×), so "FC=Same is NOT a changed fact" was wrong as stated. Softened to "not a
   *separate* changed fact when that type already has a rate," and now only fires when `changed` is
   actually spurious.

### Flagged, deliberately LEFT AS-IS (decisions for fresh eyes)

7. **`cluster_frequency` ≡ `frequency_rate`** — both project to `active-rate`, so the distinction is
   invisible to scoring. Kept (clinically real, harmless). Could merge to simplify the schema.
8. **Phase-4 leftovers unused by these 4 runs** — `VERIFY_SEED_V2`, `build_sf_verify_program_v2`,
   `change_precision_weight` (=0 here, scoring branch inert), `recall_beta` (=1). Kept because older
   launchers (`gepa_sf_verify_exectv2.py`, `gepa_sf_verify_v2_deepseek_exectv2.py`) reference them.
9. **`facts.py` maps every model `changed` → `FrequencyChange="Same"`** (loses direction, odd label).
   Scoring-neutral (faithful treats any FC as `changed`) and shared infra used by other tasks, so not
   touched. If you ever want direction-aware SF scoring this is where to start.

---

## 5. Verification status

- 8/8 unit tests pass: `tests/test_exectv2_gepa_sf_verify.py` (added uncertain-dx, multiplicity, and
  over-emission coverage).
- Consolidated real-letter behavior check (zero-LLM) confirms: generic-`seizures` TP no longer
  flagged for deletion; multiplicity / genuine over-emission / FC=Same / clean-CORRECT all behave; no
  `clinical_headline` leakage.
- **NOT yet done:** re-smoke after the audit fixes (schema/seed/demos changed = the model sees a
  different prompt), and the full run. The original smoke numbers are noise (12 letters, 20 calls) —
  ignore them.

---

## 6. Exactly how to continue

1. **Re-smoke** (tiny API cost, ~10 min — validates the simplified schema end-to-end on live models):
   ```powershell
   pwsh experiments/run_sf_verify_phase5_matrix.ps1 -Smoke
   ```
   Confirm all four arms reach the `OPT …` line. Skim the GEPA-proposed instructions in the logs —
   they should no longer contain the over-emission contradiction spiral.

2. **Full run:**
   ```powershell
   pwsh experiments/run_sf_verify_phase5_matrix.ps1
   ```
   ~3–5 hours (reasoner extraction is the slow part). Outputs:
   `experiments/exectv2_gepa_sf_verify_p5_*.json` (summary), `.jsonl` (preds), `.instruction.txt`
   (evolved prompt). The orchestrator prints the gate line per arm.

3. **Read the four results against the gate** (§1) and write the durable experiment doc; decide
   whether the feedback lever (fb arms) cleared +0.03 over 0.741, whether examples helped (ex arms),
   and reasoner-verify vs mini-verify.

Notes:
- `.env` must have `DEEPSEEK_API_KEY` and `OPENAI_API_KEY` (both verified present 2026-06-29).
- Use `uv run …` (project convention).
- Registry registration is still skipped by the malformed `experiments/registry.jsonl:63` (artifacts
  are written regardless) — fix line 63 to re-enable, as for prior arms.

---

## 7. Key files

| File | Role |
| --- | --- |
| `src/.../exectv2/gepa/program_sf_verify.py` | program, schema, seeds, `events_to_sf_facts`, `build_sf_verify_metric` (the feedback), `_states_by_type` / `_epilepsy_dx_status` helpers |
| `src/.../exectv2/gepa/sf_verify_demos.py` | hand-curated H-examples demos (4 conventions, both stages) |
| `experiments/gepa_sf_verify_phase5_exectv2.py` | parametrized launcher |
| `experiments/run_sf_verify_phase5_matrix.ps1` | overnight orchestrator (4 runs; `-Smoke`) |
| `tests/test_exectv2_gepa_sf_verify.py` | unit tests (8) |
| `src/.../exectv2/scoring/seizure_frequency.py` | `state_profile` (type-agnostic) + `frequency_state_faithful` |
| `src/.../llm/pipelines/key_entities_generation_selection/facts.py` | `_seizure_state_attributes` (state→attribute projection, finding #9) |

---

## 8. Open questions for fresh eyes

- **Is type-agnostic `state_profile` the right teaching target for a type-aware producer?** The whole
  feedback-vs-metric tension (finding #2) comes from this. ADR 0037 chose `state_profile` to avoid the
  CUI-granularity lottery in `clinical_headline`. The per-type feedback is now a *diagnostic overlay*
  that must never contradict the type-agnostic score — verify any future feedback edit preserves that.
- **Cat A multiplicity is the dominant error (28%) and the hardest.** The error analysis judged it
  partly a genuinely ambiguous convention (FC=Infrequent is a separate fact from a rate; FC=Same is
  not). Watch whether the redesigned feedback + demos actually move it, or whether it needs the
  deterministic projection (the explicit Phase 5 scope boundary: this work does NOT touch
  `sf_state_projection.py` / `rules/change.py`).
- **Schema minimalism vs. model guidance** (findings #7, #4): is dropping `unknown` net-positive, or
  does the model need an explicit "no SF here" escape hatch? The current bet is "don't emit" is the
  precision-correct behavior since gold never has `unknown`.
