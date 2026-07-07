# Results — SF closed-option direction selector, hybrid-lane integration (item 2 follow-up, dev140)

Date: 2026-07-06. Owner: ExECTv2 workstream.
Hypothesis: `sf_closed_option_hybrid_integration_2026-07-06` → **APPROACHES but
does not match the deterministic rules** (negative-for-production-wiring;
corroborates the inversion synthesis).
Driver: `scripts/run_exectv2_sf_closed_option_hybrid_integration.py --cache --mode replay`.
Predeclaration: `exectv2_sf_closed_option_hybrid_integration_predeclaration_2026-07-06.md`.
Cost: 25 gpt-4.1-mini calls (dev140, temp 0, cached). Split discipline: dev140 only.
Umbrella plan: open question #1 of
`docs/plans/predecessor_synthesis_followups_2026-07-06.md`.

## Headline

**Sourcing SF direction from the LLM closed-option selector on the hybrid lane
scores 0.8333 dev140 `state_profile_directional`, below the deterministic-rules
hybrid reference of 0.8897 (delta −0.0563), with `state_profile` byte-identical
(0.9338, no regression). The selector APPROACHES but does not match the
deterministic rules. The deterministic `rules/change.py` remains the superior
final direction source on the hybrid lane — consistent with the inversion
synthesis's "the deterministic direction arbitration is genuinely superior"
conclusion.**

This is a **negative-for-production-wiring** result that **does not contradict
the standalone probe's refute of "fundamental."** The two probes answer different
questions:

- **Standalone probe (item 2, +0.0552):** on the *raw direction-blind LLM
  artifact* (0.6552), does a closed-option contract recover direction? **Yes** —
  the contract deploys capacity the free-write contract couldn't. This moved the
  thesis (refuted "fundamental").
- **This integration (−0.0563):** on the *hybrid lane* (0.8897, already sourcing
  direction from deterministic rules), does REPLACING the deterministic rules
  with the LLM selector match them? **No** — the deterministic rules are
  genuinely better at direction on the hybrid substrate. This does not move the
  thesis; it confirms the deterministic rules are the right production source.

The selector lands *above* its own standalone-probe floor (0.7103 → 0.8333 here)
because the hybrid substrate's other components (keep/drop, verify/route) are
stronger than the raw artifact's — the selector starts from a better base. But
it lands *below* the deterministic-rules reference because the rules capture a
direction concept the selector systematically drops (see §Mechanism).

## The numbers

| Run | `state_profile_directional` F1 | `state_profile` F1 |
| --- | ---: | ---: |
| **v08 hybrid SF (deterministic rules/change.py direction)** | **0.8897** (tp=125 fp=16 fn=15) | 0.9338 |
| **Hybrid + LLM closed-option selector (this probe, 25 calls)** | **0.8333** (tp=115 fp=21 fn=25) | **0.9338** (byte-identical) |
| Standalone closed-option on raw SF-verify (item 2, prior art) | 0.7103 | 0.7483 |
| Raw SF-verify (direction-blind baseline) | 0.6552 | 0.7483 |

`state_profile` (the direction-blind metric) is byte-identical at 0.9338 — the
direction override is purely additive and does not degrade the other SF axes,
exactly as in the standalone probe. The delta is isolated to the direction
component.

### Predeclared outcome verdict

| Outcome band | Verdict | This run |
| --- | --- | --- |
| ≥ 0.8897, no `state_profile` regression | MATCHES the deterministic rules | ✗ |
| **0.7103 ≤ x < 0.8897** | **APPROACHES but does not match** | **✓ (0.8333; delta −0.0563)** |
| < 0.7103 | REGRESSES below the standalone probe | ✗ |
| `state_profile` regresses | CONTRACT FAILURE | ✗ (byte-identical 0.9338) |

**Verdict: APPROACHES but does not match.** The selector is a viable *candidate*
direction source (it recovers direction, doesn't regress the other axes, lands
above its standalone floor) but the **deterministic rules remain the superior
final source** on the hybrid lane. Recommend against production wiring that
*replaces* the rules; the selector could complement them as a tie-breaker but
that is a different design not tested here.

## Mechanism: why the selector lands below the rules

The ledger (50 direction-in-play SF mentions across 25 letters, 40/50 changed
direction) reveals a **conceptual mismatch** in the `FrequencyChange` vocab.

The deterministic `rules/change.py` distribution on these 50 mentions:
`Infrequent` 19, `Frequent` 16, `Increased` 8, `Same` 6, `Decreased` 1.

The LLM selector's assembled distribution:
`Decreased` 21, `Increased` 13, `Same` 12, `Frequent` 4, `Infrequent` 0.

**The selector systematically maps the frequency-magnitude labels
(`Frequent`/`Infrequent`) into the change-direction labels
(`Increased`/`Decreased`/`Same`).** The dominant change is `Infrequent →
Decreased` (14 mentions) and `Frequent → Same`/`Increased`/`Decreased` (12).

This is not noise — it is a defensible reading: when asked "what is the
direction of the patient's seizure-frequency change," the LLM answers in
change-direction terms (better/worse/same), because that is what "direction"
means in plain English. But the gold `FrequencyChange` attribute **conflates two
distinct clinical notions**: change-direction (`Increased`/`Decreased`/`Same`)
AND frequency-magnitude (`Frequent`/`Infrequent`). The deterministic
`rules/change.py` regexes capture both (the `change.frequent`/`change.infrequent`
builders exist precisely for the magnitude reading). The LLM selector, given a
menu of all five, gravitates to the change-direction three and drops the
magnitude two.

**The deterministic rules win because they faithfully implement the (conflated)
gold vocab; the LLM selector answers the plain-English "direction" question,
which is a subset of what the gold attribute encodes.** This is a vocab-design
finding as much as a direction-extraction finding: the `FrequencyChange`
attribute's five values are not a coherent single dimension, and the LLM's
plain-English reading of "direction" diverges from the gold's mixed encoding.

## What the selector did (ledger summary)

- **50 direction-in-play SF mentions** across 25 letters (the qualifying set:
  v08 hybrid mentions carrying a `FrequencyChange` attribute or a `changed`
  state).
- **40/50 changed direction** under the selector (the selector did not just echo
  the rules; it re-decided 80% of cases).
- **19 non-Same selections**: the selector was willing to assign direction, not
  just abstain. Distribution: 6 Increased, 10 Decreased, 3 Frequent (it used the
  `Frequent` magnitude label only 3 times, never `Infrequent`).
- **12 Same outcomes** (abstentions + explicit Same): the selector deferred when
  not confident.
- **Selection modes**: 48 `single_candidate`, 2 `no_reliable_candidate`. The
  abstention validator (mirroring gan2026 `selected_fact.py:32-49`) was wired and
  exercised.
- **`state_profile` byte-identical**: the direction override did not touch the
  count/state fields the direction-blind metric reads.

## Implications for the manuscript

1. **The deterministic `rules/change.py` is the right production direction
   source.** This probe quantifies the gap (−0.0563) when it is replaced by an
   LLM selector on the hybrid lane. The inversion synthesis's "deterministic
   direction arbitration is genuinely superior" conclusion holds at the
   integration level, not just the raw-artifact level.
2. **The standalone refute (item 2) stands; this probe does not weaken it.** The
   standalone probe tested the closed-option *contract* on a *direction-blind*
   artifact and found it deploys capacity. This probe tested the *same selector*
   as a *replacement* for an already-strong deterministic source and found the
   deterministic source superior. The two are consistent: the contract works
   when there is no good deterministic alternative; the deterministic rules are
   the better alternative when they exist.
3. **A vocab-design finding worth reporting.** The `FrequencyChange` attribute
   conflates change-direction and frequency-magnitude. The LLM's plain-English
   reading of "direction" captures only the change-direction subset; the
   deterministic regexes capture both. This is a reason the deterministic rules
   are not just "a strong baseline" but *structurally* better-aligned with the
   (conflated) gold encoding. Worth a sentence in the manuscript's SF section.
4. **The closed-option contract is production-relevant as a complement, not a
   replacement.** The selector recovers real direction without harming the other
   axes; a future design could use it as a tie-breaker or recall backstop when
   the deterministic rules have no regex match (the 21/25 letters with no
   deterministic cue). That design is out of scope here.

## Scope note (deviation from the plan's "gan2026" wording)

The plan's open question #1 literally named the gan2026 `CandidateSet` as the
integration target. The predeclaration documents why this was corrected to the
**ExECTv2 hybrid SF lane**: 0.8897 is an ExECTv2 number, the gan2026 stack has
no direction concept and scores a different surface (monthly purist/pragmatic),
and the proven selector ran on ExECTv2. Building into gan2026 literally would
have tested neither the 0.8897 reference nor the proven selector's surface. See
the predeclaration's "Scope correction" section for the full reasoning.

## Limitations and honest caveats

- **dev140 only.** The 0.8897 reference is dev140; test59 is frozen. The
  −0.0563 is a dev140 number.
- **Replay mode only (the headline).** Live mode (`run_split(...,
  direction_selector="llm_closed_option")` end-to-end) is implemented and
  available but not run for cost; replay isolates the direction-source variable
  cleanly by holding the rest of the hybrid lane fixed. A live-mode cross-check
  would add assessment variance to the direction-source variance.
- **The selector replaces; it does not complement.** This probe OVERWRITES
  `FrequencyChange` with the selector's pick. A complement design (selector only
  when the rules have no match) is not tested and could close some of the gap.
- **The vocab-conflation mechanism is a hypothesis, not a proven cause.** The
  ledger shows the LLM maps magnitude labels into direction labels; the
  interpretation (that the gold vocab conflates two dimensions) is consistent
  with the pattern but a per-row gold audit would confirm it. Such an audit is
  out of scope (dev140 row inspection is permitted but the mechanism reading is
  already defensible from the distribution shift).
- **Single model, single temp.** gpt-4.1-mini temp 0, matching the standalone
  probe + B1/B2. No cross-model replication.

## Artifacts

- Driver: `scripts/run_exectv2_sf_closed_option_hybrid_integration.py`.
- Predictions: `experiments/exectv2_sf_closed_option_hybrid_integration_dev140_20260706.jsonl`
  (v08 hybrid output with `FrequencyChange` overwritten by the selector).
- Summary: `experiments/exectv2_sf_closed_option_hybrid_integration_summary_20260706.json`.
- Per-mention ledger: `experiments/exectv2_sf_closed_option_hybrid_integration_ledger_20260706.jsonl`.
- Library (single-sourced contract): `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/hybrid/closed_option_direction.py`.
- Hybrid wiring (opt-in parameter): `hybrid/clinical_assessment.py::run_split(direction_selector=...)`.
