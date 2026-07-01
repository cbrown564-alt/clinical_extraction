> **Status: HISTORICAL** — design record only. See [`ACTIVE_ROADMAP.md`](ACTIVE_ROADMAP.md) and [`recent_plan_rationalisation_2026-06-25.md`](recent_plan_rationalisation_2026-06-25.md).

# Evidence-Validity Unification — Review, Categorise, Unify, Re-run

**Date:** 2026-06-27
**Task:** Cross-task reliability — one canonical evidence-groundedness metric for gan2026, ExECTv2, and future tasks
**Status:** Executed 2026-06-27 — canonical metric in `core/evidence.py`; see [`docs/reference/evidence_groundedness_metric.md`](../reference/evidence_groundedness_metric.md).
**Author:** Design pass on current `main`

---

## Executive summary

Today "evidence validity" is computed **three different ways under two different names**, all using a raw `evidence in note_text` substring test with **no formatting repair** — even though a rich, semantically-neutral repair cascade already exists in `core/evidence.py` and is used elsewhere (offset location, the fresh-evidence gate). The consequence is that a model which **cites the correct source span but introduces a neutral formatting quirk** (mojibake `≤`, case drift, collapsed whitespace, an `…` omission) is scored as *invalid* identically to a model that *hallucinates* evidence. This is the Qwen failure: it grounds its labels in real note text but loses ~17–21 points of measured validity to formatting (validation750: Qwen `evidence_valid` 74.8% / `evidence_text_contained` 76.5% vs GPT-4.1-mini / DeepSeek 92–96%).

This plan: (1) **defines one canonical metric** — *evidence groundedness* — in `core/evidence.py`, graded into a small fixed taxonomy; (2) **categorises invalid evidence** so "quirk" is separated from "absent"; (3) **replaces all three call sites** with the one function so the metric is identical everywhere and inherited by future tasks for free; (4) **re-runs the metric as a pure saved-output replay** (no new model calls) over the registry and reports corrected rates, with the gate-behaviour change deliberately quarantined from the metric fix.

The ethos is *lean*: one number, one function, one name, one doc. We are fixing a **fidelity/presence** metric (does the cited text exist in the source, modulo neutral formatting), **not** inventing a semantic-support judge.

---

## Problem statement

### The metric diverges across three call sites

| # | Site | Code | Name emitted | Repair applied? |
|---|------|------|--------------|-----------------|
| 1 | gan2026 hybrid / agentic | `agentic/llm_event_reasoner.py:962` `_decision_evidence_valid` → `all(evidence_is_substring(...))` | `evidence_valid` | **No** |
| 2 | gan2026 llm-only canonical | `runners/llm_only_canonical.py:45` `evidence_is_substring(...)` | `evidence_text_contained` | **No** |
| 3 | ExECTv2 lenses | `assembly/lens_ops.py:247` `evidence_valid = evidence in store.note_text` (inline; does not even call the shared helper) | `evidence_valid` | **No** |

Three problems compound:

1. **Two names for one concept.** `evidence_valid` vs `evidence_text_contained` are the *same computation* but were declared "deliberately distinct, do not compare across architectures" (see the registry surface rows). That footnote is a workaround for an accidental divergence, not a real semantic difference.
2. **Raw substring, no repair.** All three use bare `in` / `evidence_is_substring`, which is `evidence in note_text`. None apply `repair_evidence_text_if_source_exact`.
3. **The repair cascade already exists and is trusted elsewhere.** `core/evidence.py` has `repair_evidence_text_if_source_exact()` covering mojibake/control artifacts (`SEMANTICALLY_NEUTRAL_TEXT_ARTIFACTS` — literally the Qwen `≤` byte sequences), case-only drift, flexible whitespace, `…`/`...` span omission, and `header + list-item` composition. `locate_evidence()` uses it to anchor offsets, and `fresh_evidence_reasoner.py:1634` uses strict matching to *gate*. So the codebase already treats repaired spans as source-exact for **anchoring** but not for **scoring validity** — an internal inconsistency.

### Why Qwen is the canary, not the exception

Qwen-3.6 (local) emits semantically-correct evidence with neutral copy artifacts (control-char `≤`, casing, whitespace). The raw metric counts these as invalid, depressing its validity rate while its *accuracy* is competitive (it led validation750 Purist at 0.851). The same artifact class can appear from any model; Qwen just produces it most often. Fixing the metric for Qwen fixes it for everyone and removes a model-specific apologetic footnote from the registry.

### Scope boundary (what this is NOT)

- Not a semantic-entailment / "does this evidence *support* the label" judge. That is a separate, larger reliability question (semantic entropy, faithfulness). This metric answers only: *is the cited text present in the source, allowing semantically-neutral formatting repair?*
- Not a change to any prediction or accuracy number — **the metric recompute is replay-only**. Any change to gating behaviour (which *can* move predictions) is a separate, optional, gated follow-on (Phase 5), not part of the metric unification.

---

## Phase 0 — Audit & taxonomy (read-only, no code change)

**Goal:** quantify, with evidence, how much of the current "invalid" mass is recoverable quirk vs genuine absence — before changing the metric.

Build a one-off audit script (`reports/evidence_validity_audit.py`, replay-only) that, for each saved per-row artifact carrying evidence + a resolvable `note_text`:

1. Extracts every cited evidence string (gan2026: from `structured_record` / `normalized_events` / `raw_output`; ExECTv2: from `predicted_mentions` / `prediction_surfaces` / `raw_lane_mentions`).
2. Resolves `note_text` from the dataset via `source_row_index` (gan2026) / `letter_id` (ExECTv2).
3. Classifies each evidence string into the taxonomy below.
4. Emits per-model, per-task counts + a sample of 5 real strings per category.

**Proposed invalid-evidence taxonomy** (fixed, small, maps onto the existing repair cascade):

| Grade | Meaning | Counts as grounded? | Existing cascade hook |
|-------|---------|:-------------------:|-----------------------|
| `EXACT` | Verbatim substring of note | ✅ | `evidence_is_substring` |
| `REPAIRED_ARTIFACT` | Source-exact after mojibake/control-char normalisation | ✅ | `clean_semantically_neutral_text_artifacts` |
| `REPAIRED_CASE` | Source-exact after case-only repair | ✅ | `repair_case_only_evidence_copy` |
| `REPAIRED_WHITESPACE` | Source-exact after whitespace flex | ✅ | `repair_whitespace_evidence_copy` |
| `REPAIRED_ELLIPSIS` | Bounded `…` span omission, both ends source-exact | ✅ | `repair_ellipsis_span_evidence_copy` |
| `REPAIRED_SECTION` | `header + list-item` composition present in one source section | ✅ | `repair_section_header_list_item_evidence_copy` |
| `ABSENT` | Not found even after all repairs (paraphrase / hallucination / cross-note) | ❌ | — |
| `EMPTY` | No evidence string provided | ❌ | — |

**Decision rule:** *grounded* = any `EXACT` or `REPAIRED_*` grade. The headline validity number is the **grounded rate**; the `EXACT`-only rate is retained as a transparency sub-metric so we can still see raw copy fidelity per model.

**Phase 0 deliverable:** `docs/experiments/reliability/evidence_validity_audit_2026-06-27.md` — the before-picture: for each surfaced/promoted run, the split of current "invalid" rows across `REPAIRED_*` (recoverable) vs `ABSENT`/`EMPTY` (genuinely ungrounded). This is the evidence that the metric, not the model, is the problem.

---

## Phase 1 — The canonical metric (one function, `core/`)

Add to `src/clinical_extraction/core/evidence.py` (task-agnostic by construction):

```python
class EvidenceGrade(StrEnum):
    EXACT, REPAIRED_ARTIFACT, REPAIRED_CASE, REPAIRED_WHITESPACE,
    REPAIRED_ELLIPSIS, REPAIRED_SECTION, ABSENT, EMPTY

GROUNDED_GRADES: frozenset[EvidenceGrade]  # EXACT + all REPAIRED_*

def grade_evidence(note_text: str, evidence: str) -> EvidenceGrade: ...
def is_grounded(grade) -> bool: ...

@dataclass(frozen=True)
class EvidenceGroundedness:
    total: int
    grounded: int          # exact + repaired
    exact: int             # transparency sub-metric
    by_grade: dict[EvidenceGrade, int]
    per_item: tuple[tuple[str, EvidenceGrade], ...]
    @property
    def grounded_rate(self) -> float | None: ...
    @property
    def exact_rate(self) -> float | None: ...

def score_evidence_set(note_text: str, evidence: str | Sequence[str]) -> EvidenceGroundedness: ...
```

Design rules:

- `grade_evidence` reuses the **existing** repair functions in priority order (artifact → case → whitespace → ellipsis → section); it never introduces a new normalisation. The repair-cascade guarantee ("only returns when the result is a source-exact span") is what keeps every `REPAIRED_*` grade semantically safe.
- **Input contract is uniform**: `(note_text: str, evidence: str | list[str])`. A single string grades to one `EvidenceGrade`; a set yields `EvidenceGroundedness`. This is the only contract every task adopts.
- The single number every caller reports is **`grounded_rate`**. The name is **`evidence_grounded_rate`** everywhere — retiring both `evidence_valid` and `evidence_text_contained` as the public metric name (the boolean per-row field may stay as `evidence_grounded` for back-compat in artifacts).
- Pure function, no I/O, fully unit-testable.

**Tests:** `tests/test_core_evidence_groundedness.py` — one fixture per taxonomy grade (real Qwen `≤` artifact, a case-drift, a whitespace-collapse, an `…` omission, a header+item, a genuine hallucination, empty), asserting grade + grounded boolean. Lock the grounded/exact split so future cascade edits can't silently move the metric.

---

## Phase 2 — Replace the three call sites (behaviour-preserving for predictions)

Swap each site to the shared function. **None of these change a prediction or a label** — they change only the *reported metric* and its name.

| Site | Change |
|------|--------|
| `agentic/llm_event_reasoner.py:962` `_decision_evidence_valid` | Delegate to `score_evidence_set(note_text, decision.evidence).grounded_rate`/boolean; keep the field but populate from the shared grade. |
| `runners/llm_only_canonical.py:45` | Replace `evidence_text_contained` with `evidence_grounded` via the shared function; drop the bespoke name. |
| `assembly/lens_ops.py:247` (+ the other inline `evidence in note_text` lens sites) | Replace inline `in` with `is_grounded(grade_evidence(...))`; ExECTv2 lenses now inherit the repair cascade. |

Add a thin per-run aggregator (or extend the existing reporting) so every run emits `evidence_grounded_rate` + `evidence_exact_rate` + `by_grade` counts in one consistent block.

**Guard:** `fresh_evidence_reasoner.py:1634` uses strict matching as a **functional gate** (it filters non-exact evidence and can trigger fallback). Phase 2 must **leave that gate's behaviour byte-for-byte unchanged** — we only re-point the *metric*. Widening the gate to accept repaired spans is Phase 5, explicitly separated, because it can move predictions and therefore needs the holdout protocol.

---

## Phase 3 — Re-run (replay recompute, no new model calls)

Recompute `evidence_grounded_rate` over saved artifacts — this is a metric replay, not a model re-run, so it needs no budget and touches no holdout protocol.

1. Run the Phase 0 harness in "write" mode over every registry artifact that carries evidence + resolvable note_text, producing the unified `evidence_grounded_rate` (+ `exact_rate`, + `by_grade`).
2. **Priority set:** the 9 `promote` + 6 `surface_as_architecture: true` rows, then the wider registry.
3. Produce a **before/after table** (raw `evidence_valid`/`evidence_text_contained` → unified `evidence_grounded_rate`), with the Qwen rows called out specifically (expect 74.8% / 76.5% to rise toward the closed-model band as `REPAIRED_*` reclassifies).
4. Update each affected registry row's `evidence_validity` prose **and** `primary_metrics` to the single metric, keeping the old number in a `superseded` note for provenance (registry is append-aware; do not silently rewrite history — annotate).

**Replay-validity discipline:** recompute reads only saved outputs + dataset note text; gold labels are not consulted; no model is called; frozen/locked test rows keep their aggregate-only contract (recompute the rate, do not surface row-level test evidence).

---

## Phase 4 — Documentation (one canonical doc)

- `docs/reference/evidence_groundedness_metric.md` — the single source of truth: definition, the 8-grade taxonomy, the grounded vs exact distinction, the input contract, "what it does NOT measure" (semantic support), and a worked Qwen example showing a `REPAIRED_ARTIFACT` that the old metric failed. Link it from both task plan trees (`docs/plans/exectv2/`, gan2026 reliability docs).
- Short ADR note: *why* repaired-after-neutral counts as grounded (the repair cascade only returns source-exact spans), and why we collapsed two metric names into one.
- Update the registry schema note so future runs emit `evidence_grounded_rate` by default.

---

## Phase 5 (optional, separated) — Gate widening, under protocol

Only after the metric ships: consider widening the `fresh_evidence_reasoner` evidence gate (and any ExECTv2 evidence filter) to accept `REPAIRED_*` spans (storing the repaired span, mirroring what `locate_evidence` already does). This **can move predictions**, so it is **not** part of the metric unification and must go through the standard preflight + frozen-holdout protocol (`cli/frozen_test_preflight_single_model.py`, aggregate-only test readout). Treat as a follow-on experiment with its own predeclaration, not a refactor.

---

## Risks & decisions

| Risk / decision | Resolution |
|-----------------|------------|
| Repair cascade over-reaches and grades a genuine hallucination as grounded | Cascade only returns source-exact spans by construction; Phase 0 samples + Phase 1 fixtures lock the boundary. |
| Changing the metric silently changes accuracy on frozen/promoted runs | Phases 1–3 are metric-only/replay-only; gating change is quarantined to Phase 5 under protocol. |
| Two historical metric names break dashboards/registry consumers | Keep `evidence_grounded` per-row boolean for back-compat; map old names → new in one shim; annotate (don't erase) superseded registry numbers. |
| ExECTv2 lenses gain the cascade and shift their reported rate | Expected and desired; report before/after; no prediction change since lens validity is a label on already-selected findings. |
| Frozen/locked test rows | Recompute aggregate rate only; never surface row-level test evidence. |

**Open decision for the user:** the headline number — recommend **grounded rate** as the single published metric, with **exact rate** retained as a visible sub-metric (so raw copy fidelity per model is still legible). Alternative is to publish exact-only and treat grounded as diagnostic; not recommended, as it reproduces the current Qwen artifact.

---

## Acceptance criteria

1. One function in `core/evidence.py` is the **only** place evidence validity is computed; the three call sites delegate to it; `grep` finds no remaining bespoke `evidence in note_text` / `evidence_text_contained` validity computation.
2. A single metric name (`evidence_grounded_rate`) is emitted by every gan2026 and ExECTv2 run, with `exact_rate` + `by_grade` alongside.
3. The 15 surfaced/promoted rows are re-scored under the unified metric, with a documented before/after and the Qwen gap explained by `REPAIRED_*` reclassification (not lost).
4. One canonical doc + taxonomy exists and is linked from both task trees; the "do not compare across architectures" footnote is retired.
5. Tests lock every taxonomy grade; the full offline suite still passes; **no prediction or accuracy number changes** as a result of Phases 1–4.

---

## Essential-detail summary (the whole thing in five lines)

- **One metric:** *evidence groundedness* = cited text present in source, allowing semantically-neutral repair. Headline = **grounded rate**; keep **exact rate** for transparency.
- **One function:** `core/evidence.py::score_evidence_set`, reusing the existing repair cascade. Input contract `(note_text, evidence)` everywhere.
- **One taxonomy:** EXACT · REPAIRED_{ARTIFACT,CASE,WHITESPACE,ELLIPSIS,SECTION} · ABSENT · EMPTY.
- **One re-run:** replay-only recompute over saved artifacts; no new calls; gate change quarantined to a separate protocol-gated phase.
- **One doc:** `docs/reference/evidence_groundedness_metric.md`, retiring the `evidence_valid` vs `evidence_text_contained` split.
