# ExECTv2 pipeline assumption audit — Phase 4 standing guardrail

Date: 2026-07-02. Owner: ExECTv2 workstream.
Plan: `docs/plans/exectv2_pipeline_assumption_audit_plan_2026-07-02.md` (Phase 4).
Phase 0 inventory: `docs/research/exectv2_pipeline_assumption_audit_2026-07-02.md`.
Phase 1 fixes: `docs/research/exectv2_pipeline_assumption_audit_phase1_2026-07-02.md`.

## Purpose

Phases 0–1 found and fixed a bounded class of same-mistake scorer bugs: *a fact's
scored `clinical_headline` membership depended on text or facts outside that
fact's own clause/scope* (the "seed defect"). The loudest instance was the
Prescription full-span future/weight regex. Phase 4 is the "once and for all"
half: mechanisms that make the *next* latent instance of this class surface **at
commit time**, so the reactive, one-family-at-a-time discovery pattern is ended
structurally rather than by intention. This phase is free — no LLM runs.

## What was built (4 items)

### 1. Scorer-invariant property tests — `tests/test_scorer_scope_invariants.py`

Encodes the seed defect as a general, family-agnostic invariant and tests every
family's `clinical_headline_unit_keys` builder against it. Two complementary
statements:

- **Note-context invariance (all four families).** Appending an unrelated
  trailing sentence to `note_text` must not change any family's headline key set.
  This is the clean statement of "text outside the fact's own scope" and it holds
  for Prescription, SeizureFrequency, Investigations, and Diagnosis.
- **Clause-scope invariance (Prescription — the load-bearing case).** Appending
  future/titration ("to reduce and stop") or weight ("60mg/kg/day") language
  *after* a current-dose clause inside `annotation.text` must not change headline
  membership. The keys are asserted equal to the clean span's, and non-empty.

The invariant is proven **load-bearing** by a local re-implementation of the
pre-fix full-span check (`_old_full_span_is_future` / `_old_full_span_is_weight`):
the same perturbation flips membership `in → out` under the old logic (`False`
on the clean span, `True` on the perturbed span) while the current clause-scoped
scorer keeps both — so the assertions are not vacuous.

Per-family scope boundaries the tests pin down (a durable finding worth stating,
because it explains *why* the invariant takes two forms):

| Family | Headline key derived from | "Outside the fact's scope" channel tested |
| --- | --- | --- |
| Prescription | name+dose+frequency **attributes**, gated by clause-scoped text predicates | trailing titration/weight text *and* `note_text` |
| SeizureFrequency | seizure-type CUI + count **attributes** | trailing phrase text *and* `note_text` |
| Investigations | modality + performed/result **attributes** | trailing phrase text *and* `note_text` |
| Diagnosis | the canonicalized concept **phrase itself** | `note_text` only — the phrase *is* the fact's clause |

Diagnosis is the instructive asymmetry: its headline unit *is* the annotation
phrase, so appending a coordinated concept legitimately adds a key (a new fact,
not out-of-clause noise), whereas the surrounding note never contributes one. The
test documents this so a future change that made the Diagnosis key read note
context, or silently absorbed appended text into one concept, would fail.

### 2. Scorer/projection consistency test — `tests/test_scorer_projection_consistency.py`

Fails if the future/weight-based decision is ever again made at a different text
scope in the scorer than in its projection twin
(`deterministic/conventions/prescription.py`, whose truncate-at-cue at L266-268 is
the reference clause-scope implementation). Constructs spans where a naive
**full-span** reading (cue anywhere → drop) and a **clause-scope** reading
(current dose before the cue → keep) give opposite answers, then asserts the
scorer's `clinical_headline` membership decision matches
`prescription_residual_additions`'s current-regimen retention decision
construct-by-construct. Cases use future cues shared by both layers' vocabularies
("to reduce", "increase to", "reducing") and whitelisted drug/dose/frequency
tuples, so the only free variable is text scope. A guard test asserts the RETAIN
constructs genuinely contain a cue (so the reconciliation is not tested vacuously).

### 3. Edit-triggers-predeclaration gate — `scripts/check_scorer_edit_predeclaration.py`

Given changed paths (positional args or `--stdin` from `git diff --name-only`) and
a commit/PR message (`--message`/`--message-file`), blocks (exit 1) when any path
is **guarded** — under `scoring/`, a deterministic projection file
(`conventions/*`, `*_projection*`, `sf_state_projection.py`,
`target_projection/*`), or `contract/drug_lexicon.py` — unless the message
references a `hypothesis_id` that **exists** in
`experiments/hypothesis_registry.jsonl` **and** mentions a **dev140 replay**. The
script never runs git itself. Behavior is covered by
`tests/test_scorer_edit_predeclaration_gate.py`; wiring (git `commit-msg` hook and
a PR-body CI step) is documented in
`docs/runbooks/scorer_edit_predeclaration_gate.md`.

CI/hook note: the gate needs the commit *message*, available only at the
commit-msg stage; the repo's existing pre-commit hooks run at the pre-commit stage
(filenames only). A one-line `.pre-commit-config.yaml` addition would therefore
lack the input it needs, so the wiring is **documented** (git `commit-msg` hook +
CI PR-body step) rather than bolted onto the existing hook block. This is the
deliberate documentation-over-hook branch the Phase-4 plan allows.

### 4. Mechanism-taxonomy-as-standing-lens + parked-items ledger

See the two sections below.

## Mechanism taxonomy is the standing lens

Future digs **must extend `experiments/exectv2_ledger/mechanism.py`** (the shared
`Mechanism`/`Verdict` enums) and feed the shared ledger, rather than inventing a
new bespoke local script. That module already consolidated four mutually
inconsistent per-script taxonomies (`H1_CARDINALITY`/`H2_GENUINE_DIVERGENCE`,
`NOT_SOURCE_NEAR_FN`, the ad hoc `H3_ORTHOGRAPHIC`); the seed defect's own class
now has a home there as `SCORER_MECHANICS_ARTIFACT`. Closing this loop is what
prevents the bespoke-script sprawl that made the seed defect discoverable only by
accident. Any new scorer-correctness finding should be adjudicated with these
enums and recorded through the ledger + `hypothesis_registry.jsonl`, not a
one-off script that agrees with no other.

## Parked items (explicitly deferred, with reason)

These were surfaced by the Phase 0 inventory but are **out of scope for Phase 4's
free guardrail work**. Each is parked with a one-line rationale so it is visible
and citable rather than silently dropped (satisfies success-criterion 3). None
moves a headline F1 that a Phase-1 fix already touched.

| ID | Layer / symbol | Why parked |
| --- | --- | --- |
| **P6** | `scoring/prescription.py` future/weight **keys** (L228-237) | Diagnostic-only (`future_medication`/`weight_based_dosing` components), not `clinical_headline`; whole-span phrase key under-credits but does not corrupt the headline number the manuscript cites. Fix is cosmetic to a diagnostic; no citation at risk. |
| **SF-2** | `scoring/seizure_frequency.py` `_frequency_state` vs `frequency_state_faithful` | Direction (more/fewer/improved/worse) is present in gold and producible but modelled by no headline key and scored by no metric. Closing it is a **schema + metric change** (a 5-way direction-aware state + a direction-sensitive metric), not a scope fix — squarely the Phase-6 SF finding, not a measurement bug. |
| **F2** | `scoring/match.py` `_first_overlapping_prediction` (L543) greedy `used_pred` | The greedy first-overlap match can let a short generic gold phrase steal the prediction a longer specific gold would match, distorting `source_near` overlap-recall + attribute-agreement. Needs an **optimal (non-greedy) matching** change **and** re-citation of the evidence-decomposition `source_near` numbers wherever they appear; both exceed the free guardrail scope. Flag on any re-cite of those numbers. |
| **P7** | `deterministic/all_entities/prescription.py` `_PRESCRIPTION_WEIGHT_BASED_CONTEXT.search(evidence)` (L162) | Producer-side (predict-time): a whole-evidence weight scope can skip every dose in that evidence before scoring sees it. Measuring the effect needs a **re-prediction** run, so it is gated behind a costed Phase-2-style probe, not a free replay. |
| **SF-5** | `deterministic/sf_state_projection.py` (+ `sf_unknown_suppression`) | Producer-side: both projections replicate the 3-way count-only state definition and can classify/suppress a `changed` fact as `unknown`. Reconciling them to the 4-way faithful definition is a producer change requiring **re-prediction** to measure, and is entangled with SF-2's schema decision. Park until SF-2 is decided. |

Parked items that are producer-side (P7, SF-5) or need a schema/metric decision
(SF-2, F2's optimal matching) should be picked up under the relevant costed phase,
not retro-fitted into the free guardrail. P6 is a diagnostic-only cosmetic fix
that can ride along with any future Prescription scorer touch **through the gate
above** (predeclare + dev140 replay).

## Test results (as run 2026-07-02)

`uv run python -m pytest tests/test_scorer_scope_invariants.py
tests/test_scorer_projection_consistency.py
tests/test_scorer_edit_predeclaration_gate.py -q` → **40 passed**. The gate CLI was
also exercised end-to-end (guarded-without-predeclaration → exit 1;
guarded-with-predeclaration+replay → exit 0; docs-only → exit 0).

Concurrency caveat: other agents were editing scoring/deterministic/contract
source in the same working tree during this phase. These tests were written
against the current post-Phase-1 interfaces and passed on that snapshot; the
orchestrator re-validates the whole suite after all edits land. Two pre-existing,
unrelated collection errors (`tests/test_doc_hygiene.py`; a gan2026 registry
import) are out of scope for this phase.

## Files created

- `tests/test_scorer_scope_invariants.py`
- `tests/test_scorer_projection_consistency.py`
- `tests/test_scorer_edit_predeclaration_gate.py`
- `scripts/check_scorer_edit_predeclaration.py`
- `docs/runbooks/scorer_edit_predeclaration_gate.md`
- `docs/research/exectv2_pipeline_assumption_audit_phase4_guardrail_2026-07-02.md` (this doc)

No `src/` file, registry, `PROJECT_STATUS.md`, dossier, manuscript, frontend, or CI
config was modified.
