# Predeclaration — SF closed-option direction selector (item 2, dev140)

Date: 2026-07-06. Owner: ExECTv2 workstream.
Hypothesis: `sf_closed_option_direction_selector_2026-07-06` (PENDING).
Driver: `scripts/run_exectv2_sf_closed_option_direction_probe.py --cache`.
Prior art: `sf_direction_extraction_probe_2026-07-03` (registry entry 31,
REFUTED at hard-emission −0.0775) — the free-write-family negative this test
crosses into a second architecture family.
Umbrella plan: item 2 of `docs/plans/predecessor_synthesis_followups_2026-07-06.md`.

## Purpose (the cross-family test)

Our SF-direction capacity-vs-execution gap is currently bounded by **four
measured negatives, all in the free-write-then-arbitrate architecture family**:

1. B2 hard-emission: −0.0775 `state_profile_directional` (dev140).
2. B2 hard-emission: −0.0483 `state_profile_directional` (full-200).
3. B2 `state_profile` regression −0.1548 (dev140) — the direction field's
   cognitive load degrades the other SF axes.
4. The three-family Phase-0 degeneracy (adding a direction field regresses all
   of Dx/SF/Inv).

The per-key CORRECT/WRONG adjudicator in B1 is **not** a closed-option selector
— it is a keep/drop *judge* over *free-written* tokens. Every measured negative
so far lives in the free-write family.

**This experiment tests the gap in a different architecture family**: a
closed-option selector where the LLM **never free-writes a direction**; it
picks a `candidate_id` verbatim from a deterministic candidate menu, or
abstains. This is the dspy G32 principle (the LLM picks a label from a
deterministic menu or abstains to a special label — never free-writes a rate),
transferred to the ExECTv2 SF direction surface.

Two predeclared outcomes (each moves the manuscript):

- **Refutes "fundamental":** the closed-option selector recovers direction at
  ≥ +0.05 dev140 `state_profile_directional` vs the raw 0.6552 baseline. The
  gap was an artifact of the free-write generation contract, not a capacity
  limit. This is the dspy outcome and a major positive finding.
- **Confirms "fundamental across families":** recovery < +0.02. This becomes
  the **fifth** negative, from a *different architecture family*, promoting the
  "fundamental" claim from "4 negatives in one family" to "5 negatives across
  two families" — dramatically stronger for the manuscript.

## Framing absorbed from prerequisite audits (items 6 & 7)

This predeclaration froze *after* the two prerequisite audits landed:

- **Item 6 (`docs/research/gan_multiple_sentinel_audit_2026-07.md`):** our Gan
  numbers are **not directly comparable** to dspy's 90.3% monthly — our scorer
  sends bare `multiple per <period>` to the unknown bin while both predecessors
  count it (a ~5pp Purist / ~4.8pp Pragmatic convention difference; the 2-vs-3
  axis is negligible at <0.3pp). **Therefore the cross-family claim here is
  stated in terms of our own within-architecture deltas (raw 0.6552 → closed-
  option), not in terms of matching dspy's absolute rate.** dspy G32 is cited
  only as the *architectural principle* (closed-option generation) being
  transferred, not as a comparable accuracy target.
- **Item 7 (`docs/research/exectv2_gepa_policy_wall_audit_2026-07.md`):** two
  evolved GEPA seeds (18,638 / 16,119 chars) clear dspy's 14,639-char policy
  wall and exhibit the overfit-cue signature. **Crucially, item 2 does not run
  on the policy-walled surface** — it runs on the *raw SF-verify* program
  (`exectv2_gepa_sf_verify_gpt41mini_20260628.jsonl`), whose four measured
  negatives motivate the experiment, and which uses no evolved seed. So the
  four negatives are not artifacts of the GEPA policy wall; they are properties
  of the un-evolved raw surface. Item 2 is therefore a **clean** test of the
  generation contract, uncontaminated by the GEPA overfit confound. If the
  closed-option contract also fails here, the "fundamental" claim is
  strengthened *despite* (not because of) the policy-wall finding — it would
  show the gap survives a contract change on a surface that is not itself
  overfit.

## Vocabulary reconciliation (frozen)

The umbrella plan names the candidate menu
`{Increasing, Decreasing, Stable, Same, None}`. **The actual closed vocab
everywhere in this codebase — gold annotations, the `FrequencyChange`
attribute, the `frequency_state_directional` scorer, and `rules/change.py`
(line 3) — is `{Decreased, Frequent, Increased, Infrequent, Same}`.** This
predeclaration freezes on the **real 5-value vocab**. The LLM's candidate menu
contains exactly these five labels (as `candidate_id`s) plus an `ABSTAIN`
option. A selector that abstains maps deterministically to `Same` — the
directional-neutral bucket — so abstention is not silent: it is a visible
`Same`-default with provenance `abstain`.

## Frozen contract

| Field | Value |
| --- | --- |
| Program | New `ClosedOptionDirectionSelector` dspy signature (see Driver §1-3) — no GEPA evolution, hand-written to keep attribution clean |
| Input artifact | `experiments/exectv2_gepa_sf_verify_gpt41mini_20260628.jsonl` (the raw SF-verify program, unchanged) |
| Disagreement set | Derived at runtime: letters with ≥1 `frequency_state_faithful == "changed"` SeizureFrequency mention (35 mentions across 28 letters; ~30 gold-directional) — identical to B1's loader |
| Candidate menu source | `deterministic/rules/change.py` `CHANGE_EXTRACT_IMPLS` regex matches against the letter text — deterministic; the menu lists only direction cues the regexes actually find, plus `ABSTAIN` |
| Model | `openai/gpt-4.1-mini` |
| Temperature | 0.0 (matches B1/B2) |
| max_tokens | 8000 |
| Cache | on (`--cache`) |
| Split | dev140 only (gap is two-split confirmed; test59 frozen) |
| Call count | **~28** (one selector call per letter with ≥1 changed mention; 28 letters). Upper bound ~56 if a second pass is needed. |
| Scorer | `score_frequency_state` → `state_profile_directional` (primary), `state_profile` (regression check) — unchanged, reused from B1 |
| Row inspection | dev140 only (changed-mention letters); no test59 / full-200 row inspection |

## Driver design (mirrors B1 `run_b1`, `scripts/run_exectv2_sf_direction_probe.py:221-309`, with three architectural differences that define the cross-family test)

1. **Deterministic candidate menu builder (new code).** Per changed-mention
   letter, run `rules/change.py`'s `CHANGE_EXTRACT_IMPLS` (the five direction
   regexes) against the letter text. Emit a candidate menu:
   `{candidate_id: "C0", label: "Increased", evidence_span: "seizure frequency has increased"}`,
   one per matched direction cue, plus `ABSTAIN`. **The menu lists only labels
   the deterministic layer has evidence for** — this is the closed-option
   contract. (Mirrors gan2026 `CandidateSet` + the closed-list-enumeration
   prompt pattern from `assessment_probe_signature.py:255-269`.)

2. **Abstention-validated selector contract (the key difference from B1).** A
   dspy signature `ClosedOptionDirectionSelector` returning
   `selected_candidate_id` + `selection_mode ∈ {single_candidate,
   no_reliable_candidate, ambiguous}`, with a validator (mirroring gan2026
   `selected_fact.py:32-49`) that **forbids** a selected id when mode is a
   defer mode. Prompt constraint verbatim: *"Return a `candidate_id` that
   appears in the menu, or `ABSTAIN`. Never invent, renumber, or free-write a
   direction label."* **B1's `DirectionAdjudicator` had no such constraint** —
   it free-wrote a label then normalized. That is the family difference under
   test.

3. **Deterministic assembly (mirrors gan2026 `assemble_clinical_assessment`).**
   Map the selected `candidate_id` → `FrequencyChange` label, or → `Same` on
   abstain/invalid. Apply to a copy of the raw SF-verify artifact exactly as
   B1 does (`:257-296`), carry all 140 letters through, re-score via
   `score_frequency_state`.

Reused unchanged from B1: `_letters_with_changed_mentions` (disagreement-set
loader, `:173`), `_pred_letters_from_raw` (`:195`), `build_dspy_lm`
(`gan2026/llm_config.py`).

## Predeclared outcomes

Target metric = `state_profile_directional`. Reference numbers (all from the
B1/B2 results doc and the free-replay): raw baseline **0.6552** (tp=95 fp=55
fn=45); B1 post-hoc free-write **0.7254** (+12/30 recovered); B2 hard-emission
**0.5892** (−0.0775); v08 hybrid production **0.8897**.

| Outcome | Verdict | Action |
| --- | --- | --- |
| Closed-option recovers ≥ **+0.05** dev140 `state_profile_directional` vs raw 0.6552 (i.e. ≥ 0.7052), with no `state_profile` regression | **REFUTES "fundamental"** — the gap was a free-write-contract artifact; the closed-option family recovers direction where the free-write family could not | Major positive finding; report as the dspy-G32 outcome transferring to ExECTv2; the "fundamental" claim is downgraded to "free-write-family-specific" |
| Closed-option recovers **< +0.02** (i.e. < 0.6752) | **CONFIRMS "fundamental across families"** — the fifth negative, from a different architecture family | Promote "fundamental" from 4-negatives-one-family to 5-negatives-two-families; strengthen the manuscript's core thesis |
| Closed-option recovers **+0.02 to +0.05** (0.6752–0.7052) | **INCONCLUSIVE** — partial recovery, not cleanly above or below the thresholds | Run the per-key closed-option analogue; report as ambiguous, do not claim either direction |
| `state_profile` regresses | **CONTRACT FAILURE** — the closed-option selector harmed the direction-blind metric | Document; the menu construction is interfering with the underlying extraction |

The kill criterion is the **< +0.02** band: if the closed-option selector
fails to recover meaningful direction, the experiment confirms the gap across
two families and is reported as a strengthening negative.

## Cost & isolation

- ~28 gpt-4.1-mini calls (one selector call per changed-mention letter), temp 0,
  cached. Upper bound ~56.
- Same-day baseline (raw 0.6552) reproduced in-run as the pre-selector sanity
  check (identical to B1's baseline step), so the delta is isolated from
  scorer drift.
- dev140 only; no test59 / full-200 row inspection.

## What this is NOT

- Not a closed-option selector wired into gan2026's `CandidateSet` substrate
  (per the plan's open-question #1: standalone probe first; substrate
  integration is a follow-up only if this works).
- Not a test of dspy's absolute 90.3% rate (item 6 showed that number is on a
  different scoring convention).
- Not a test on the policy-walled GEPA surface (item 7 showed that surface is
  overfit; this runs on the raw program).
- Not conflated with item 3 (retrieval-highlight priming) — item 3 changes the
  *input*; this changes the *generation contract*. The two are independent
  levers on the same null hypothesis.
