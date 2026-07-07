# Predeclaration — SF closed-option direction selector, hybrid-lane integration (item 2 follow-up, dev140)

Date: 2026-07-06. Owner: ExECTv2 workstream.
Hypothesis: `sf_closed_option_hybrid_integration_2026-07-06` (PENDING).
Driver: `scripts/run_exectv2_sf_closed_option_hybrid_integration.py --cache`.
Prior art: `sf_closed_option_direction_selector_2026-07-06` (registry entry 33,
the standalone probe that REFUTED "fundamental" at +0.0552 on the raw SF-verify
artifact). This is its **substrate-integration follow-up**: the same closed-
option contract, now wired as a candidate direction source on the **hybrid SF
lane** (the v08 production surface), re-scored against the **0.8897** hybrid
`state_profile_directional` reference.
Umbrella plan: open question #1 of
`docs/plans/predecessor_synthesis_followups_2026-07-06.md`.

## Purpose (the integration question)

The standalone probe (item 2) established that a closed-option direction
selector recovers direction **on the raw SF-verify LLM artifact** (+0.0552,
0.6552 → 0.7103), refuting the "fundamental" framing of the SF capacity-vs-
execution gap. It noted (results doc §Implications): *"the production v08
hybrid currently sources direction from deterministic `rules/change.py` (0.8897)
— the closed-option selector does not beat that, but it offers a complementary
LLM-side direction signal that could feed the hybrid arbitration as a candidate
source. That integration is out of scope here."*

**This experiment runs that integration.** The question is no longer "does the
closed-option contract work at all" (answered: yes, on the raw artifact) but:
**does sourcing SF direction from the LLM closed-option selector — instead of
the deterministic `rules/change.py` that the v08 hybrid uses — match, approach,
or regress the 0.8897 hybrid `state_profile_directional` reference?**

This is **candidate work**, not a thesis-mover. The standalone refute already
changed the central claim's status; this probe tests whether the LLM selector is
a viable *production* direction source on the actual hybrid substrate, or whether
the deterministic rules remain the superior final source (as the inversion
synthesis concluded).

## Scope correction (deviation from the plan's "gan2026" wording)

The umbrella plan's open question #1 literally reads: *"wire the closed-option
selector into gan2026's `CandidateSet` as a candidate direction source feeding
the hybrid arbitration, and re-score against the 0.8897 hybrid reference."* The
evidence does not support the literal "gan2026" target:

- **0.8897 is an ExECTv2 number**, not a gan2026 number. It is the v08 hybrid
  `state_profile_directional` on dev140, with direction sourced from
  `deterministic/rules/change.py` (`PROJECT_STATUS.md:211`; the direction-probe
  docs' free replay; the closed-option results doc line 32).
- **The gan2026 `CandidateSet` stack has no direction concept.** Its
  `CandidateKind` (`gan2026/deterministic/candidates.py:13-18`) is
  `{frequency_rate, cluster_frequency, seizure_free, last_event_only,
  unknown_frequency, no_reference}`; `NormalizedBurden` has no direction field;
  the assessment probe actively *pushes* improvement/worsening language out of
  structured fields into `assessment_summary`. The gan2026 stack scores against
  monthly frequency (purist/pragmatic), a different surface where 0.8897 does
  not apply.
- **The proven closed-option selector ran on ExECTv2** (`state_profile_directional`,
  dev140), scoring 0.7103.

**Therefore this predeclaration freezes on the ExECTv2 hybrid SF lane as the
integration target** — the surface where the 0.8897 reference and the
`FrequencyChange` attribute already live, and where the proven selector ran. The
gan2026 `CandidateSet` was considered and rejected as the literal target because
inventing a direction concept in a stack that has none, on a metric that isn't
direction-sensitive, would not be a test of the 0.8897 reference. (The plan's
own item-2 "What already exists" lists both CandidateSets and calls the ExECTv2
one "the analogue," suggesting the wording conflated them.) This deviation is
documented here for auditability; it is the smallest honest change that tests
the reference the plan names.

## Vocabulary (inherited, unchanged)

The closed 5-value `FrequencyChange` gold vocab (`rules/change.py:3`):
`{Decreased, Frequent, Increased, Infrequent, Same}`. The selector menu lists
all five + `ABSTAIN` always (the closed-option contract constrains output, not
options); abstention maps deterministically to `Same`. Identical to the
standalone probe.

## Frozen contract

| Field | Value |
| --- | --- |
| Selector | `ClosedOptionDirectionSelector` from `hybrid.closed_option_direction` (the library module extracted from the standalone probe — single-sourced contract) |
| Integration seam | `hybrid/clinical_assessment.py::run_split(direction_selector="llm_closed_option")` — opt-in; the default `"off"` path is the v08 production lane (direction from `rules/change.py`), byte-identical, reproduced in-run as the baseline |
| Override behavior | When a letter qualifies (≥1 kept assessment carrying a `FrequencyChange` suggestion OR a `frequency_state_faithful == "changed"` state — the standalone probe's disagreement definition), the selector fires once; its pick overrides `FrequencyChange` on kept SF mentions *after* assessment, with provenance stamped in row diagnostics. The LLM still owns keep/drop and the other attributes; the selector owns only the direction. |
| Input artifact (replay mode) | `experiments/exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl` (the saved v08 hybrid SF output; carries `FrequencyChange` in `predicted_mentions[*].attributes`, sourced from `rules/change.py`) |
| Model | `openai/gpt-4.1-mini` |
| Temperature | 0.0 (matches the standalone probe + B1/B2) |
| max_tokens | 8000 |
| Cache | on (`--cache`) |
| Split | dev140 only (the 0.8897 reference is dev140; test59 frozen) |
| Call count | **~28** in replay mode (one selector call per qualifying letter — the same disagreement set the standalone probe used: 28 letters with changed-state mentions). Live mode would be ~140; replay is the headline. |
| Scorer | `score_frequency_state` → `state_profile_directional` (primary), `state_profile` (regression check) — unchanged, reused from the standalone probe |
| Baseline reference | 0.8897 `state_profile_directional` (v08 hybrid, dev140), reproduced in-run from the input artifact before the selector fires |
| Row inspection | dev140 only (qualifying letters); no test59 / full-200 row inspection |

## Predeclared outcomes

Target metric = `state_profile_directional`. Reference: v08 hybrid **0.8897**
(direction from `rules/change.py`); standalone-probe closed-option on raw SF-
verify **0.7103** (the floor — the selector's recovery on the raw artifact).

| Outcome | Verdict | Action |
| --- | --- | --- |
| Hybrid-with-LLM-direction **≥ 0.8897** with no `state_profile` regression | **MATCHES the deterministic rules** — the LLM selector is a viable production direction source; the contract finding (item 2) transfers to the integration level | Report as corroboration; the closed-option selector is a production-relevant alternative to `rules/change.py` |
| Hybrid-with-LLM-direction **0.7103 ≤ x < 0.8897** | **APPROACHES but does not match** — the selector lands at/above the standalone-probe level; the residual is integration cost + cases the deterministic rules catch that the menu misses | Report "the selector is a viable *candidate* source but the deterministic rules remain superior as the *final* source" (consistent with the inversion synthesis) |
| Hybrid-with-LLM-direction **< 0.7103** | **REGRESSES below the standalone probe** — the hybrid substrate adds cost without benefit; the selector harms the hybrid lane | Recommend against production wiring; the deterministic rules are unambiguously the right final source |
| `state_profile` regresses | **CONTRACT FAILURE** — the override harmed the direction-blind metric (e.g. the selector's `FrequencyChange` interacts badly with the verify/route gate) | Document; recommend against wiring |

The interesting band is the middle one (0.7103 ≤ x < 0.8897): the standalone
probe already showed the selector recovers direction on the raw artifact, so the
integration question is *how much of the deterministic-rules advantage survives*.
The deterministic `rules/change.py` is genuinely strong (the inversion synthesis
concluded it is "genuinely superior" to LLM direction); the expected outcome is
that the integrated selector approaches but does not match the rules — making
this likely a **negative-for-production-wiring** result that nonetheless
corroborates the standalone contract finding.

## Cost & isolation

- ~28 gpt-4.1-mini calls (replay mode; one selector call per qualifying letter),
  temp 0, cached. The hybrid SF artifact is already saved — no hybrid-assessment
  LLM calls fire in replay mode.
- Same-day baseline (0.8897) reproduced in-run from the input artifact before
  the selector fires, so the delta is isolated from scorer drift.
- dev140 only; no test59 / full-200 row inspection.

## Why replay mode (not live mode) is the headline

The cleanest attribution design isolates the *direction-source* variable (LLM
selector vs deterministic rules) while holding the rest of the hybrid lane fixed.
Replay mode does exactly that: load the saved v08 hybrid output, fire the
selector on the disagreement-set letters, overwrite `FrequencyChange` on those
letters' SF mentions with the selector's pick, carry all 140 letters through,
re-score. The only thing that changes is the direction-attribute provenance.

Live mode (`run_split(..., direction_selector="llm_closed_option")` end-to-end)
would re-run the hybrid assessment too, adding ~140 calls and conflating
assessment variance with direction-source variance. It is implemented (the
`direction_selector` parameter is wired into `run_split`) and available as a
cross-check, but replay is the headline attribution surface.

## What this is NOT

- Not a re-test of the "fundamental" claim (the standalone probe settled that:
  closed-option REFUTES fundamental on the raw artifact). This tests production
  integration, not the capacity-vs-execution gap.
- Not a test on the gan2026 `CandidateSet` stack (rejected per the scope
  correction above; that stack has no direction concept and the 0.8897 reference
  does not apply to it).
- Not a test of dspy's absolute 90.3% rate (item 6 showed that number is on a
  different scoring convention).
- Not conflated with item 3 (retrieval-highlight priming) — item 3 changes the
  *input*; this changes the *direction source* on the hybrid substrate.
- Not a claim that the LLM selector should replace `rules/change.py` in
  production — the inversion synthesis already concluded the deterministic rules
  are superior. This probe quantifies *how much* superior, on the integration
  surface.
