# `Diagnosis:diagnosis_residual_additions` model-compensation removal study — result

Date: 2026-08-11
Status: **complete — KILLED (rule kept), compensation pattern holdout-confirmed**
Protocol: recovered from git history; this report is the answer.
Parent finding: [model-compensating rule audit](../shared/model_compensating_rule_audit_2026-08-11.md)
Dev140 mechanism ledger (reused, not repeated): 2026-08-10 audit note pruned; recover from Git history / [artifact](../../experiments/exectv2_diagnosis_residual_additions_mechanism_audit_20260810.json)
New artifacts: [`test59` study](../../experiments/exectv2_diagnosis_residual_additions_test59_20260811.json)
Runner: [`removed in the 2026-08-16 scripts prune; recover from git history (was `scripts/check_exectv2_diagnosis_residual_additions_test59.py`)`](../../removed in the 2026-08-16 scripts prune; recover from git history (was `scripts/check_exectv2_diagnosis_residual_additions_test59.py`))

## Plain answer

**Full removal is correctly KILLED, as predicted — but the reason matters.**
The rule was hypothesized to be dev140-memorization (53 hard-coded regex
patterns matching literal note phrasing) whose apparent weak-model
compensation might evaporate on notes it wasn't written against. That
hypothesis is **refuted**: the pattern set fires on 67.8% of `test59`
letters, essentially the same rate as `dev140`'s 70.7% (raw per-letter
firing, not the post-dedup 213/830 "changed cells" figure — see note below).
More importantly, **the compensation pattern itself replicates on holdout**:
Gemma 4 26B — the weakest model — is again the standout beneficiary of
keeping the rule (removing it costs Gemma -0.0523 F1 **and** -0.0351
exactness, the only model where removal makes exact-match worse too), while
GPT-5.6 Sol/Luna and DeepSeek lose far less F1 (-0.011 to -0.017) and are
flat-to-positive on exactness. This is not dev140 overfitting; it is a real,
durable, holdout-confirmed weak-model compensation effect. No removal or
scoped variant is authorized by this study; the rule stays as-is.

## Phase 1 — reused, not repeated

The row-level mechanism audit predeclared for Phase 1 already existed
(`diagnosis_residual_additions_mechanism_audit_2026-08-10.md` (pruned),
written the day before the model-compensating rule audit but not
cross-referenced until now — see "process note" below). Its per-cell ledger
carries `model_slug`, so the per-model breakdown Phase 1 asked for could be
computed directly from the existing artifact with zero new replay:

| Model | Help | Harm | Net | Competence (LLM-only) |
| --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Sol | 11 | 11 | 0 | 0.78 |
| DeepSeek V4 Flash | 12 | 11 | +1 | 0.78 |
| GPT-5.6 Luna | 15 | 10 | +5 | 0.76 |
| GPT-4.1-mini | 14 | 6 | +8 | 0.73 |
| Qwen 3.6 35B | 16 | 8 | +8 | 0.73 |
| Gemma 4 26B | 16 | 8 | +8 | 0.69 |

A clean monotonic gradient (net help rises as competence falls), corroborating
the F1-delta correlation finding (r=-0.932) from the parent audit at
cell-count granularity. `gold_supported` in the existing ledger is a perfect
predictor of effect direction (every `help` cell is gold-supported; every
`harm` cell is not) — there is no ambiguous-classification burden here, unlike
the general Diagnosis gold-multiplicity finding elsewhere.

**The existing audit already identified a targeted deletion candidate:**
remove 4 specific "broadening" patterns (ids 47/55/46/38: `focal seizures`,
`generalised seizures`, `focal seizures with altered awareness`,
`generalised epilepsy`) that have zero observed help and all-harm. Re-checked
against the model breakdown here: those 4 patterns' harm is spread roughly
evenly across all 6 models (4-8 harm cells each, no help cells anywhere), so
removing them would **not** resolve the compensation skew — the skew lives in
the other 53 (mostly helpful) patterns, not the 4 flagged ones. That
candidate remains a legitimate, separate simplification (recovers pure harm
uniformly) but is orthogonal to the compensation question this study asks.
It was not re-tested here; it retains its own `dev140`-only status from the
2026-08-10 audit pending its own holdout confirmation.

## Phase 2 — test59 holdout (aggregate-only, this session)

### Firing-rate transfer check

| | dev140 (reference, raw per-letter) | test59 |
| --- | ---: | ---: |
| Letters firing | 99/140 (70.71%) | 40/59 (67.80%) |
| Cells firing | — | 240/354 (67.80%, identical per model since firing depends only on note text) |

**Important correction made during this run:** the protocol's originally
planned baseline was the `dev140` decomposition's 213/830 "changed cells"
figure (25.7%) — that undercounts true firing because it only counts matches
that survived de-duplication and changed the final assembled set. Recomputed
the dev140 reference the same way as test59 (raw pattern match against note
text, before dedup): 70.71%. Against the correct baseline, test59's 67.80%
is a ~4% relative drop, not the order-of-magnitude collapse the
memorization hypothesis predicted. **Verdict: TRANSFERS.**

### Removal-arm accuracy delta

| Model | Cells | Changed | Exactness Δ (removed − kept) | Micro-F1 Δ | Confirmed? |
| --- | ---: | ---: | ---: | ---: | --- |
| Whole panel | 352 | 43 | +0.0028 | **-0.0240** | No |
| GPT-4.1-mini | 59 | 6 | +0.0169 | -0.0157 | No |
| GPT-5.6 Luna | 59 | 4 | +0.0000 | -0.0155 | No |
| GPT-5.6 Sol | 59 | 5 | +0.0169 | -0.0112 | No |
| DeepSeek V4 Flash | 59 | 5 | +0.0169 | -0.0174 | No |
| Qwen 3.6 35B | 59 | 8 | +0.0000 | -0.0349 | No |
| Gemma 4 26B | 59 | 15 | **-0.0351** | **-0.0523** | No |

Every model fails the F1 tolerance (`>= -0.005`); Gemma additionally fails on
exactness (only model where removal makes exact match worse, not just F1).
**VERDICT: KILLED** — matches the a priori expectation stated in the
protocol (dev140 already showed this outcome in-sample) and, more
informatively, replicates the exact same weak-model-skewed shape out of
sample.

### Fidelity

336/352 (95.5%) of baseline (rule-kept) replayed cells matched the retained
sealed predictions exactly — in the same range as the parent family-lens
decomposition's 97.6% but not identical; noted as a caveat, not investigated
further (aggregate-only row policy prohibits inspecting which letters
diverge).

## Process note

This protocol's Phase 1 was written without first finding
`diagnosis_residual_additions_mechanism_audit_2026-08-10.md` (pruned), which
had already done the row-level ledger work one day earlier under a different
naming pattern. It surfaced only when starting to execute Phase 1 and finding
`removed in the 2026-08-16 scripts prune; recover from git history (was `scripts/audit_exectv2_diagnosis_residual_additions.py`)` already in the repo.
No harm resulted — the existing artifact had exactly the per-cell data needed
and was reused rather than duplicated — but it is a reminder to search
`docs/research/*2026-08-10*` and `scripts/*diagnosis_residual*` more broadly
before predeclaring a study, not just the three artifacts the parent audit's
protocol named.

## Recommendations

1. **No rule change.** `diagnosis_residual_additions` stays as-is; removal is
   KILLED on both dev140 and test59, and the compensation it provides is
   real and durable, not an artifact of dev-set memorization.
2. ~~The separate, narrower "remove 4 zero-help broadening patterns"
   simplification... remains a live, distinct candidate~~ **Correction
   (2026-08-11, same day): already landed.** Checking the git history found
   this was committed in the same commit that produced the 2026-08-10
   mechanism audit (`e6d3960e`) — the current 53-pattern array already has
   these 4 patterns removed. It was never run through this project's own
   predeclared holdout process before landing (a process gap, low risk given
   it targeted pure zero-help harm), but is not an open item.
3. **New finding, also closed same day:** that same commit tried to add a
   subsumption safeguard for the one remaining problem pattern
   (`generalised tonic clonic seizures` matched from headings, help:harm 8:12
   on dev140) but the guard is dead code — a string-equality check against a
   value `canonicalize_diagnosis_concept` can never produce. A predeclared
   fix study
   (subsumption-guard fix notes pruned; recover from Git history)
   found the naive one-line correction is **not safe**: it rescues 15 dev140
   cells but loses 4, all on one letter where gold wants both the plain and
   "secondary generalised" tonic-clonic labels simultaneously. **REFUTED at
   Phase 1; guard stays dead; not landed.**
4. No scoped/weak-model-gated variant is authorized by this study (the
   protocol's "no tuning" clause) — that remains a hypothesis, not a tested
   result, and would need its own predeclaration if pursued.
5. The broader implication for the model-compensating rule audit: not every
   compensating rule is dev-overfit noise. This one is genuine and durable.
   The audit's job was to flag candidates for scrutiny, not to presume they
   are all bugs — this result is exactly that scrutiny working as intended.

## Claim boundary

Single predeclared aggregate-only `test59` study. No holdout row inspection
(letter IDs, note text, and predictions stayed in `scratch/`/process memory
only; only counts and deltas are in the artifact). Not clinical validation,
not the published ExECT benchmark, not a re-opening of the broader Diagnosis
lens. Confirms the existing default; does not change any shipped rule or
scored artifact.
