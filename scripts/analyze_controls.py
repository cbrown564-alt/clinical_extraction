"""Analyze RQ1/RQ2 component-control matrix results."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any


MATRIX_JSONL_PATH = Path("experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.jsonl")
REPORT_PATH = Path("experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.md")

ISOLATED_CONDITIONS = (
    "candidate_only",
    "gold_query_evidence_only",
    "candidate_conditioned_evidence_only",
    "projection_only",
)
PAIRED_CONDITIONS = (
    "candidate_plus_evidence",
    "evidence_plus_projection",
    "candidate_plus_evidence_plus_projection",
)


def main() -> None:
    rows = load_rows(MATRIX_JSONL_PATH)
    report = build_report(rows)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Wrote {REPORT_PATH}")


def load_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def build_report(rows: Sequence[Mapping[str, Any]]) -> str:
    by_panel = group_by(rows, "row_panel_id")
    balanced = by_panel.get("balanced_validation50", [])
    hard = by_panel.get("hidden_family_hard_panel", [])

    lines = [
        "# Gan 2026 RQ1/RQ2 Component-Control Matrix Analysis",
        "",
        "Full validation-development analysis of the RQ1/RQ2 component-control matrix.",
        "Only the `balanced_validation50` isolated controls contain fresh parsed outputs;",
        "the hidden-family hard panel and paired-task overload rows remain planned or empty",
        "surfaces and are not interpretable as model failures.",
        "",
        f"- Date: `2026-06-04`",
        f"- JSONL artifact: `{MATRIX_JSONL_PATH}`",
        f"- Total matrix rows: {len(rows)}",
        f"- Source rows represented: {len({row['source_row_index'] for row in rows})}",
        f"- Completed output surface: `balanced_validation50` isolated controls",
        f"- Claim boundary: validation-development component analysis only; no locked-test or benchmark-comparable claim.",
        "",
        "## Executive Findings",
        "",
        "1. Isolated RQ1/RQ2 prompts have strong schema adherence on `balanced_validation50`: "
        "`candidate_only`, `gold_query_evidence_only`, `candidate_conditioned_evidence_only`, "
        "and `projection_only` each parsed 50/50 rows.",
        "2. Candidate generation and evidence selection are credible component capabilities: "
        "candidate-only exact evidence is 47/50, gold-query evidence exactness is 47/50, "
        "and candidate-conditioned evidence exactness is 47/50.",
        "3. Projection is the weak link. It parsed 50/50 and often selected the right broad "
        "decision kind, but only 4/50 outputs are already in exact Gan canonical label form. "
        "Most frequency and seizure-free rows need deterministic rendering or policy handling.",
        "4. Unknown and unresolved-multiple rows are not solved by the current projection-only "
        "surface: unknown rows are usually collapsed to `no_reference` or `seizure_free`, and "
        "unresolved-multiple rows are usually abstained, collapsed, or over-projected.",
        "5. The paired-task overload rows have no parsed outputs, so overload loss is still "
        "unanswered. The hard panel also has no outputs, so hidden-family transfer remains "
        "unanswered beyond panel membership.",
        "",
        "## Artifact Coverage",
        "",
        "| Panel | Matrix rows | Source rows | Completed rows | Status |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for panel_id, panel_rows in sorted(by_panel.items()):
        completed = sum(has_output(row) for row in panel_rows)
        status = "completed isolated controls" if completed else "planned surface only"
        lines.append(
            f"| `{panel_id}` | {len(panel_rows)} | "
            f"{len({row['source_row_index'] for row in panel_rows})} | {completed} | {status} |"
        )

    lines.extend(
        [
            "",
            "## Condition Status",
            "",
            "| Condition | Task | Panel | Rows | Parsed | Exact evidence | Output status |",
            "| --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for panel_id in ("balanced_validation50", "hidden_family_hard_panel"):
        for condition_id, condition_rows in sorted(group_by(by_panel.get(panel_id, []), "condition_id").items()):
            parsed = sum(parsed_successfully(row) for row in condition_rows)
            exact = sum(row.get("exact_evidence_status") == "exact" for row in condition_rows)
            status = condition_status(condition_rows)
            lines.append(
                f"| `{condition_id}` | `{condition_rows[0]['component_task']}` | `{panel_id}` | "
                f"{len(condition_rows)} | {parsed}/{len(condition_rows)} | {exact}/{len(condition_rows)} | {status} |"
            )

    lines.extend(candidate_section(balanced))
    lines.extend(evidence_section(balanced, "gold_query_evidence_only", "Gold-Query Evidence Only"))
    lines.extend(
        evidence_section(
            balanced,
            "candidate_conditioned_evidence_only",
            "Candidate-Conditioned Evidence Only",
        )
    )
    lines.extend(projection_section(balanced))
    lines.extend(hidden_family_section(balanced))
    lines.extend(gap_section(rows))
    return "\n".join(lines) + "\n"


def candidate_section(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    condition_rows = rows_for(rows, "candidate_only")
    counts = [len(candidates(row)) for row in condition_rows]
    kinds = Counter(candidate.get("candidate_kind") for row in condition_rows for candidate in candidates(row))
    temporality = Counter(candidate.get("temporality") for row in condition_rows for candidate in candidates(row))
    confidence = Counter(candidate.get("confidence") for row in condition_rows for candidate in candidates(row))
    zero_rows = [row for row in condition_rows if not candidates(row)]
    non_exact = [row for row in condition_rows if row.get("exact_evidence_status") != "exact"]

    lines = [
        "",
        "## RQ1 Candidate-Only Readout",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Parsed rows | {sum(parsed_successfully(row) for row in condition_rows)}/{len(condition_rows)} |",
        f"| Exact-evidence rows | {sum(row.get('exact_evidence_status') == 'exact' for row in condition_rows)}/{len(condition_rows)} |",
        f"| Candidate facts emitted | {sum(counts)} |",
        f"| Mean candidates per row | {mean(counts):.2f} |",
        f"| Median candidates per row | {median(counts):.0f} |",
        f"| P90 candidates per row | {percentile(counts, 90):.0f} |",
        f"| Rows with no candidates | {len(zero_rows)} |",
        "",
        "| Candidate kind | Count |",
        "| --- | ---: |",
    ]
    for key, value in kinds.most_common():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "| Temporality | Count |",
            "| --- | ---: |",
        ]
    )
    for key, value in temporality.most_common():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "| Confidence | Count |",
            "| --- | ---: |",
        ]
    )
    for key, value in confidence.most_common():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "Interpretation: candidate-only is useful as an RQ1 recall surface, not as a final "
            "answer selector. It emits a small candidate burden, mostly one or two facts per "
            "note, and preserves ambiguity on many rows. The eight zero-candidate rows are "
            "expected to include `unknown` or `no_reference` cases rather than automatic failures.",
            "",
            "Non-exact or unchecked candidate rows:",
            "",
            "| Row | Gold | Status | Mechanism note |",
            "| ---: | --- | --- | --- |",
        ]
    )
    for row in non_exact:
        lines.append(
            f"| {row['source_row_index']} | `{md(row['gold_label'])}` | "
            f"`{row.get('exact_evidence_status')}` | {candidate_note(row)} |"
        )
    return lines


def evidence_section(rows: Sequence[Mapping[str, Any]], condition_id: str, title: str) -> list[str]:
    condition_rows = rows_for(rows, condition_id)
    span_counts = [len(evidence_spans(row)) for row in condition_rows]
    roles = Counter(span.get("role") for row in condition_rows for span in evidence_spans(row))
    support = Counter(span.get("support_status") for row in condition_rows for span in evidence_spans(row))
    missing_components = Counter(
        missing
        for row in condition_rows
        for span in evidence_spans(row)
        for missing in span.get("missing_components", [])
    )
    non_exact = [row for row in condition_rows if row.get("exact_evidence_status") != "exact"]
    insufficient = sum(bool(output(row).get("insufficient_evidence_reason")) for row in condition_rows)

    lines = [
        "",
        f"## RQ2 {title} Readout",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Parsed rows | {sum(parsed_successfully(row) for row in condition_rows)}/{len(condition_rows)} |",
        f"| Exact-evidence rows | {sum(row.get('exact_evidence_status') == 'exact' for row in condition_rows)}/{len(condition_rows)} |",
        f"| Evidence spans emitted | {sum(span_counts)} |",
        f"| Mean spans per row | {mean(span_counts):.2f} |",
        f"| Median spans per row | {median(span_counts):.0f} |",
        f"| P90 spans per row | {percentile(span_counts, 90):.0f} |",
        f"| Rows with insufficient-evidence reason | {insufficient} |",
        "",
        "| Evidence role | Count |",
        "| --- | ---: |",
    ]
    for key, value in roles.most_common():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "| Support status | Count |",
            "| --- | ---: |",
        ]
    )
    for key, value in support.most_common():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "| Most frequent missing component | Count |",
            "| --- | ---: |",
        ]
    )
    for key, value in missing_components.most_common(7):
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "Interpretation: this is a strong evidence-location surface but not a full "
            "clinical decision surface. Missing operands remain common by design because the "
            "prompt is allowed to say that selected evidence is decisive, contextual, or "
            "incomplete without rendering a Gan label.",
            "",
            "Non-exact evidence rows:",
            "",
            "| Row | Gold | Status | Mechanism note |",
            "| ---: | --- | --- | --- |",
        ]
    )
    for row in non_exact:
        lines.append(
            f"| {row['source_row_index']} | `{md(row['gold_label'])}` | "
            f"`{row.get('exact_evidence_status')}` | {evidence_note(row)} |"
        )
    return lines


def projection_section(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    condition_rows = rows_for(rows, "projection_only")
    exact = sum(exact_label_match(row) for row in condition_rows)
    kind = sum(projection_kind_match(row) for row in condition_rows)
    null_label = sum(output(row).get("seizure_frequency_label") in (None, "") for row in condition_rows)
    by_gold: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    transitions = Counter((row.get("gold_kind"), output(row).get("decision_kind")) for row in condition_rows)
    mismatches = [row for row in condition_rows if not projection_kind_match(row)]

    for row in condition_rows:
        bucket = by_gold[str(row.get("gold_kind"))]
        bucket[0] += 1
        bucket[1] += exact_label_match(row)
        bucket[2] += projection_kind_match(row)
        bucket[3] += output(row).get("seizure_frequency_label") in (None, "")

    lines = [
        "",
        "## Projection-Only Readout",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Parsed rows | {sum(parsed_successfully(row) for row in condition_rows)}/{len(condition_rows)} |",
        f"| Exact canonical label matches | {exact}/{len(condition_rows)} |",
        f"| Broad decision-kind matches | {kind}/{len(condition_rows)} |",
        f"| Null or abstained labels | {null_label}/{len(condition_rows)} |",
        "",
        "| Gold kind | Rows | Exact label | Broad kind match | Null label |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for gold_kind, values in sorted(by_gold.items()):
        total, exact_count, kind_count, null_count = values
        lines.append(f"| `{gold_kind}` | {total} | {exact_count} | {kind_count} | {null_count} |")
    lines.extend(
        [
            "",
            "| Gold kind -> decision kind | Rows |",
            "| --- | ---: |",
        ]
    )
    for (gold_kind, decision_kind), count in transitions.most_common():
        lines.append(f"| `{gold_kind}` -> `{decision_kind}` | {count} |")
    lines.extend(
        [
            "",
            "Interpretation: projection-only separates semantic selection from benchmark rendering. "
            "The model often recognizes ordinary frequency and seizure-free states, but it "
            "does not reliably emit canonical Gan labels and it mishandles `unknown` and "
            "`unresolved_multiple` policy states. This supports a deterministic compiler or "
            "policy layer after any LLM-selected state, plus an explicit ambiguity/review "
            "routing policy rather than direct model rendering.",
            "",
            "Projection-kind mismatches:",
            "",
            "| Row | Gold | Gold kind | Predicted label | Decision kind | Families |",
            "| ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for row in mismatches:
        families = ";".join(row.get("hidden_families") or [])
        lines.append(
            f"| {row['source_row_index']} | `{md(row['gold_label'])}` | `{row['gold_kind']}` | "
            f"`{md(output(row).get('seizure_frequency_label'))}` | "
            f"`{output(row).get('decision_kind')}` | `{families}` |"
        )
    return lines


def hidden_family_section(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    families = sorted({family for row in rows_for(rows, "candidate_only") for family in row.get("hidden_families", [])})
    lines = [
        "",
        "## Balanced Panel Hidden-Family Readout",
        "",
        "| Family | Rows | Candidate exact | Gold-query evidence exact | Candidate-conditioned evidence exact | Projection kind match |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for family in families:
        base = [row for row in rows_for(rows, "candidate_only") if family in row.get("hidden_families", [])]
        candidate_exact = exact_for_family(rows, "candidate_only", family)
        gold_exact = exact_for_family(rows, "gold_query_evidence_only", family)
        conditioned_exact = exact_for_family(rows, "candidate_conditioned_evidence_only", family)
        projection_rows = [row for row in rows_for(rows, "projection_only") if family in row.get("hidden_families", [])]
        projection_match = sum(projection_kind_match(row) for row in projection_rows)
        lines.append(
            f"| `{family}` | {len(base)} | {candidate_exact}/{len(base)} | "
            f"{gold_exact}/{len(base)} | {conditioned_exact}/{len(base)} | "
            f"{projection_match}/{len(base)} |"
        )
    lines.extend(
        [
            "",
            "Family interpretation: exact evidence stays high even in dense overlapping families, "
            "but projection degrades on benchmark conventions, unknown boundaries, unresolved "
            "multiple states, and ambiguity-heavy rows. That pattern points to representation "
            "and policy failures rather than a simple inability to locate text.",
        ]
    )
    return lines


def gap_section(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    paired = [row for row in rows if row.get("condition_id") in PAIRED_CONDITIONS]
    hard = [row for row in rows if row.get("row_panel_id") == "hidden_family_hard_panel"]
    source_blank = sum(not row.get("source_id_status") for row in rows if has_output(row))
    model_blank = sum(not row.get("model_id") for row in rows if has_output(row))
    completed = sum(has_output(row) for row in rows)
    lines = [
        "",
        "## Instrumentation Gaps And Next Analysis",
        "",
        f"- Paired-task overload rows with outputs: {sum(has_output(row) for row in paired)}/{len(paired)}.",
        f"- Hidden-family hard-panel rows with outputs: {sum(has_output(row) for row in hard)}/{len(hard)}.",
        f"- Completed rows missing `source_id_status`: {source_blank}/{completed}.",
        f"- Completed rows missing `model_id`: {model_blank}/{completed}.",
        "- `projection_only` exact-evidence status is `not_checked` by design because the input is fixed candidate/evidence state rather than newly selected spans.",
        "",
        "## Decision",
        "",
        "The matrix supports a development-control answer for isolated `balanced_validation50` only: "
        "candidate generation and evidence selection are worth carrying forward as component "
        "surfaces, but projection should not be trusted as direct final-label rendering. "
        "Before moving to paired prompts or the hard panel, fill model metadata and source-id "
        "validation, then run the paired-task overload rows with the same prompt versions.",
        "",
    ]
    return lines


def rows_for(rows: Sequence[Mapping[str, Any]], condition_id: str) -> list[Mapping[str, Any]]:
    return [row for row in rows if row.get("condition_id") == condition_id]


def group_by(rows: Iterable[Mapping[str, Any]], key: str) -> dict[str, list[Mapping[str, Any]]]:
    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(key) or "")].append(row)
    return groups


def output(row: Mapping[str, Any]) -> Mapping[str, Any]:
    value = row.get("component_output") or {}
    return value if isinstance(value, Mapping) else {}


def has_output(row: Mapping[str, Any]) -> bool:
    return bool(output(row))


def parsed_successfully(row: Mapping[str, Any]) -> bool:
    return bool((row.get("component_metrics") or {}).get("parsed_successfully"))


def candidates(row: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    value = output(row).get("candidates") or []
    return value if isinstance(value, list) else []


def evidence_spans(row: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    value = output(row).get("selected_evidence") or []
    return value if isinstance(value, list) else []


def condition_status(rows: Sequence[Mapping[str, Any]]) -> str:
    if not rows:
        return "missing"
    if any(has_output(row) for row in rows):
        return "fresh outputs present"
    if rows[0].get("condition_id") in PAIRED_CONDITIONS:
        return "not run: overload unanswered"
    return "not run"


def exact_label_match(row: Mapping[str, Any]) -> bool:
    predicted = str(output(row).get("seizure_frequency_label") or "").strip().lower()
    gold = str(row.get("gold_label") or "").strip().lower()
    return bool(predicted and predicted == gold)


def projection_kind_match(row: Mapping[str, Any]) -> bool:
    decision_kind = output(row).get("decision_kind")
    gold_kind = row.get("gold_kind")
    predicted = output(row).get("seizure_frequency_label")
    if gold_kind in {"frequency", "seizure_free", "unknown", "no_reference"}:
        return decision_kind == gold_kind
    if gold_kind == "unresolved_multiple":
        # The projection schema has no unresolved_multiple decision kind, so the
        # least-bad broad match is preserving a non-null frequency-like state
        # rather than collapsing the row to no_reference, unknown, or seizure_free.
        return decision_kind == "frequency" and bool(predicted)
    return False


def exact_for_family(rows: Sequence[Mapping[str, Any]], condition_id: str, family: str) -> int:
    return sum(
        row.get("exact_evidence_status") == "exact"
        for row in rows_for(rows, condition_id)
        if family in row.get("hidden_families", [])
    )


def candidate_note(row: Mapping[str, Any]) -> str:
    if row.get("exact_evidence_status") == "not_checked":
        return "raw output retained; exact-evidence checker did not validate the parsed packet"
    candidate = next(iter(candidates(row)), {})
    evidence = str(candidate.get("evidence") or "")
    if evidence:
        return md(evidence[:120])
    return "no candidate evidence available"


def evidence_note(row: Mapping[str, Any]) -> str:
    span = next(iter(evidence_spans(row)), {})
    evidence = str(span.get("evidence") or "")
    if output(row).get("insufficient_evidence_reason"):
        return md(str(output(row).get("insufficient_evidence_reason"))[:120])
    if evidence:
        return md(evidence[:120])
    return "no selected evidence available"


def mean(values: Sequence[int]) -> float:
    return sum(values) / len(values) if values else 0.0


def median(values: Sequence[int]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return float(ordered[len(ordered) // 2])


def percentile(values: Sequence[int], pct: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(len(ordered) * pct / 100) - 1))
    return float(ordered[index])


def md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    main()
