# Gan 2026 Agentic Line: Next-Phase Brief

Date: 2026-06-14

Status: validation-only design brief distilled from the completed structured-event,
consensus, V1-V11 ladder, and V12 fresh-evidence results. This does not authorize a
new `test450` run, does not tune from V12 row-level holdout behavior, and does not
change scoring policy. It exists to point the next validation-only cycle at the
right metric and the right experiment.

## Why this brief exists

The structured-event consensus surface (`structured_event_consensus.py`) and its
unit test encode a *mechanic* — flip the deterministic baseline only on unanimous
exact-label agreement — but say nothing about whether that mechanic is a good
*signal*. Reading the validation750 and test450 replays together shows the mechanic
is built on a proxy that does not survive holdout. This brief states the insights
sharply so the next cycle does not re-run the same shape of experiment.

## Insight 1: the validation -> test gap is the architecture-selection signal

Rank by holdout loss, not peak validation:

| Architecture | Validation Purist | Test Purist | Gap |
| --- | ---: | ---: | ---: |
| Deterministic floor | 0.929 (697/750) | 0.762 (343/450) | -16.7pp |
| Three-agent exact consensus | 0.944 (708/750) | 0.811 (365/450) | -13.3pp |
| GPT structured-events V0 | 0.881 (661/750) | 0.809 (364/450) | -7.2pp |
| V12 fresh-evidence reasoner | 0.909 (682/750) | 0.842 (379/450) | -6.7pp |

The gap tracks how much of the answer is borrowed from deterministic,
validation-tuned components. The floor is the most overfit; consensus is floor
plus a thin override and inherits that overfit; V12 has the smallest gap *and* the
best test score because the LLM owns the final selection and deterministic code is
demoted to prompt assembly, format-only repair, exact-evidence filtering, safety
gates, rendering, and scoring.

Consensus "won" validation (the only run to clear 700/750) and was the worst
generalizer of the LLM-centred options.

**Action:** promote candidates on within-validation cross-family stability (hold
out clinical families, not just rows), so a candidate cannot be promoted on a
number that will not survive distribution shift.

## Insight 2: unanimity is a proxy for "easy row," not "correct on a hard row"

The unanimity gate looks principled but the replay attribution shows what it does:

- Validation: 122 changed labels, but only 27 wrong->correct / 16 correct->wrong.
  ~79 of 122 changes were category-neutral (label text changed, Purist bucket
  unchanged). Changed-label precision 0.2213.
- Test: 114 changed, 45 wrong->correct / 23 correct->wrong, precision 0.3947.

Three models agreeing tells you the row is easy, not that the consensus label is
correct on a hard row. The mechanism conflates agreement with accuracy, and quietly
breaks 16-23 already-correct rows.

The oracle that picks among floor + 3 agents reaches 740/750 (0.987) on validation.
The headroom is almost entirely a *selector-quality* problem.

**Action:** make changed-label precision the primary promotion gate, not raw count.
Treat agreement as one weak feature, not the trigger. A row where agents agree but
the baseline was already right should never be a change.

## Insight 3: V12 won by deepening one escalation, not by orchestrating more

The V1-V11 ladder traced a precision/recall frontier: every "safe" variant
(verifier, routers, specialists, cross-model adjudicators) topped out at hard50
40-42/50 with near-zero net gain; every "free" variant (broad reasoner,
represented-event normalizer) regressed. Safer = weaker, freer = worse.

V12 broke the frontier with a single well-scoped action — return to raw evidence
and keep-or-replace — not with more agents. On test, format-only repair contributed
0 rows (raw 372 -> format 372); the entire gain came from the replace step
(372 -> 379). Deterministic rendering/parsing is exhausted.

The matched-budget work already showed extra context hurts (parser/candidate
context dropped hard50 to 19-21/50) and multi-agent panels do not beat
self-consistency at equal budget.

**Action:** do not add agents or tools. Make V12's replace decision more selective
(uncertainty-gated) without losing the high-value replacements. Any larger
orchestration must beat a matched-budget single-agent comparator before it is
trusted.

## Insight 4: source-coverage asymmetry silently invalidated the consensus audit

The validation policy used GPT + Qwen(v0.6 + recent-unresolved-burden patch) +
DeepSeek(v0.6). The test had no DeepSeek artifact on disk, so the audit silently
degraded to a different, weaker two-agent policy. The 708 -> 365 comparison is not
apples-to-apples.

**Action:** freeze the model panel and verify that every panel member's `test450`
artifact exists *before* any validation freeze. Make panel/source symmetry across
splits a hard precondition in the freeze protocol, not a tuning detail.

## Insight 5: instrument the gap before attacking it

V12 missed the 383/450 target by 4 rows; the residual is clinical selection under
distribution shift, not formatting. But no run reports which families drive the
validation750 (682) -> test450 (379) drop. The candidate families are
denominator/window, cluster axis, seizure-free duration, unknown/no-reference, and
multi-semiology.

**Action:** the highest-leverage next experiment is validation-only: add per-family
transition reporting to the replay artifacts so a future freeze knows whether
gains/losses concentrate in a specific boundary family. We are currently optimizing
a scalar against a target we cannot decompose.

## Next-phase checklist

1. Promote on gap-robustness (held-out-family CV), not peak validation.
2. Make changed-label precision the primary selector gate; agreement is a feature,
   not a trigger.
3. Deepen V12's single replace action with uncertainty gating; no new agents until
   a matched-budget comparator is beaten.
4. Hard-gate panel/source symmetry across splits in the freeze protocol.
5. Add per-family transition reporting first, so the 0.84 -> 0.85 gap is decomposed,
   not guessed.

## Work completed (2026-06-14)

Checklist step 5 (per-family transition reporting, the prerequisite for step 1)
is implemented, checklist step 1 (held-out-family CV promotion) builds on it, and
checklist step 2 (precision-gated decision selector) builds on both — see the
dedicated sections below. Steps 3 and 4 are closed by the 2026-06-15 follow-up
sections below.

- New shared module `agentic/family_transitions.py`:
  - `note_text_from_rules_row` — attached `note_text` field, else parse
    `prompt_input_json`, else `""` (safe degradation).
  - `tag_hidden_families` — wraps `labels.classify_hidden_families`, classifying
    on the **baseline label** so a row's family set is stable regardless of
    whether the candidate flips it.
  - `summarize_transitions_by_family` — schema-agnostic via key paths; returns
    `{families, total_rows, multilabel_note}` with per-family `rows`,
    `baseline_purist_correct`, `candidate_purist_correct`, `changed_labels`,
    `wrong_to_correct`, `correct_to_wrong`, `net_purist_gain`,
    `changed_label_precision`. Families are multi-label, so per-family counts
    overlap and do not partition `total_rows` (stated in `multilabel_note`).
  - `CONSENSUS_PATHS` / `FRESH_EVIDENCE_PATHS` presets for the two row schemas.
- Wired into `structured_event_consensus.py` and V12 `fresh_evidence_reasoner.py`
  as `metadata["summary_by_family"]`, **gated on `split != "test"`** so the
  holdout audit stays aggregate-only per the freeze protocol.
- Tests: new `tests/test_gan2026_family_transitions.py` (note-text fallbacks,
  multi-label fan-out, gain/precision math, unclassified default) plus two cases
  added to `tests/test_gan2026_agentic_structured_event_consensus.py`
  (decomposition present on validation, omitted on holdout). The consensus test
  also gained an interpretive module docstring on why exact unanimity was chosen
  and its known failure mode.
- Smoke on the real validation750 rules artifact: `note_text` threaded on all
  750 rows; every family populates.

**Caveat that gated this work's usefulness (now resolved — see update below):**
the reused `classify_hidden_families` taxonomy was too permissive to
discriminate the gap. On validation750 `current_vs_historical` fired 739/750 and
`diary_or_log_aggregation` 727/750 — near-universal families cannot isolate
where validation diverges from test. Before this readout is trusted for a freeze
decision, the taxonomy needs tighter, more mutually-exclusive families (or
splitting the heavy families by rate bucket / boundary category). The
instrumentation is correct; its signal is only as sharp as the family
definitions.

### Taxonomy sharpening (2026-06-14, follow-up)

The caveat above is resolved. A new dedicated classifier
`labels.classify_boundary_families` (plus `labels.boundary_band`) replaces the
saturated keyword taxonomy *for the transition readout only*; the legacy
`classify_hidden_families` is left untouched because frozen pre-registrations
(`selective_boundary_candidate_predeclaration`) and the `rq1_rq2` control panels
hardcode its exact family names. `family_transitions.tag_hidden_families` now
takes `gold_per_month` (not gold/baseline label text) and the two agentic call
sites thread `reference.gold_monthly_frequency` through.

The new taxonomy has two axes:

- **Partitioning boundary bands** from the *gold* monthly rate (a coarsened
  `map_purist`): `band_zero`, `band_unknown`, `band_submonthly`, `band_monthly`,
  `band_weekly`, `band_daily`. Exactly one per row; on validation750 they sum to
  750 and no band exceeds 24%. These map onto the brief's denominator/window and
  unknown/no-reference gap candidates.
- **Cleaned qualitative families**, word-boundary regex over note text only:
  `cluster_burden` (43%) and `seizure_free_duration` (15%). Semiology was dropped
  — it fires on a majority of epilepsy notes at any threshold (59% at >=2 distinct
  types) and so cannot isolate the gap.

Measured impact on the validation750 consensus replay: per-band changed-label
precision now spans 0.11 -> 1.00 (the old taxonomy was a uniform ~0.22
aggregate), and the readout localizes the consensus override's damage — it nets
-3 on `band_weekly` (8 correct->wrong vs 5 wrong->correct) while `band_daily` is a
clean 6/6. This operationalizes Insights 2 and 5 together and unblocks checklist
step 1 (held-out-family CV promotion).

Touched: `labels.py`, `agentic/family_transitions.py`,
`agentic/structured_event_consensus.py`, `agentic/fresh_evidence_reasoner.py`,
`tests/test_gan2026_family_transitions.py`,
`tests/test_gan2026_agentic_structured_event_consensus.py`.

### Held-out-family CV promotion (2026-06-14, checklist step 1)

Step 1 is implemented on top of the sharpened taxonomy. The new module
`agentic/family_cv_promotion.py` (`summarize_family_holdout_cv`) turns the
per-family transition summary into a promotion *gate* instead of a readout. It
runs leave-one-band-out CV over the six partitioning boundary bands (the
canonical fold set is now exported as `labels.BOUNDARY_BANDS`): for each fold the
held-out band's own transitions are the generalization estimate and the union of
the remaining bands is the retained/selection set. A candidate is `gap_robust`
only if (a) the aggregate net Purist gain is positive, (b) no held-out band
regresses (net Purist gain >= 0), and (c) every band that changes labels clears a
changed-label precision bar (default 0.5, parameterized). Conditions (b) and (c)
fold Insights 1 and 2 into the gate: agreement/aggregate count is never the
trigger, and a band carried by distribution-shift-fragile borrowing is caught.

Wired into `structured_event_consensus.py` and `fresh_evidence_reasoner.py` as
`metadata["family_holdout_cv"]`, **gated on `split != "test"`** alongside
`summary_by_family`, so the verdict is a validation-only instrument.

Measured on the real validation750 consensus replay (the only run to clear
700/750), the gate does exactly what the brief argues it should: it **refuses**
the candidate that won validation.

| Band | rows | held-out net gain | changed-label precision |
| --- | ---: | ---: | ---: |
| band_zero | 112 | +0 | 0.12 |
| band_unknown | 170 | +5 | 0.17 |
| band_submonthly | 87 | +0 | 0.11 |
| band_monthly | 141 | +3 | 0.31 |
| band_weekly | 177 | **-3** | 0.19 |
| band_daily | 63 | +6 | 1.00 |

Aggregate net gain is **+11** (the number promote-on-peak-validation would have
used) but `gap_robust = False`: `band_weekly` regresses (5 wrong->correct vs 8
correct->wrong) and five of six bands fall below the 0.5 precision bar. This is
the overfit signature of Insight 1 made into a hard verdict — a positive
aggregate riding on `band_daily` while a held-out band is silently sacrificed.

Touched: `labels.py` (`BOUNDARY_BANDS`),
`agentic/family_cv_promotion.py` (new),
`agentic/structured_event_consensus.py`, `agentic/fresh_evidence_reasoner.py`,
`tests/test_gan2026_family_cv_promotion.py` (new),
`tests/test_gan2026_agentic_structured_event_consensus.py`.

This closes checklist step 1. Step 2 (make changed-label precision the primary
selector gate at the *decision* layer, not just the audit layer) is now also
closed — see the dedicated section below. Step 3 (uncertainty-gated V12 replace)
and step 4 (panel/source symmetry hard-gate) are now closed by the 2026-06-15
follow-up sections below.

### Precision-gated decision selector (2026-06-14, checklist step 2)

Step 1 turned changed-label precision into a whole-candidate *verdict* that never
changes what the pipeline emits. Step 2 turns the same signal into a *selector*
that edits the output. The new module `agentic/precision_gated_selector.py`
(`summarize_precision_gated_selector`) keeps agreement as the candidate-generating
feature — the upstream selector still proposes a switch — but only *applies* a
proposed switch inside boundary bands whose changed-label precision clears the bar
(default 0.5) and whose net Purist gain is non-negative. The allow-set is a frozen
per-band policy, learned on validation and meant to be frozen before any held-out
application; a `leave_one_out` field recomputes each row's gate with that row
excluded from its band's statistics, so no band is credited for a switch whose own
outcome set its gate. The module is schema-agnostic via the same `*_PATHS` presets
as `family_transitions`, and is wired into both
`structured_event_consensus.py` and `fresh_evidence_reasoner.py` as
`metadata["precision_gated_selector"]`, **gated on `split != "test"`** alongside
`summary_by_family` and `family_holdout_cv`.

Measured on the real validation750 consensus replay, the selector does at the
decision layer what step 1's verdict only flagged. Agreement proposed 122
switches; precision kept 6:

| Band | switched | net Purist gain | changed-label precision | allowed |
| --- | ---: | ---: | ---: | :---: |
| band_zero | 17 | +0 | 0.12 | no |
| band_unknown | 47 | +5 | 0.17 | no |
| band_submonthly | 9 | +0 | 0.11 | no |
| band_monthly | 16 | +3 | 0.31 | no |
| band_weekly | 27 | **-3** | 0.19 | no |
| band_daily | 6 | +6 | 1.00 | **yes** |

The ungated candidate scores 708/750 (+11 over the 697 baseline) — the number
that "won" validation. The gated selector keeps only `band_daily`'s clean +6 and
reverts the other five bands, landing at **703/750 (gated net +6)**. In doing so
it suppresses 16 correct->wrong regressions and 79 category-neutral churn switches
(the "agents agree but the baseline was already right" case of Insight 2) at the
cost of forgoing 21 fixes that lived in the low-precision, distribution-shift
-fragile bands. The leave-one-out estimate is identical (+6, 6 switches kept):
`band_daily`'s six unanimous fixes survive removal of any one, so the retained
gain is the generalizing portion, not a single-row artifact. This is Insight 1's
overfit signature (+11 riding on borrowed deterministic components) converted into
an actual, gold-free-at-decision-time output policy.

Touched: `agentic/precision_gated_selector.py` (new),
`agentic/structured_event_consensus.py`, `agentic/fresh_evidence_reasoner.py`,
`tests/test_gan2026_precision_gated_selector.py` (new),
`tests/test_gan2026_agentic_structured_event_consensus.py`.

### V12 safety-gate v0.4 (2026-06-15, checklist step 3)

Step 3 is implemented as a conservative selector hardening pass rather than a
new orchestration branch. Validation replay showed that V12 `unknown`
replacements were the only replacement kind with negative net Purist gain, so
`fresh_evidence_reasoner` now rejects them via
`fresh_evidence_gate_fallback: unknown_replacement_not_selective` and bumps the
safety gate to `gan2026_fresh_evidence_safety_gate_v0_4`.

Saved-output validation750 replay over the existing V12 raw outputs:

| Condition | Purist |
| --- | ---: |
| V0 structured-event reference | 661/750 |
| V12 v0.4 original final | 682/750 |
| V12 safety-gate v0.4 replay | 683/750 |

This is directionally useful but not transformational. It suppresses 14 unknown
replacement attempts, reduces correct->wrong regressions from 22 to 19, and
keeps the current V12 family as a hardened comparator rather than a credible
path to the requested `>=405/450` holdout target.

Durable note:
`experiments/gan2026_fresh_evidence_reasoner_safety_v0_4_validation750_no_call_replay_2026-06-15.md`.

### Source-symmetry hard gate (2026-06-15, checklist step 4)

Step 4 is resolved. The filled DeepSeek `test450` structured-event artifact is
now the pinned V12 test source:

`experiments/gan2026_v06_test450_hybrid_structured_events_deepseek_2026-06-14.jsonl`.

`frozen_test_preflight` now hard-gates all three test sources (GPT, Qwen,
DeepSeek) for source path, existence, unique row ids, locked `test450` coverage,
and split labels before any future V12 frozen audit. After Yujian's
unknown-frequency clarification, the current future path uses V12 prompt v0.6
with safety gate v0.9:

`experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_2026-06-15.*`.

### Unknown-frequency policy update (2026-06-15)

Yujian clarified the annotation boundary for unknown frequencies: if either the
seizure count or the relevant time period is unclear, `unknown` is usually safer
than inferring a rate. The v0.4 validation artifact underperformed V0 on the
gold-unknown validation slice (`76/92` final Purist versus V0 `79/92`) and made
the same over-inference errors on supervisor-discussed validation rows.

`fresh_evidence_reasoner` is now prompt version
`gan2026_fresh_evidence_reasoner_v0_6` with safety gate
`gan2026_fresh_evidence_safety_gate_v0_9`. It explicitly tells the model that
last-event-only evidence is unknown, last-seizure-date plus no-seizures-since
does not by itself create a seizure-free duration, open-ended "since
starting/beginning medication or diet" evidence is unknown unless both count and
window are explicit, and explicit count plus usable follow-up period can support
a frequency label. The safety gate selectively allows last-event-only unknown
demotions and blocks open-ended treatment-start denominators when the original
answer is already a boundary state; v0.7 also blocks seizure-free replacements
of original frequency labels when the model rationale is historical frequency,
not a current absence state. Safety v0.8 adds two no-call replay guards for
vague-multiple exactification and same-day cluster downgrades. Safety v0.9 adds
a scorer-neutral semantic repair from `no seizure frequency reference` to
`unknown` when seizure evidence exists but count/window is unclear. This is a
validation-cycle prompt/gate change, not a scorer change or a completed holdout
improvement.

Validation hard-slice signal:

| Surface | V0 Purist | V12 v0.6/safety-v0.9 Purist | W->C | C->W |
| --- | ---: | ---: | ---: | ---: |
| supervisor6 | 4/6 | 5/6 | 1 | 0 |
| trigger25 | 21/25 | 22/25 | 1 | 0 |
| trigger_full | 105/123 | 109/123 | 4 | 0 |
| validation250 no-call replay | 236/250 | 240/250 | 4 | 0 |

The larger trigger panel is a clean targeted win, and safety v0.9 preserves the
v0.8 no-call Purist counts while converting 4 trigger-panel and 5 validation250
no-reference fallbacks to `unknown`. The broader validation250 result still
trails the earlier V12 v0.4 validation250 comparator (`242/250`). Treat prompt
v0.6/safety-v0.9 as diagnostic/revise evidence rather than a frozen holdout
candidate.

Durable note:
`docs/research/gan2026_unknown_frequency_policy_audit_2026-06-15.md`.

### Consensus + fresh agreement selector (2026-06-15)

The next validation-only selector cycle moved beyond V12 micro-gates. The new
module `agentic/consensus_fresh_agreement_selector.py` tests a saved-output
hybrid policy:

1. keep the deterministic/rules-tool baseline by default;
2. accept an exact structured-event consensus switch only when V12
   fresh-evidence reasoning independently emits that same final label.

This directly tests the brief's selector-quality thesis: agreement is useful only
as one feature, and V12's deeper raw-evidence pass may filter the low-quality
portion of exact consensus.

Validation750 no-call replay:

| Condition | Purist |
| --- | ---: |
| Deterministic baseline | 697/750 |
| Exact structured-event consensus | 708/750 |
| V12 fresh-evidence v0.4 | 682/750 |
| Consensus + V12 agreement selector | 712/750 |

Transition profile versus deterministic: 109 changed labels, 26 wrong->correct,
11 correct->wrong, 70 correct->correct churn changes, 2 wrong->wrong, net +15,
changed-label precision 0.2385. Boundary-band net gains are non-negative, but
precision remains weak outside `band_daily`: `band_unknown` 0.1739,
`band_submonthly` 0.125, `band_monthly` 0.3077, and `band_weekly` 0.2381.
`band_daily` is clean at 6/6.

Decision: revise, not freeze. This is the strongest current validation aggregate
for the selector family, but it still does not satisfy the precision-first
promotion rule needed before another holdout-facing candidate. The next useful
design should keep the V12-agreement feature and add higher-precision
non-daily-band discrimination.

Durable artifact:
`experiments/gan2026_consensus_fresh_agreement_selector_validation750_no_call_replay_2026-06-15.md`.

### Consensus + fresh agreement selector v0.2 (2026-06-15)

The v0.1 selector improved aggregate validation but accepted too much boundary
churn. v0.2 adds a conservative, deployable precision gate:

- suppress switches whose deterministic origin is `no seizure frequency
  reference`;
- suppress agreed consensus/V12 replacements to `unknown` or `seizure_free`;
- otherwise keep the v0.1 rule: exact consensus switch plus V12 final-label
  agreement.

Validation750 no-call replay:

| Condition | Purist | Changed | W->C | C->W | Changed-label precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| Consensus + V12 agreement v0.1 | 712/750 | 109 | 26 | 11 | 0.2385 |
| Consensus + V12 agreement v0.2 | 710/750 | 58 | 21 | 8 | 0.3621 |

The trade is useful: v0.2 keeps every 125-row validation block non-negative and
raises precision while retaining a +13 net Purist gain over the deterministic
baseline. Boundary-band summary: `band_unknown` improves to 0.4545 precision
(5 W->C / 1 C->W), `band_daily` stays clean at 6/6, but `band_submonthly`
0.125, `band_monthly` 0.3077, and `band_weekly` 0.25 remain below the promotion
bar.

Decision: revise, not freeze. v0.2 is a better precision profile than v0.1, but
still needs explicit denominator/window and multi-semiology discrimination in
the submonthly/monthly/weekly bands before a holdout-facing protocol would be
reasonable.

Durable artifact:
`experiments/gan2026_consensus_fresh_agreement_selector_v0_2_validation750_no_call_replay_2026-06-15.md`.

### Consensus + fresh agreement selector v0.3 (2026-06-15)

v0.3 keeps the same saved-output selector family but applies Yujian's
unknown-frequency discipline at the decision layer. The selector still requires
exact structured-event consensus plus V12 fresh-evidence agreement, but it now
suppresses:

- switches whose deterministic origin is `unknown` or
  `no seizure frequency reference`;
- agreed replacements to `unknown` or `seizure_free`;
- agreed replacements whose rendered label is parser-ambiguous `other` rather
  than a specific supported label family.

Validation750 no-call replay:

| Condition | Purist | Changed | W->C | C->W | Changed-label precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| Consensus + V12 agreement v0.1 | 712/750 | 109 | 26 | 11 | 0.2385 |
| Consensus + V12 agreement v0.2 | 710/750 | 58 | 21 | 8 | 0.3621 |
| Consensus + V12 agreement v0.3 | 712/750 | 28 | 17 | 2 | 0.6071 |

Boundary-band summary:

| Band | Net | Changed | W->C | C->W | Precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| `band_zero` | 0 | 0 | 0 | 0 | None |
| `band_unknown` | +5 | 6 | 5 | 0 | 0.8333 |
| `band_submonthly` | 0 | 1 | 0 | 0 | 0.0 |
| `band_monthly` | +2 | 3 | 2 | 0 | 0.6667 |
| `band_weekly` | +2 | 12 | 4 | 2 | 0.3333 |
| `band_daily` | +6 | 6 | 6 | 0 | 1.0 |

This is the best precision profile in the selector family so far: v0.3 restores
the v0.1 aggregate while reducing churn by about 74% and moving unknown-band
changes from fragile to high-precision. It is still not a frozen holdout
candidate. The weekly band remains below the precision bar, and this remains a
validation-only replay over saved outputs. The next selector should focus on
weekly denominator/window and multi-semiology discrimination rather than adding
more agents.

Durable artifact:
`experiments/gan2026_consensus_fresh_agreement_selector_v0_3_validation750_no_call_replay_2026-06-15.md`.

### Consensus + fresh agreement selector v0.4 (2026-06-15)

v0.4 targets the remaining v0.3 weekly-band regressions. Both regressions were
cluster-burden degradations: one demoted a cluster cadence to a plain monthly
rate, and one changed a deterministic five-clusters-per-month cadence to one
cluster per month. v0.4 therefore keeps all v0.3 unknown/ambiguous safeguards
and adds a cluster-cadence gate:

- if the deterministic label contains a cluster cadence, consensus/V12 agreement
  may not demote it to a non-cluster label;
- if both deterministic and agreed labels contain a cluster cadence, the cadence
  itself must match; the selector may still refine events-per-cluster burden.

Validation750 no-call replay:

| Condition | Purist | Changed | W->C | C->W | Changed-label precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| Consensus + V12 agreement v0.1 | 712/750 | 109 | 26 | 11 | 0.2385 |
| Consensus + V12 agreement v0.2 | 710/750 | 58 | 21 | 8 | 0.3621 |
| Consensus + V12 agreement v0.3 | 712/750 | 28 | 17 | 2 | 0.6071 |
| Consensus + V12 agreement v0.4 | 714/750 | 26 | 17 | 0 | 0.6538 |

Boundary-band summary:

| Band | Net | Changed | W->C | C->W | Precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| `band_zero` | 0 | 0 | 0 | 0 | None |
| `band_unknown` | +5 | 6 | 5 | 0 | 0.8333 |
| `band_submonthly` | 0 | 1 | 0 | 0 | 0.0 |
| `band_monthly` | +2 | 3 | 2 | 0 | 0.6667 |
| `band_weekly` | +4 | 10 | 4 | 0 | 0.4 |
| `band_daily` | +6 | 6 | 6 | 0 | 1.0 |

This is the selector-family front-runner: it restores more aggregate validation
headroom than exact consensus alone, removes all changed-label regressions in
the saved replay, and keeps the unknown-frequency improvements from v0.3. It is
still not a frozen holdout candidate. The gate was mined on validation replay
rows, so the next step is a predeclared hard-slice or robustness panel covering
cluster cadence, weekly denominator/window, and multi-semiology cases before any
future holdout-facing protocol.

Durable artifact:
`experiments/gan2026_consensus_fresh_agreement_selector_v0_4_validation750_no_call_replay_2026-06-15.md`.

### v0.4 hard-slice audit (2026-06-15)

Because v0.4 was mined from validation replay behavior, it needed a harder
selective-action audit before being treated as anything more than a useful
diagnostic. The audit fixes slice membership from saved selector features and
then scores those slices on validation:

- v0.4 accepted actions;
- validation weekly-band accepted actions;
- non-cluster specific corrections;
- same-cadence cluster-burden refinements;
- unknown-band accepted actions;
- monthly-or-weekly accepted actions;
- v0.3 actions suppressed by v0.4;
- six 125-row validation blocks.

Key readout:

| Slice | Rows | W->C | C->W | Net | Precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| all v0.4 accepted actions | 26 | 17 | 0 | +17 | 0.6538 |
| weekly accepted actions | 10 | 4 | 0 | +4 | 0.4 |
| unknown-band accepted actions | 6 | 5 | 0 | +5 | 0.8333 |
| same-cadence cluster refinements | 4 | 1 | 0 | +1 | 0.25 |
| v0.3 actions suppressed by v0.4 | 2 | 0 | 2 | -2 | 0.0 |

The suppressed actions are exactly the two v0.3 regressions: one cluster-label
demotion and one cluster-cadence change. v0.4 keeps all `17` W->C fixes and has
no changed-label regressions in any 125-row validation block. This supports the
clinical rationale for the gate.

Decision: still revise, not freeze. The audit is validation-only and uses saved
outputs, so it reduces concern about v0.4 but does not prove robustness. The
next meaningful evidence is a predeclared source-near synthetic/adversarial
panel for cluster cadence, weekly denominator/window, unknown-boundary, and
multi-semiology cases, run as component-stress conditions before any
holdout-facing protocol.

Durable artifact:
`experiments/gan2026_consensus_fresh_agreement_selector_v0_4_hard_slice_audit_2026-06-15.md`.

### v0.4 synthetic component-stress and unknown-origin check (2026-06-15)

The requested source-near synthetic/adversarial component-stress step is now
complete. The panel uses hand-specified deterministic, consensus, and V12
fresh-evidence component outputs plus the real v0.4 selector implementation. It
does not read Gan rows and is not validation, holdout, benchmark, or
model-performance evidence.

Stress coverage:

- cluster cadence demotion and cluster-cadence changes;
- same-cadence cluster burden refinements;
- weekly denominator/window corrections;
- last-event-only and open-ended "since starting" unknown-boundary cases;
- explicit count-plus-window cases that begin from deterministic `unknown`;
- seizure-free replacements of current rates;
- multi-semiology highest-current-burden selection;
- agreement controls where fresh evidence disagrees or consensus is unchanged.

Synthetic readout:

| Surface | Purist |
| --- | ---: |
| Deterministic component | 13/20 |
| Consensus component | 11/20 |
| Fresh-evidence component | 12/20 |
| v0.4 selected | 18/20 |

v0.4 matches the expected action on `20/20` synthetic cases, blocks `9` unsafe
agreed switches, changes `7` labels, and has `5` W->C with `0` C->W. The panel
supports the v0.4 mechanism but also exposes the main conservative cost: explicit
count-plus-window cases that start from deterministic `unknown` remain unknown.

That tempting v0.5 relaxation was checked on the saved validation750 selector
rows before implementation. Only `4` validation switches were blocked solely by
deterministic `unknown` origin. Accepting them all would yield `0` W->C, `2`
C->W, `2` C->C, and net `-2`; the two regressions are gold-unknown rows with the
same last-event/seizure-free over-interpretation risk highlighted by Yujian.

Decision: keep v0.4, revise toward evidence-aware unknown-origin handling only.
A future v0.5 must key on explicit count plus usable follow-up period from
evidence, not on consensus plus fresh agreement alone, and it needs its own
predeclared development panel before any holdout-facing protocol.

Durable artifacts:
`experiments/gan2026_consensus_fresh_agreement_selector_v0_4_synthetic_component_stress_2026-06-15.md`;
`experiments/gan2026_consensus_fresh_agreement_selector_v0_4_unknown_origin_relaxation_probe_2026-06-15.md`.

### Consensus + fresh agreement selector v0.5 (2026-06-15)

The v0.4 unknown-origin probe rejected a broad relaxation out of deterministic
`unknown`, but the remaining validation errors showed a different high-precision
opening: deterministic seizure-free/no-reference boundary overreach. v0.5 keeps
all v0.4 consensus+fresh safeguards and adds one narrow V12 fresh-evidence
rescue after v0.4 would otherwise keep the baseline:

- deterministic `seizure_free` may switch only to fresh `unknown` or
  `no seizure frequency reference`;
- deterministic `no seizure frequency reference` may switch only to fresh
  `seizure_free`;
- deterministic `unknown` to a specific rate remains blocked.

Validation750 no-call replay:

| Condition | Purist | Changed | W->C | C->W | Changed-label precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| Deterministic baseline | 697/750 | 0 | 0 | 0 | None |
| Consensus + V12 agreement v0.4 | 714/750 | 26 | 17 | 0 | 0.6538 |
| Consensus + V12 agreement v0.5 | 728/750 | 40 | 31 | 0 | 0.775 |

Boundary-band summary for v0.5:

| Band | Net | Changed | W->C | C->W | Precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| `band_zero` | +3 | 3 | 3 | 0 | 1.0 |
| `band_unknown` | +16 | 17 | 16 | 0 | 0.9412 |
| `band_submonthly` | 0 | 1 | 0 | 0 | 0.0 |
| `band_monthly` | +2 | 3 | 2 | 0 | 0.6667 |
| `band_weekly` | +4 | 10 | 4 | 0 | 0.4 |
| `band_daily` | +6 | 6 | 6 | 0 | 1.0 |

The v0.5 boundary-rescue audit isolates the new actions added over v0.4. All
`14` are W->C with `0` C->W: `11` deterministic seizure-free to fresh
uncertain-boundary rescues in `band_unknown`, and `3` deterministic
no-reference to fresh seizure-free rescues in `band_zero`. All validation
125-row blocks are non-negative for the new action family.

Decision: revise, not freeze. v0.5 is now the selector-family validation
front-runner, but the improvement is mined from saved validation behavior. The
next evidence should be a predeclared source-near synthetic/adversarial panel
focused on fresh boundary rescue before any holdout-facing protocol.

Durable artifacts:
`experiments/gan2026_consensus_fresh_agreement_selector_v0_5_validation750_no_call_replay_2026-06-15.md`;
`experiments/gan2026_consensus_fresh_agreement_selector_v0_5_boundary_rescue_audit_2026-06-15.md`.

### Consensus + fresh agreement selector v0.6 (2026-06-15)

The predeclared v0.5 boundary-rescue synthetic stress panel confirmed the
validation signal but exposed a portability risk. v0.5 accepted every
seizure-free/no-reference fresh boundary rescue based on label family alone. On
source-near hard negatives, that can erase a valid seizure-free duration or turn
a true no-reference letter into seizure-free.

v0.6 keeps v0.5's validation-winning action family but adds a gold-free
fresh-boundary-profile guard:

- deterministic `seizure_free` may switch to fresh `unknown`/no-reference only
  when the fresh profile supports seizure-free overreach, such as
  last-event-only, unclear denominator/window, qualitative current events, or no
  explicit seizure-free duration;
- deterministic `seizure_free` stays put when the fresh profile affirms an
  explicit seizure-free duration or zero-event interval;
- deterministic `no seizure frequency reference` may switch to fresh
  `seizure_free` only when the fresh profile supports a missed boundary state,
  not when it merely says there is no positive seizure-frequency evidence.

Validation750 no-call replay is unchanged from v0.5:

| Condition | Purist | Changed | W->C | C->W | Changed-label precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| Deterministic baseline | 697/750 | 0 | 0 | 0 | None |
| Consensus + V12 agreement v0.5 | 728/750 | 40 | 31 | 0 | 0.775 |
| Consensus + V12 agreement v0.6 | 728/750 | 40 | 31 | 0 | 0.775 |

The synthetic boundary-rescue panel is where v0.6 matters:

| Condition | Selected Purist | W->C | C->W | Changed-label precision |
| --- | ---: | ---: | ---: | ---: |
| v0.5 label-only rescue | 8/12 | 5 | 3 | 0.625 |
| v0.6 profile-guard rescue | 11/12 | 5 | 0 | 1.0 |

The remaining synthetic miss is the supervisor-approved explicit count plus
usable follow-up period case that starts from deterministic `unknown`. That is
not solved by boundary-profile rescue and should remain blocked until a separate
evidence feature can distinguish it from last-event-only or open-ended "since"
evidence.

Decision: revise, not freeze. v0.6 is the selector-family development
front-runner because it preserves v0.5 validation performance and fixes the
fresh-boundary synthetic hard negatives. It is still saved-output development
evidence, not a holdout-facing frozen candidate.

Durable artifacts:
`experiments/gan2026_consensus_fresh_agreement_selector_v0_5_boundary_rescue_synthetic_stress_2026-06-15.md`;
`experiments/gan2026_consensus_fresh_agreement_selector_v0_6_validation750_no_call_replay_2026-06-15.md`;
`experiments/gan2026_consensus_fresh_agreement_selector_v0_6_boundary_rescue_synthetic_stress_2026-06-15.md`.

### Consensus + fresh agreement selector v0.7 (2026-06-15)

v0.6 left one synthetic false negative that matched Yujian's count-plus-window
exception: deterministic `unknown`, but the note contains an explicit seizure
count and a usable follow-up or observation period. v0.7 adds a separate
gold-free profile gate for exactly that case:

- deterministic origin must be `unknown`;
- consensus and V12 fresh evidence must agree on the same supported specific
  rate label;
- the fresh profile must positively contain both an explicit count signal and a
  usable window/follow-up/observation-period signal;
- the gate blocks last-event-only, "none since", open-ended "since
  starting/beginning", unclear denominator/window, vague-count, unsupported
  replacement, and disagreement profiles.

Validation750 no-call replay is unchanged from v0.6:

| Condition | Purist | Changed | W->C | C->W | Changed-label precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| Consensus + V12 agreement v0.6 | 728/750 | 40 | 31 | 0 | 0.775 |
| Consensus + V12 agreement v0.7 | 728/750 | 40 | 31 | 0 | 0.775 |

The reason is important: the saved validation replay contains no qualifying
unknown-origin W->C row for this profile gate. The previous validation-only
unknown-origin relaxation remains rejected.

The synthetic count-window panel shows the mechanism itself works:

| Surface | Selected Purist | W->C | C->W | Changed-label precision | Desired actions |
| --- | ---: | ---: | ---: | ---: | ---: |
| v0.7 count-window stress | 10/12 | 5 | 0 | 1.0 | 12/12 |

The two synthetic false negatives are intentional conservative costs: a
consensus/fresh disagreement case and a no-reference-origin count-window case.
Both require a separate design before any relaxation.

Decision: revise, not freeze. v0.7 is a cleaner selector-family development
state because it covers the count-window mechanism without damaging validation,
but it is validation-neutral and therefore not a new holdout-facing signal. The
next useful step is a validation-only residual headroom audit over v0.7 selected
wrong rows and oracle-correct component availability, not another micro-gate.

Durable artifacts:
`experiments/gan2026_consensus_fresh_agreement_selector_v0_7_validation750_no_call_replay_2026-06-15.md`;
`experiments/gan2026_consensus_fresh_agreement_selector_v0_7_unknown_count_window_synthetic_stress_2026-06-15.md`.

### v0.7 residual headroom audit (2026-06-15)

The final follow-up audit decomposes the remaining v0.7 selected validation
errors without reading locked test rows or making model calls. v0.7 selected is
correct on `728/750`, leaving `22` selected-wrong rows. Of those, `11` have no
correct component available among deterministic, consensus, and V12 fresh
evidence, so selector changes alone cannot recover them. The other `11` do have
a correct unselected component: `6` where consensus and fresh are both correct,
and `5` where only fresh is correct.

The audit also checks a broad relaxation that looked attractive after v0.7:
accept every consensus+fresh-agreed replacement currently gated as
parser-ambiguous `other` when the label is parseable by the Gan label parser.
That rule is rejected on validation: `27` candidate actions, `4` W->C, `5`
C->W, `16` C->C churn, `2` W->W churn, net Purist `-1`.

Decision: revise, not freeze. The selector has real residual headroom, but the
next rule must be a narrower clinically meaningful profile feature, not parser
compatibility alone. If this line continues, it should be predeclared around the
remaining current-frequency/denominator-window profiles and stress-tested
against source-near hard negatives before any holdout-facing protocol.

Durable artifact:
`experiments/gan2026_consensus_fresh_agreement_selector_v0_7_residual_headroom_audit_2026-06-15.md`.

### Consensus + fresh agreement selector v0.8 (2026-06-15)

The v0.7 residual audit rejected a broad parseable-`other` relaxation, but the
examples exposed a narrower clinically meaningful family: consensus and fresh
evidence sometimes agree on a parser-compatible count/window label that v0.7
gated as `other` only because the label contains an explicit denominator or
range (`11 per 3 month`, `1 per 6 to 8 week`). v0.8 adds a narrow
parseable-refinement gate:

- start from the v0.7 selector and preserve its boundary and unknown-frequency
  protections;
- require consensus and fresh evidence to agree exactly on the replacement;
- require the replacement to be parser-compatible under the Gan label parser;
- require a fresh profile with denominator/window support, explicit current
  frequency clearly stated, or explicit count over a usable current window;
- block boundary origins, last-event-only profiles, seizure-free interval
  profiles, highest-semiology traps, disagreement, and parser-incompatible
  replacements such as `several per month`.

Validation750 no-call replay:

| Condition | Purist | Changed | W->C | C->W | Changed-label precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| Consensus + V12 agreement v0.7 | 728/750 | 40 | 31 | 0 | 0.775 |
| Consensus + V12 agreement v0.8 | 731/750 | 47 | 34 | 0 | 0.7234 |

The `7` v0.8-only parseable-refinement actions contribute `3` W->C and `0`
C->W on saved validation; the other `4` are Purist-preserving label refinements.
The source-near synthetic hard-negative panel matches desired actions `11/11`,
with `3` W->C, `0` C->W, and changed-label precision `1.0`.

Decision: revise, not freeze. v0.8 is the selector-family validation
front-runner, but the improvement is still small and validation-mined. The
post-v0.8 residual leaves `19/750` selected validation errors: `8` have a
correct unselected component and `11` have no correct deterministic,
consensus, or fresh-evidence component available. The next step should be either
a very narrow predeclared selector feature with a hard-negative panel or a shift
back to improving component generation.

Durable artifacts:
`experiments/gan2026_consensus_fresh_agreement_selector_v0_8_validation750_no_call_replay_2026-06-15.md`;
`experiments/gan2026_consensus_fresh_agreement_selector_v0_8_parseable_refinement_synthetic_stress_2026-06-15.md`.

### Consensus + fresh agreement selector v0.9 (2026-06-15)

v0.9 is a residual cleanup pass, not a new architecture. It keeps v0.8 and adds
two narrow gates from the post-v0.8 selected-wrong audit:

- normalized-equivalent consensus/fresh disagreement: if consensus and fresh
  differ textually but normalize to the same monthly frequency, and the
  deterministic label normalizes differently, accept the fresh label;
- specific-rate-to-unknown uncertainty: if deterministic emits a specific rate,
  both model sources emit `unknown`, and the fresh profile explicitly says the
  evidence is unquantified (`unknown_frequency`, no count/rate, device logs or
  patient uncertainty), accept `unknown`;
- block no-reference churn and fully specified cluster-burden demotion.

Validation750 no-call replay:

| Condition | Purist | Changed | W->C | C->W | Changed-label precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| Consensus + V12 agreement v0.8 | 731/750 | 47 | 34 | 0 | 0.7234 |
| Consensus + V12 agreement v0.9 | 733/750 | 49 | 36 | 0 | 0.7347 |

The v0.9-only actions are exactly two validation W->C transitions: one
normalized-equivalent monthly label disagreement and one specific-rate to
unknown-uncertainty rescue. The synthetic stress panel matches desired actions
`7/7`, with `2` W->C and `0` C->W.

Decision: revise, not freeze. v0.9 is the selector-family validation
front-runner, but the result is still too small and validation-local for a
holdout-facing candidate. The post-v0.9 residual leaves `17/750` selected
validation errors; `11` have no correct deterministic, consensus, or
fresh-evidence component available. The next meaningful work should improve
component generation rather than continue selector micro-gates.

Durable artifacts:
`experiments/gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.md`;
`experiments/gan2026_consensus_fresh_agreement_selector_v0_9_semantic_equiv_unknown_synthetic_stress_2026-06-15.md`.

### v0.9 residual component-generation audit (2026-06-15)

The final follow-up audit decomposes the remaining v0.9 selected validation
errors by component availability and clinical failure type. It is validation-only
over saved selector rows; it does not read locked test rows and does not make
model calls.

Summary:

- v0.9 selected correct: `733/750`;
- selected wrong: `17/750`;
- correct component available but not selected: `6` rows (`5` fresh-only,
  `1` consensus+fresh);
- no correct deterministic, consensus, or fresh-evidence component available:
  `11` rows;
- selector-only oracle ceiling with current components: `739/750`;
- no-correct residual categories include last-event/seizure-free
  over-inference on unknown-boundary rows (`6`), quantified-rate
  over-inference on unknown-boundary rows (`5`), cluster-burden component
  failures (`2`), and denominator/window or highest-semiology conflict (`1`).

This audit incorporates Yujian's unknown-frequency clarification at the design
level: when either seizure count or the relevant time period is unclear,
`unknown` is usually safer than inferring a rate or seizure-free duration from a
last-event date. The residual shows the selector has only small remaining
headroom with the current component pool. The larger problem is that multiple
components still over-read last-event/no-seizures-since/current-rate snippets or
drop the cluster axis before the selector sees a viable answer.

Decision: revise and pivot. Stop adding selector micro-gates unless a future
feature is predeclared and stress-tested; the next meaningful work should be
component generation for unknown-boundary preservation, seizure-free
over-inference suppression, denominator/window discipline, and cluster-burden
representation.

Durable artifacts:
`experiments/gan2026_consensus_fresh_agreement_selector_v0_9_residual_component_generation_audit_2026-06-15.md`.

### v0.10 component-repair probe (2026-06-15)

The residual audit made a tempting deterministic component-repair hypothesis
obvious: rewrite fresh-evidence last-event/seizure-free over-inferences to
`unknown`, then let the existing v0.9 selector accept the repaired component
where appropriate. v0.10 tests that hypothesis as a validation-only no-call
replay over saved v0.9 selector rows. It does not read locked test rows and does
not make model calls.

Stop rule: reject any repair with selected correct-to-wrong regressions or lower
selected Purist; revise only for zero-regression selected gain.

Results:

| Repair rule | Repairs | Selected Purist | Delta vs v0.9 | Selected W->C | Selected C->W | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| seizure-free last-event to unknown | 20 | 725/750 | -8 | 3 | 11 | reject |
| last-event plus unclear-count markers to unknown | 3 | 733/750 | 0 | 0 | 0 | diagnostic/no gain |
| any last-event seizure-free/frequency to unknown | 48 | 723/750 | -10 | 4 | 14 | reject |

Decision: reject broad deterministic last-event-to-unknown component repair. It
does recover some supervisor-style unknown-boundary rows, but it damages many
validation rows where seizure-free is Purist-correct. The next component
generation attempt should be model-owned: require an explicit ambiguity
classification before final-label rendering, with a hard-negative panel that
contrasts last-event-only ambiguity against true seizure-free duration and
explicit count-plus-window cases.

Durable artifacts:
`experiments/gan2026_consensus_fresh_agreement_selector_v0_10_component_repair_probe_2026-06-15.md`.

### Ambiguity-classification component contract (2026-06-15)

The v0.10 probe rejects deterministic after-the-fact repair, so the next
component-generation design moves the ambiguity decision into the model-owned
fresh-evidence output. `fresh_evidence_reasoner` now accepts an optional
`ambiguity_classification` field before final-label rendering. The schema values
separate:

- `unknown_count_or_window`;
- `last_event_only_unknown`;
- `explicit_count_window`;
- `explicit_seizure_free_duration`;
- `cluster_axis_incomplete`;
- `cluster_axis_complete`;
- `no_seizure_frequency_reference`;
- `not_applicable`.

The safety gate now allows selective `unknown` replacements when the model
explicitly classifies the case as `unknown_count_or_window`,
`last_event_only_unknown`, or `cluster_axis_incomplete`. This keeps the
supervisor's ambiguity rule model-owned rather than turning it into a broad
profile-string rewrite.

A supervisor-seeded validation-only panel encodes the six clarified examples:

| Row | Supervisor label | Expected component label | Ambiguity class |
| ---: | --- | --- | --- |
| 11272 | `unknown` | `unknown` | `last_event_only_unknown` |
| 14454 | `2 per 2 month` | `2 per 2 month` | `explicit_count_window` |
| 14029 | `unknown` | `unknown` | `unknown_count_or_window` |
| 13267 | `2 per 5 month` | `2 per 5 month` | `explicit_count_window` |
| 14137 | `unknown` | `unknown` | `unknown_count_or_window` |
| 11337 | `unknown` | `unknown` | `unknown_count_or_window` |

Result: the parser/safety-gate contract passes `6/6`. This is not a promoted
candidate and it does not authorize a new `test450` audit. It is the first
hard-negative gate for any future live ambiguity-aware component-generation run.

Important protocol consequence: the historical V12 v0.6/safety-v0.9 frozen
preflight now correctly fails because `fresh_evidence_reasoner.py` and
`tests/test_gan2026_fresh_evidence_reasoner.py` have changed from the pinned
hashes. A future holdout-facing run would require a new frozen protocol after
validation evidence, plus explicit user authorization.

Durable artifacts:
`experiments/gan2026_unknown_frequency_ambiguity_panel_2026-06-15.md`.

After DeepSeek became available, the exact three-agent consensus replay was
checked aggregate-only with the symmetric source panel: `366/450` Purist, only
one row above the prior constrained two-agent `365/450`. The symmetry gap is
closed; the consensus family remains far below the `0.900` holdout target.

## Source artifacts

- `docs/research/gan2026_hybrid_structured_events_agentic_consensus_fresh_evidence_analysis_2026-06-14.md`
- `experiments/gan2026_agentic_structured_event_consensus_unanimous_exact_validation750_2026-06-13.md`
- `experiments/gan2026_agentic_structured_event_consensus_available_two_agent_exact_test450_2026-06-13.md`
- `experiments/gan2026_fresh_evidence_reasoner_safety_v0_4_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_3_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_4_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_4_hard_slice_audit_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_4_synthetic_component_stress_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_4_unknown_origin_relaxation_probe_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_5_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_5_boundary_rescue_audit_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_5_boundary_rescue_synthetic_stress_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_6_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_6_boundary_rescue_synthetic_stress_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_7_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_7_unknown_count_window_synthetic_stress_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_7_residual_headroom_audit_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_8_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_8_parseable_refinement_synthetic_stress_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_semantic_equiv_unknown_synthetic_stress_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_residual_component_generation_audit_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_10_component_repair_probe_2026-06-15.md`
- `experiments/gan2026_unknown_frequency_ambiguity_panel_2026-06-15.md`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/structured_event_consensus.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/family_transitions.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/family_cv_promotion.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/precision_gated_selector.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/consensus_fresh_agreement_selector.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/fresh_evidence_reasoner.py`
- `tests/test_gan2026_agentic_structured_event_consensus.py`
- `tests/test_gan2026_family_transitions.py`
- `tests/test_gan2026_consensus_fresh_agreement_selector.py`
