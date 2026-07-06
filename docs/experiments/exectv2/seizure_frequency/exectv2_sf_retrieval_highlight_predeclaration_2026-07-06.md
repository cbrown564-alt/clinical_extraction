# Predeclaration — SF retrieval-highlight salience priming (item 3, dev140)

Date: 2026-07-06. Owner: ExECTv2 workstream.
Hypothesis: `sf_retrieval_highlight_priming_2026-07-06` (PENDING).
Driver: `scripts/run_exectv2_sf_retrieval_highlight_probe.py --cache`.
Prior art: `sf_direction_extraction_probe_2026-07-03` (registry entry 31, the B1
post-hoc free-write adjudicator this probe's Arm A reproduces as the within-run
control) and `sf_closed_option_direction_selector_2026-07-06` (registry entry 32,
item 2, the generation-contract leg that REFUTED "fundamental" — this is the
orthogonal input leg).
Umbrella plan: item 3 of `docs/plans/predecessor_synthesis_followups_2026-07-06.md`.

## Purpose (the orthogonal second leg of the cross-family bet)

The SF-direction capacity-vs-execution gap was bounded by **four measured
negatives, all in the free-write-then-arbitrate architecture family** (B2
hard-emission −0.0775 dev140 / −0.0483 full-200, B2 `state_profile` regression
−0.1548, three-family Phase-0 degeneracy). Item 2 (registry entry 32, the
closed-option selector) tested the **generation-contract** axis and REFUTED
"fundamental" (+0.0552): the gap does not survive a change of *contract*.

**This experiment tests the orthogonal axis: the *input*.** Every decoupling
mechanism we tested for the SF-direction gap restructured the *call* (B2 coupled,
per-key decoupled, per-letter B1). Item 2 restructured the *generation contract*
(closed-option select-or-abstain). **None restructured the *input*.** This probe
primes the input with deterministic direction-relevant spans *before* the coupled
extraction call. If the gap is specifically about *coupling cognitive load*,
priming the relevant spans first could deploy the capacity that call-restructuring
and contract-constraining deploy from the other axes.

The motivating predecessor finding is dissertation-recursive's Gan winner:
`gpt_5_5 + Gan_retrieval_highlight` scored Pragmatic µF1 0.840 vs 0.760 for
`cot_label`. The decisive evidence is the ablation:
`Gan_retrieval_only_ablation` (spans only, no full letter) scored 0.520 vs 0.840
for highlight — a **−32pp drop proving retrieval works by salience-priming the
input, not by direct lookup.** This probe transfers that mechanism test to the
ExECTv2 SF direction surface.

Two predeclared outcomes (each moves the manuscript):

- **Input-scaffolding deploys capacity:** Arm B (full letter + highlights)
  recovers direction ≥ +0.05 dev140 `state_profile_directional` vs Arm A
  (baseline, within-run). The gap was partly about input salience, not a
  fundamental capacity limit — corroborating item 2's refute along the orthogonal
  input axis.
- **Highlight is not the lever for ExECTv2 direction:** Arm B − Arm A < +0.02.
  The Gan finding does not transfer to this surface; the gap survived an input
  change even though it did not survive a contract change (item 2). This
  strengthens "fundamental" along a *different axis* than item 2: input-robust
  even if contract-sensitive.

## Framing absorbed from prerequisite audits (items 6 & 7)

Same two audits that framed item 2 frame item 3 identically, because item 3 runs
on the same raw surface against the same baseline:

- **Item 6 (`docs/research/gan_multiple_sentinel_audit_2026-07.md`):** our Gan
  numbers are **not directly comparable** to dissertation-recursive's 0.840 /
  0.520 (different scoring convention). **Therefore the cross-family claim here
  is stated in within-architecture-delta terms (Arm B − Arm A within this run),
  not in terms of matching dissertation-recursive's absolute rates.** The 0.840 /
  0.520 / −32pp numbers are cited only as the *architectural principle*
  (retrieval-by-priming) being transferred, and as the *mechanism* the Arm C
  ablation replicates.
- **Item 7 (`docs/research/exectv2_gepa_policy_wall_audit_2026-07.md`):** like
  item 2, this probe runs on the **raw SF-verify program**
  (`exectv2_gepa_sf_verify_gpt41mini_20260628.jsonl`), not the policy-walled GEPA
  surface. So the input-priming test is uncontaminated by the GEPA overfit
  confound.

## Vocabulary reconciliation (frozen)

Identical to item 2. The real closed vocab everywhere in this codebase — gold
annotations, the `FrequencyChange` attribute, the `frequency_state_directional`
scorer, and `rules/change.py` — is `{Decreased, Frequent, Increased, Infrequent,
Same}`. The adjudicator free-writes exactly one of these five labels per changed
mention (matching B1's `DirectionAdjudicationSignature` output contract verbatim
— the family-under-test difference is the *input*, so the *output* contract is
held fixed to keep attribution clean). "Same" is the directional-neutral default
when the letter states no direction.

## Frozen contract

| Field | Value |
| --- | --- |
| Program | New `HighlightDirectionAdjudicator` dspy signature — no GEPA evolution, hand-written to keep attribution clean. **Free-writes a label like B1** (this is NOT a closed-option selector — that is item 2; the two items are independent levers and must not be conflated). |
| Input artifact | `experiments/exectv2_gepa_sf_verify_gpt41mini_20260628.jsonl` (the raw SF-verify program, unchanged — identical to item 2 / B1) |
| Disagreement set | Derived at runtime: letters with ≥1 `frequency_state_faithful == "changed"` SeizureFrequency mention (35 mentions across 28 letters; ~30 gold-directional) — identical to B1's / item 2's loader |
| Span source | `deterministic/sf_surface_registry/adapters/extraction.py` → `CHANGE_RULES` (5 rules) + `TEMPORAL_RULES` (13 rules), applied via `RuleSpec.apply(ExtractionContext(text), DEFAULT_ABLATION)` → `AttributeExtraction.span=(start,end)` char offsets + `.evidence` text + `.attributes["FrequencyChange"]` (where present) |
| Highlight markers | Selected spans wrapped in the raw `note_text` with `[[HL]]...[[/HL]]` (the markers named in the umbrella plan), inserted right-to-left by char offset to preserve indices |
| Model | `openai/gpt-4.1-mini` |
| Temperature | 0.0 (matches B1/B2/item 2) |
| max_tokens | 8000 |
| Cache | on (`--cache`) |
| Split | dev140 only (gap is two-split confirmed; test59 frozen) |
| Call count | **~84** (Arm A 28 + Arm B 28 + Arm C 28; one adjudicator call per letter with ≥1 changed mention per arm) |
| Scorer | `score_frequency_state` → `state_profile_directional` (primary), `state_profile` (regression check) — unchanged, reused from B1 / item 2 |
| Row inspection | dev140 only (changed-mention letters); no test59 / full-200 row inspection |

## Driver design (mirrors item 2 / B1, with the three arms as the design under test)

All three arms share the **same adjudicator signature** and the **same
disagreement set**. The only difference across arms is the `letter_text` field
fed to the LLM — this isolates the *input* lever:

1. **Deterministic span selection (new code).** Per changed-mention letter, run
   `CHANGE_RULES` + `TEMPORAL_RULES` via `RuleSpec.apply()` against the letter
   text. Collect `(start, end, evidence, rule_id)` tuples. Dedup overlapping
   spans deterministically (keep earliest start; an enclosing span wins over a
   later-overlapping one). This is the retrieval bank; it is sourced from
   deterministic rules, NOT from the LLM. (This is the ExECTv2 analogue of
   dissertation-recursive's `retrieve_frequency_spans()` over its
   `_FREQUENCY_SENTENCE_PATTERNS` regex bank.)

2. **Highlight direction adjudicator (mirrors B1's free-write contract).** A
   dspy signature `HighlightDirectionAdjudicator` that, per letter, reads the
   (possibly highlighted) `letter_text` + the list of changed mentions + an
   `instruction`, and free-writes a 5-way direction per mention — the **same
   output contract as B1's `DirectionAdjudicationSignature`**. The instruction
   field carries the per-arm weigh-the-highlights guidance (neutral for Arm A;
   "highlighted spans are the clinically relevant direction cues; weigh them"
   for Arms B/C). This is NOT a closed-option selector.

3. **Three arms (the design under test).**
   - **Arm A (baseline, control):** raw `letter_text` unchanged + neutral
     instruction. Exact reproduction of B1's free-write adjudicator. Anchors the
     within-run delta; expected to reproduce ~B1 (0.7254, +12 tp). If it does
     not, the run is a contract failure (see outcomes table).
   - **Arm B (highlight):** `letter_text` with the deterministic spans wrapped
     in `[[HL]]...[[/HL]]` + the weigh-the-highlights instruction. Full letter +
     highlights. The dissertation-recursive highlight condition.
   - **Arm C (highlight-only ablation):** `letter_text` = only the highlighted
     span `evidence` texts (concatenated, no surrounding letter context) + the
     weigh-the-highlights instruction. The dissertation-recursive ablation whose
     −32pp drop proved priming-vs-lookup.

4. **Apply-then-rescore (reused verbatim from item 2 / B1).** For each arm, apply
   the adjudicated directions to a copy of the raw SF-verify artifact (same
   per-mention-index application as item 2 `:359-374`), carry all 140 letters
   through, re-score via `score_frequency_state`, write a per-arm pred-JSONL +
   summary JSON, plus one combined per-mention ledger.

Reused unchanged from item 2 / B1: `_letters_with_changed_mentions`
(disagreement-set loader), `_pred_letters_from_raw`, `_raw_row_by_id`,
`build_dspy_lm`, the baseline-reproduce-then-rescore pattern, the
`dspy.Parallel` evaluator, the carry-all-140-letters-through pattern.

## Predeclared outcomes

Target metric = `state_profile_directional`. Arm A is the within-run control; the
reference numbers from B1/item 2 are raw baseline **0.6552** (tp=95) and B1
post-hoc free-write **0.7254** (tp=107). Arm A must reproduce ~B1 for the run to
be valid.

| Outcome | Verdict | Action |
| --- | --- | --- |
| Arm B − Arm A ≥ **+0.05** dev140 `state_profile_directional`, no `state_profile` regression | **INPUT-SCAFFOLDING DEPLOYS CAPACITY** — gap partly about input salience, not fundamental; corroborates item 2's refute along the orthogonal input axis | Second cross-family refute (input lever); manuscript states the gap does not survive a change of input *or* contract |
| Arm B − Arm A **< +0.02** | **HIGHLIGHT IS NOT THE LEVER for ExECTv2 direction** (Gan finding does not transfer); gap survived an input change | Report as the diversifying negative; "free-write-family-specific under contract change (item 2), but input-robust (item 3)" |
| Arm B − Arm A **+0.02 to +0.05** | **INCONCLUSIVE** — partial priming effect, not cleanly above or below the thresholds | Report as ambiguous; do not claim either direction |
| Arm A regresses `state_profile` vs raw, or Arm A `state_profile_directional` ≪ B1 0.7254 (e.g. < 0.68) | **CONTRACT FAILURE** — baseline did not reproduce B1; the run is not a valid test of B/C | Stop; do not interpret B/C; document and re-run after fixing the baseline reproduction |
| Arm C ≈ Arm B (within ~0.05) | Retrieval works by **direct lookup** here (different mechanism than Gan) | Report as a cross-surface mechanism difference |
| Arm C ≪ Arm B (≥ ~0.10 below) | Retrieval works by **priming** — replicates dissertation-recursive's −32pp mechanism result on a different surface | Corroborating mechanism finding; the highlight works by salience-priming, not lookup |

The **kill criterion** is the **Arm B − Arm A < +0.02** band: if highlighting the
direction-relevant spans does not move `state_profile_directional`, the input-
priming lever does not deploy capacity on the ExECTv2 SF direction surface and
the experiment is reported as a strengthening negative along the input axis.

## Cost & isolation

- ~84 gpt-4.1-mini calls (one adjudicator call per changed-mention letter per
  arm; 28 letters × 3 arms), temp 0, cached. Same model/temp as item 2 / B1.
- Same-day Arm A baseline reproduced in-run as the control (identical to B1's
  post-hoc free-write contract), so the Arm B − Arm A delta is isolated from
  scorer drift and from cross-run model variance.
- dev140 only; no test59 / full-200 row inspection.

## What this is NOT

- Not a closed-option selector (that is item 2). The adjudicator free-writes a
  direction label; the lever under test is the *input*, not the *generation
  contract*. The two items are independent orthogonal levers on the same null
  hypothesis.
- Not a test of dissertation-recursive's absolute 0.840 / 0.520 rates (item 6
  showed those are on a different scoring convention). Cited only as the
  architectural principle (retrieval-by-priming) and the mechanism the Arm C
  ablation replicates.
- Not a test on the policy-walled GEPA surface (item 7 showed that surface is
  overfit; this runs on the raw program, same as item 2).
- Not a re-run of item 2 with a different menu. There is no menu — the
  deterministic layer produces *spans*, not *options*, and the LLM free-writes
  over the full letter (or the highlighted spans in Arm C).
