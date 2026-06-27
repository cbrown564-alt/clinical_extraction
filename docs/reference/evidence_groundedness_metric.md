# Evidence Groundedness Metric

**Canonical reference** for cross-task evidence validity in gan2026, ExECTv2, and future tasks.

Implementation: `src/clinical_extraction/core/evidence.py` (`grade_evidence`, `score_evidence_set`).

---

## Definition

**Evidence groundedness** answers one question: *is the cited text present in the source note, allowing semantically-neutral formatting repair?*

The headline published rate is **`evidence_grounded_rate`** (grounded ÷ total cited evidence strings). The transparency sub-metric **`evidence_exact_rate`** retains raw verbatim copy fidelity (exact substring only).

**Grounded** = any `EXACT` or `REPAIRED_*` grade below. **Not grounded** = `ABSENT` or `EMPTY`.

This is a **fidelity/presence** metric. It does **not** judge whether evidence semantically supports the label (faithfulness / entailment is a separate reliability question).

---

## Input contract

Every caller uses the same pure function:

```python
score_evidence_set(note_text: str, evidence: str | Sequence[str]) -> EvidenceGroundedness
```

- Single string → one grade; sequence → aggregate `EvidenceGroundedness`.
- Per-row boolean back-compat field: `evidence_grounded` (all items grounded).
- Per-run summary: `evidence_grounded_rate`, `evidence_exact_rate`, `by_grade` counts.

Retired public metric names: `evidence_valid` and `evidence_text_contained` (same raw-substring computation, accidentally divergent naming). New runs emit the unified names only.

---

## Taxonomy (8 grades)

| Grade | Meaning | Grounded? | Repair hook |
|-------|---------|:---------:|-------------|
| `EXACT` | Verbatim substring of note | yes | `evidence_is_substring` |
| `REPAIRED_ARTIFACT` | Source-exact after mojibake/control-char normalisation | yes | `clean_semantically_neutral_text_artifacts` |
| `REPAIRED_CASE` | Source-exact after case-only repair | yes | `repair_case_only_evidence_copy` |
| `REPAIRED_WHITESPACE` | Source-exact after whitespace flex | yes | `repair_whitespace_evidence_copy` |
| `REPAIRED_ELLIPSIS` | Bounded `…`/`...` span omission, both ends source-exact | yes | `repair_ellipsis_span_evidence_copy` |
| `REPAIRED_SECTION` | `header + list-item` composition in one source section | yes | `repair_section_header_list_item_evidence_copy` |
| `ABSENT` | Not found after all repairs | no | — |
| `EMPTY` | No evidence string provided | no | — |

The repair cascade only returns spans that exist verbatim in the source after neutral normalisation — so every `REPAIRED_*` grade is semantically safe to count as grounded for **scoring**. Functional **gates** that filter evidence before prediction may still require exact match (Phase 5, protocol-gated).

---

## Worked example — Qwen `≤` artifact

**Note text (excerpt):** `overall a frequency of ≤ four seizures per week`

**Model evidence (copy quirk):** `overall a frequency of \x026 four seizures per week`

| Metric | Result |
|--------|--------|
| Old exact-substring (`evidence_valid` / `evidence_text_contained`) | **invalid** |
| Unified `grade_evidence` | `REPAIRED_ARTIFACT` → **grounded** |

On validation750 surfaced Qwen rows, this artifact class explains most of the gap between ~75% exact-valid and ~91–95% grounded (replay recompute 2026-06-27; see [evidence groundedness reconciliation](../experiments/reliability/evidence_groundedness_reconciliation_2026-06-27.md)).

---

## ADR — why one metric, why repaired counts as grounded

1. **One function, one name.** Three call sites previously computed the same raw `in` test under two names (`evidence_valid` vs `evidence_text_contained`). The divergence was accidental, not semantic. Collapsing to `evidence_grounded_rate` removes cross-architecture footnotes that blocked fair comparison.

2. **Repair cascade already trusted for anchoring.** `locate_evidence()` and offset placement use the same cascade. Scoring validity with a stricter test than anchoring was internally inconsistent.

3. **Repaired spans are source-exact by construction.** Each repair function returns only when the result is found verbatim in `note_text`. Phase 0 taxonomy audit + unit fixtures lock the boundary between recoverable quirk and genuine absence.

4. **Gates are separate.** Widening functional evidence gates (e.g. `fresh_evidence_reasoner.py:1634`) to accept `REPAIRED_*` spans can move predictions and requires frozen-holdout protocol — not part of metric unification.

---

## Related documents

- Unification plan: [evidence_validity_unification_plan_2026-06-27.md](../plans/evidence_validity_unification_plan_2026-06-27.md)
- Phase 0 before picture: [evidence_validity_audit_2026-06-27.md](../experiments/reliability/evidence_validity_audit_2026-06-27.md)
- Phase 3 replay table: [evidence_groundedness_reconciliation_2026-06-27.md](../experiments/reliability/evidence_groundedness_reconciliation_2026-06-27.md)
- ExECTv2 evaluation protocol: [06_evaluation_and_benchmark_protocol.md](../plans/exectv2/06_evaluation_and_benchmark_protocol.md)
- gan2026 reliability scorecard: [gan2026_reliability_scorecard_and_phased_plan_2026-06-17.md](../experiments/gan2026/reliability/gan2026_reliability_scorecard_and_phased_plan_2026-06-17.md)
