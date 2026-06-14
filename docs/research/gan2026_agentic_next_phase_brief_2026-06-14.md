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
dedicated sections below. Steps 3 and 4 remain open design/experiment work.

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
and step 4 (panel/source symmetry hard-gate) remain open.

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

## Source artifacts

- `docs/research/gan2026_hybrid_structured_events_agentic_consensus_fresh_evidence_analysis_2026-06-14.md`
- `experiments/gan2026_agentic_structured_event_consensus_unanimous_exact_validation750_2026-06-13.md`
- `experiments/gan2026_agentic_structured_event_consensus_available_two_agent_exact_test450_2026-06-13.md`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/structured_event_consensus.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/family_transitions.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/family_cv_promotion.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/precision_gated_selector.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/fresh_evidence_reasoner.py`
- `tests/test_gan2026_agentic_structured_event_consensus.py`
- `tests/test_gan2026_family_transitions.py`
