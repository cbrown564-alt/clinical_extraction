"""Aggregate-only Investigations rule/adjudicator ablation for ExECTv2.

This report compares saved full-200 Investigations surfaces without emitting
row-level examples or failure ledgers. The row artifacts are read internally to
score aggregate variants and to estimate selective-adjudicator call burden.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.frontend_review import (
    REPO_ROOT,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_investigations_arbitration as arbitration,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_investigations_verifier as verifier,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)

DEFAULT_GENERATED_ON = "2026-06-25"
DEFAULT_DIRECT_JSONL = Path(
    "experiments/"
    "exectv2_v08_full200_currentcode_investigations_structured_direct_no_verifier_"
    "gpt41mini_20260624.jsonl"
)
DEFAULT_VERIFIER_JSONL = Path(
    "experiments/exectv2_v08_full200_currentcode_investigations_verifier_gpt41mini_"
    "20260624.jsonl"
)
DEFAULT_ARBITRATION_JSONL = Path(
    "experiments/exectv2_v08_full200_currentcode_investigations_arbitration_20260624.jsonl"
)
DEFAULT_SELECTIVE_JSONL = Path(
    "experiments/exectv2_v08_full200_currentcode_investigations_selective_adjudicator_"
    "v02_empty_pending_no_diagnostic_20260625.jsonl"
)
DEFAULT_DEV_DIRECT_JSONL = Path(
    "experiments/exectv2_llm_only_per_entity_dev140_gpt41mini_20260617_investigations.jsonl"
)
DEFAULT_DEV_ARBITRATION_JSONL = Path(
    "experiments/exectv2_llm_investigations_arbitration_v02_dev140_20260621.jsonl"
)
DEFAULT_JSON = Path("experiments/exectv2_investigations_rule_ablation_20260625.json")
DEFAULT_MARKDOWN = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_investigations_rule_ablation_2026-06-25.md"
)
SELECTIVE_POLICY_V01 = "v01_broad_ambiguous"
SELECTIVE_POLICY_V02 = "v02_empty_pending_or_explicit_not_performed"
MAX_ACCEPTABLE_SELECTIVE_BURDEN = 0.20
SELECTIVE_POLICY_V03 = "v03_empty_output_only"
SELECTIVE_POLICY_V04 = "v04_capped_direct_risk_top20"
SELECTIVE_REVIEW_BURDEN_CEILING = MAX_ACCEPTABLE_SELECTIVE_BURDEN

_PENDING_OR_PLANNED_RE = re.compile(
    r"\b(?:will|arrang(?:e|ed|ing)|request(?:ed|ing)?|await(?:ing)?|"
    r"appointment|suggest|recommend|should update|today agreed to chase|"
    r"up to date|not yet (?:performed|received)|planned|pending)\b",
    re.IGNORECASE,
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    resolved = path if path.is_absolute() else REPO_ROOT / path
    return [
        json.loads(line)
        for line in resolved.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def build_investigations_rule_ablation_payload(
    direct_rows: Sequence[Mapping[str, Any]],
    verifier_rows: Sequence[Mapping[str, Any]],
    *,
    arbitration_rows: Sequence[Mapping[str, Any]] | None = None,
    development_direct_rows: Sequence[Mapping[str, Any]] | None = None,
    development_arbitration_rows: Sequence[Mapping[str, Any]] | None = None,
    generated_on: str = DEFAULT_GENERATED_ON,
) -> dict[str, Any]:
    """Build the aggregate payload from direct, verifier, and arbitrated rows."""

    direct_pending_rows, direct_pending_metadata = arbitration.arbitrate_rows(direct_rows)
    arbitrated_rows = (
        [dict(row) for row in arbitration_rows]
        if arbitration_rows is not None
        else arbitration.arbitrate_rows(verifier_rows)[0]
    )
    selective_v01_rows, routed_v01_letters = selective_verifier_rows(
        direct_rows,
        arbitrated_rows,
        policy=SELECTIVE_POLICY_V01,
    )
    selective_v02_rows, routed_v02_letters = selective_verifier_rows(
        direct_rows,
        arbitrated_rows,
        policy=SELECTIVE_POLICY_V02,
    )
    selective_v03_rows, routed_v03_letters = selective_verifier_rows(
        direct_rows,
        arbitrated_rows,
        policy=SELECTIVE_POLICY_V03,
    )
    selective_v04_rows, routed_v04_letters = selective_verifier_rows(
        direct_rows,
        arbitrated_rows,
        policy=SELECTIVE_POLICY_V04,
    )
    development_policy_selection = _development_policy_selection(
        development_direct_rows,
        development_arbitration_rows,
    )
    selective_gate = _selective_review_burden_gate(development_policy_selection)

    variants = [
        _variant(
            "structured_direct_result_lens",
            "Structured direct + result lens",
            direct_rows,
            rule_family="result_lens",
            calls_per_letter=0.0,
            comparator_rows=direct_rows,
        ),
        _variant(
            "structured_direct_pending_suppression",
            "Structured direct + pending-test suppression",
            direct_pending_rows,
            rule_family="pending_test_suppression",
            calls_per_letter=0.0,
            comparator_rows=direct_rows,
            action_counts=direct_pending_metadata["arbitration_action_counts"],
        ),
        _variant(
            "verifier_only",
            "Verifier only",
            verifier_rows,
            rule_family="llm_verifier",
            calls_per_letter=1.0,
            comparator_rows=direct_rows,
        ),
        _variant(
            "verifier_plus_pending_suppression",
            "Verifier + deterministic pending-test suppression",
            arbitrated_rows,
            rule_family="llm_verifier_plus_pending_test_suppression",
            calls_per_letter=1.0,
            comparator_rows=verifier_rows,
            action_counts=_action_counts(arbitrated_rows),
        ),
        _variant(
            "selective_verifier_v01_broad_pending_suppression",
            "Selective verifier v01 broad ambiguity + pending-test suppression",
            selective_v01_rows,
            rule_family="selective_llm_verifier_plus_pending_test_suppression",
            calls_per_letter=routed_v01_letters / len(direct_rows) if direct_rows else 0.0,
            comparator_rows=direct_rows,
            action_counts=_action_counts(selective_v01_rows),
            routed_letters=routed_v01_letters,
        ),
        _variant(
            "selective_verifier_v02_empty_pending_no",
            "Selective verifier v02 empty/pending/not-performed + pending-test suppression",
            selective_v02_rows,
            rule_family="selective_llm_verifier_v02_plus_pending_test_suppression",
            calls_per_letter=routed_v02_letters / len(direct_rows) if direct_rows else 0.0,
            comparator_rows=direct_rows,
            action_counts=_action_counts(selective_v02_rows),
            routed_letters=routed_v02_letters,
        ),
        _variant(
            "selective_verifier_v03_empty_output_only",
            "Selective verifier v03 empty-output-only + pending-test suppression",
            selective_v03_rows,
            rule_family="selective_llm_verifier_v03_empty_output_only",
            calls_per_letter=routed_v03_letters / len(direct_rows) if direct_rows else 0.0,
            comparator_rows=direct_rows,
            action_counts=_action_counts(selective_v03_rows),
            routed_letters=routed_v03_letters,
        ),
        _variant(
            "selective_verifier_v04_capped_direct_risk_top20",
            "Selective verifier v04 capped direct-risk top 20% + pending-test suppression",
            selective_v04_rows,
            rule_family="selective_llm_verifier_v04_capped_direct_risk_top20",
            calls_per_letter=routed_v04_letters / len(direct_rows) if direct_rows else 0.0,
            comparator_rows=direct_rows,
            action_counts=_action_counts(selective_v04_rows),
            routed_letters=routed_v04_letters,
        ),
    ]
    return {
        "artifact_kind": "exectv2_investigations_rule_ablation",
        "generated_on": generated_on,
        "row_inspection_policy": "aggregate_only_no_full200_failure_ledgers",
        "allow_model_calls": False,
        "surface": "current-code v08-shape full-200 Investigations",
        "claim_boundary": (
            "Aggregate-only component ablation over saved current-code full-200 "
            "Investigations artifacts. Reports rule-family deltas, call burden, "
            "and action counts without full-200 row identifiers, note text, "
            "evidence snippets, rationales, or failure examples."
        ),
        "controls": {
            "structured_direct_investigations_f1": _metrics(direct_rows)["f1"],
            "verifier_plus_arbitration_investigations_f1": _metrics(arbitrated_rows)["f1"],
        },
        "max_acceptable_selective_burden": MAX_ACCEPTABLE_SELECTIVE_BURDEN,
        "development_policy_selection": development_policy_selection,
        "selective_review_burden_gate": selective_gate,
        "variants": variants,
        "decision": _decision(variants, selective_gate),
    }


def selective_verifier_rows(
    direct_rows: Sequence[Mapping[str, Any]],
    arbitrated_verifier_rows: Sequence[Mapping[str, Any]],
    *,
    policy: str = SELECTIVE_POLICY_V02,
) -> tuple[list[dict[str, Any]], int]:
    """Use the arbitrated verifier only when direct rows are heuristically ambiguous."""

    verifier_by_id = {str(row["letter_id"]): dict(row) for row in arbitrated_verifier_rows}
    capped_route_ids = (
        _capped_direct_risk_route_ids(direct_rows)
        if policy == SELECTIVE_POLICY_V04
        else set()
    )
    selected: list[dict[str, Any]] = []
    routed = 0
    for row in direct_rows:
        needs_adjudicator = (
            str(row["letter_id"]) in capped_route_ids
            if policy == SELECTIVE_POLICY_V04
            else _needs_investigations_adjudicator(row, policy=policy)
        )
        if needs_adjudicator:
            routed += 1
            selected.append(dict(verifier_by_id[str(row["letter_id"])]))
        else:
            selected.append(dict(row))
    return selected, routed


def write_investigations_rule_ablation_artifacts(
    *,
    direct_jsonl: Path = DEFAULT_DIRECT_JSONL,
    verifier_jsonl: Path = DEFAULT_VERIFIER_JSONL,
    arbitration_jsonl: Path = DEFAULT_ARBITRATION_JSONL,
    selective_jsonl: Path = DEFAULT_SELECTIVE_JSONL,
    json_path: Path = DEFAULT_JSON,
    markdown_path: Path = DEFAULT_MARKDOWN,
    generated_on: str = DEFAULT_GENERATED_ON,
) -> dict[str, Path]:
    """Write JSON, Markdown, and selective diagnostic JSONL artifacts."""

    direct_rows = read_jsonl(direct_jsonl)
    verifier_rows = read_jsonl(verifier_jsonl)
    arbitrated_rows = read_jsonl(arbitration_jsonl)
    development_direct_rows = read_jsonl(DEFAULT_DEV_DIRECT_JSONL)
    development_arbitration_rows = read_jsonl(DEFAULT_DEV_ARBITRATION_JSONL)
    payload = build_investigations_rule_ablation_payload(
        direct_rows,
        verifier_rows,
        arbitration_rows=arbitrated_rows,
        development_direct_rows=development_direct_rows,
        development_arbitration_rows=development_arbitration_rows,
        generated_on=generated_on,
    )
    selective_rows, _ = selective_verifier_rows(
        direct_rows,
        arbitrated_rows,
        policy=SELECTIVE_POLICY_V02,
    )

    selective_jsonl.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(selective_rows, selective_jsonl)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(
        render_investigations_rule_ablation_markdown(
            payload,
            json_path=json_path,
            selective_jsonl=selective_jsonl,
        ),
        encoding="utf-8",
    )
    return {"json": json_path, "markdown": markdown_path, "selective_jsonl": selective_jsonl}


def render_investigations_rule_ablation_markdown(
    payload: Mapping[str, Any],
    *,
    json_path: Path,
    selective_jsonl: Path,
) -> str:
    lines = [
        "# ExECTv2 Investigations Rule Ablation",
        "",
        f"- Generated: `{payload['generated_on']}`",
        f"- JSON: `{json_path.as_posix()}`",
        f"- Selective diagnostic JSONL: `{selective_jsonl.as_posix()}`",
        f"- Row inspection policy: `{payload['row_inspection_policy']}`",
        f"- Model calls during this build: `{payload['allow_model_calls']}`",
        f"- Surface: {payload['surface']}",
        (
            "- Maximum acceptable selective review burden: "
            f"`{payload['max_acceptable_selective_burden']:.2f}`"
        ),
        f"- Claim boundary: {payload['claim_boundary']}",
        "",
        "## Aggregate Table",
        "",
        (
            "| Variant | Rule family | Calls / letter | Selective burden | "
            "Changed rows | Actions | F1 | P | R | TP | FP | FN | Evidence valid |"
        ),
        (
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | "
            "---: | ---: | ---: | ---: |"
        ),
    ]
    for row in payload["variants"]:
        metrics = row["metrics"]
        lines.append(
            f"| {row['label']} | `{row['rule_family']}` | "
            f"{row['calls_per_letter']:.4f} | {row['selective_call_burden']:.4f} | "
            f"{row['changed_rows']} | {sum(row['action_counts'].values())} | "
            f"{metrics['f1']:.4f} | {metrics['precision']:.4f} | "
            f"{metrics['recall']:.4f} | {metrics['tp']} | {metrics['fp']} | "
            f"{metrics['fn']} | {row['evidence_validity_rate']:.4f} |"
        )
    decision = payload["decision"]
    development = payload.get("development_policy_selection") or []
    if development:
        lines.extend(
            [
                "",
                "## Dev140 Policy Selection",
                "",
                "| Policy | Routed burden | Burden gate | F1 | P | R | TP | FP | FN |",
                "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in development:
            metrics = row["metrics"]
            gate_outcome = (
                "pass"
                if row["selective_call_burden"] <= SELECTIVE_REVIEW_BURDEN_CEILING
                else "fail"
            )
            lines.append(
                f"| {row['label']} | {row['selective_call_burden']:.4f} | "
                f"{gate_outcome} | "
                f"{metrics['f1']:.4f} | {metrics['precision']:.4f} | "
                f"{metrics['recall']:.4f} | {metrics['tp']} | {metrics['fp']} | "
                f"{metrics['fn']} |"
            )
    gate = payload.get("selective_review_burden_gate", {})
    if gate:
        lines.extend(
            [
                "",
                "## Selective Review Burden Gate",
                "",
                f"- Ceiling: `{gate['ceiling']:.4f}` routed letters per letter",
                f"- Gate status: `{gate['status']}`",
                f"- Selected low-burden dev policy: `{gate['selected_policy_id']}`",
                f"- Blocked over-ceiling dev policies: `{', '.join(gate['blocked_policy_ids'])}`",
                (
                    "- Live-call boundary: this is a no-call dev140 scaffold; a live "
                    "selective-adjudicator experiment still needs a fresh "
                    "predeclaration freezing the selected policy, scorer, surface, "
                    "and stop rule."
                ),
            ]
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Selected next architecture: `{decision['selected_next_architecture']}`",
            (
                "- Deterministic replacement promoted: "
                f"`{decision['deterministic_replacement_promoted']}`"
            ),
            (
                "- Selective burden acceptable: "
                f"`{decision['selective_v02_burden_acceptable']}`"
            ),
            f"- Rationale: {decision['rationale']}",
            "",
            "## Interpretation",
            "",
            (
                "The deterministic pending-test suppression layer is useful as a "
                "precision cleanup over the verifier, but the saved direct structured "
                "surface does not close the gap to the verifier-backed lane. "
                "The v02 selective policy was chosen on dev140 because it removes "
                "the broad unknown-result and multi-modality triggers while keeping "
                "empty-output, planned-test, and explicit-not-performed cases routed. "
                "On the aggregate-only full-200 replay it reduces verifier burden "
                "versus v01 without improving F1, but `0.5100` is far above the "
                "maximum acceptable review burden of `0.2000`, so it remains "
                "diagnostic. The v01-v03 selective policies remain over the "
                "selective-review burden ceiling, so continued cost work should "
                "use the v04 capped direct-risk scaffold, or another dev-only "
                "policy that is <=0.20 by construction, before any live "
                "selective-adjudicator experiment is predeclared."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _variant(
    variant_id: str,
    label: str,
    rows: Sequence[Mapping[str, Any]],
    *,
    rule_family: str,
    calls_per_letter: float,
    comparator_rows: Sequence[Mapping[str, Any]],
    action_counts: Mapping[str, int] | None = None,
    routed_letters: int = 0,
) -> dict[str, Any]:
    summary = verifier.summarize_rows([dict(row) for row in rows])
    n_rows = len(rows)
    return {
        "variant_id": variant_id,
        "label": label,
        "rule_family": rule_family,
        "calls_per_letter": round(calls_per_letter, 4),
        "selective_call_burden": round(routed_letters / n_rows, 4) if n_rows else 0.0,
        "routed_letters": routed_letters,
        "changed_rows": changed_rows(rows, comparator_rows),
        "action_counts": dict(sorted((action_counts or {}).items())),
        "metrics": _metrics_from_summary(summary),
        "evidence_validity_rate": float(summary.get("evidence_validity_rate", 1.0)),
        "call_failures": int(summary.get("call_failures", 0)),
        "parse_schema_failures": int(summary.get("parse_failures", 0)),
    }


def _metrics(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return _metrics_from_summary(verifier.summarize_rows([dict(row) for row in rows]))


def _metrics_from_summary(summary: Mapping[str, Any]) -> dict[str, Any]:
    clinical = summary["clinical_recovery"]["investigations"]
    return {
        "f1": float(clinical["f1"]),
        "precision": float(clinical["precision"]),
        "recall": float(clinical["recall"]),
        "tp": int(clinical["tp"]),
        "fp": int(clinical["fp"]),
        "fn": int(clinical["fn"]),
    }


def _decision(
    variants: Sequence[Mapping[str, Any]],
    selective_gate: Mapping[str, Any],
) -> dict[str, Any]:
    by_id = {str(row["variant_id"]): row for row in variants}
    direct_f1 = by_id["structured_direct_result_lens"]["metrics"]["f1"]
    direct_suppression_f1 = by_id["structured_direct_pending_suppression"]["metrics"]["f1"]
    verifier_arbitrated_f1 = by_id["verifier_plus_pending_suppression"]["metrics"]["f1"]
    selective_v01_f1 = by_id["selective_verifier_v01_broad_pending_suppression"]["metrics"]["f1"]
    selective_v02 = by_id["selective_verifier_v02_empty_pending_no"]
    selective_v02_f1 = selective_v02["metrics"]["f1"]
    selective_v02_burden = float(selective_v02["selective_call_burden"])
    selective_v03_f1 = by_id["selective_verifier_v03_empty_output_only"]["metrics"]["f1"]
    selective_v04_f1 = by_id["selective_verifier_v04_capped_direct_risk_top20"]["metrics"]["f1"]
    deterministic_promoted = direct_suppression_f1 >= verifier_arbitrated_f1 - 0.01
    selective_v02_burden_acceptable = (
        selective_v02_burden <= MAX_ACCEPTABLE_SELECTIVE_BURDEN
    )
    selected_low_burden_policy = str(selective_gate.get("selected_policy_id") or "")
    selected = (
        "deterministic_investigations_replacement"
        if deterministic_promoted
        else (
            "selective_investigations_adjudicator_low_burden_dev_scaffold"
            if selected_low_burden_policy
            else "blocked_until_selective_review_burden_redesign"
        )
    )
    return {
        "selected_next_architecture": selected,
        "deterministic_replacement_promoted": deterministic_promoted,
        "selected_low_burden_policy": selected_low_burden_policy,
        "selective_review_burden_ceiling": SELECTIVE_REVIEW_BURDEN_CEILING,
        "direct_to_verifier_arbitrated_gap": round(verifier_arbitrated_f1 - direct_f1, 4),
        "max_acceptable_selective_burden": MAX_ACCEPTABLE_SELECTIVE_BURDEN,
        "selective_v02_burden": selective_v02_burden,
        "selective_v02_burden_acceptable": selective_v02_burden_acceptable,
        "direct_suppression_to_verifier_arbitrated_gap": round(
            verifier_arbitrated_f1 - direct_suppression_f1,
            4,
        ),
        "selective_v01_to_verifier_arbitrated_gap": round(
            verifier_arbitrated_f1 - selective_v01_f1,
            4,
        ),
        "selective_v02_to_verifier_arbitrated_gap": round(
            verifier_arbitrated_f1 - selective_v02_f1,
            4,
        ),
        "selective_v03_to_verifier_arbitrated_gap": round(
            verifier_arbitrated_f1 - selective_v03_f1,
            4,
        ),
        "selective_v04_to_verifier_arbitrated_gap": round(
            verifier_arbitrated_f1 - selective_v04_f1,
            4,
        ),
        "rationale": (
            "Deterministic replacement is promoted only if direct structured plus "
            "deterministic suppression is within 0.0100 F1 of the verifier plus "
            "suppression control. Otherwise any selective Investigations policy "
            f"must first satisfy the <= {SELECTIVE_REVIEW_BURDEN_CEILING:.2f} "
            "dev140 routed-letter burden ceiling before a live selective-adjudicator "
            "experiment is predeclared."
        ),
    }


def changed_rows(
    rows: Sequence[Mapping[str, Any]],
    comparator_rows: Sequence[Mapping[str, Any]],
) -> int:
    comparator = {str(row["letter_id"]): _signature(row) for row in comparator_rows}
    return sum(
        _signature(row) != comparator.get(str(row["letter_id"]))
        for row in rows
    )


def _signature(row: Mapping[str, Any]) -> tuple[tuple[Any, ...], ...]:
    mentions = []
    for mention in row.get("predicted_mentions", []):
        attrs = tuple(
            sorted(
                (str(k), str(v))
                for k, v in dict(mention.get("attributes") or {}).items()
            )
        )
        mentions.append((str(mention.get("entity", "")), str(mention.get("text", "")), attrs))
    return tuple(sorted(mentions))


def _development_policy_selection(
    development_direct_rows: Sequence[Mapping[str, Any]] | None,
    development_arbitration_rows: Sequence[Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    if development_direct_rows is None or development_arbitration_rows is None:
        return []
    rows: list[dict[str, Any]] = []
    for policy, label in (
        (SELECTIVE_POLICY_V01, "v01 broad ambiguity"),
        (SELECTIVE_POLICY_V02, "v02 empty/pending/not-performed"),
        (SELECTIVE_POLICY_V03, "v03 empty-output-only"),
        (SELECTIVE_POLICY_V04, "v04 capped direct-risk top 20%"),
    ):
        selective_rows, routed_letters = selective_verifier_rows(
            development_direct_rows,
            development_arbitration_rows,
            policy=policy,
        )
        rows.append(
            _variant(
                policy,
                label,
                selective_rows,
                rule_family=policy,
                calls_per_letter=(
                    routed_letters / len(development_direct_rows)
                    if development_direct_rows
                    else 0.0
                ),
                comparator_rows=development_direct_rows,
                routed_letters=routed_letters,
            )
        )
    return rows


def _selective_review_burden_gate(
    development_policy_selection: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if not development_policy_selection:
        return {
            "ceiling": SELECTIVE_REVIEW_BURDEN_CEILING,
            "surface": "dev140_no_call_saved_artifacts",
            "status": "not_evaluable_without_dev140_policy_rows",
            "selected_policy_id": "",
            "eligible_policy_ids": [],
            "blocked_policy_ids": [],
        }
    eligible = [
        row
        for row in development_policy_selection
        if float(row["selective_call_burden"]) <= SELECTIVE_REVIEW_BURDEN_CEILING
    ]
    blocked = [
        str(row["variant_id"])
        for row in development_policy_selection
        if float(row["selective_call_burden"]) > SELECTIVE_REVIEW_BURDEN_CEILING
    ]
    selected = max(
        eligible,
        key=lambda row: (
            float(row["metrics"]["f1"]),
            -float(row["selective_call_burden"]),
            str(row["variant_id"]),
        ),
        default=None,
    )
    return {
        "ceiling": SELECTIVE_REVIEW_BURDEN_CEILING,
        "surface": "dev140_no_call_saved_artifacts",
        "status": "passes_design_ceiling" if selected else "blocked_until_redesign",
        "selected_policy_id": str(selected["variant_id"]) if selected else "",
        "eligible_policy_ids": [str(row["variant_id"]) for row in eligible],
        "blocked_policy_ids": blocked,
    }


def _needs_investigations_adjudicator(
    row: Mapping[str, Any],
    *,
    policy: str = SELECTIVE_POLICY_V02,
) -> bool:
    mentions = list(row.get("predicted_mentions", []))
    if not mentions:
        return True
    if policy == SELECTIVE_POLICY_V03:
        return False
    if policy == SELECTIVE_POLICY_V04:
        raise ValueError("v04 routing must be evaluated with cohort-level risk capping")
    route_pending_or_not_performed = False
    route_broad_ambiguity = False
    modalities = set()
    for mention in mentions:
        attrs = dict(mention.get("attributes") or {})
        evidence = str(mention.get("evidence", ""))
        rationale = str(mention.get("rationale", ""))
        context = f"{evidence} {rationale}"
        if _PENDING_OR_PLANNED_RE.search(context):
            route_pending_or_not_performed = True
        for modality in ("MRI", "CT", "EEG"):
            if f"{modality}_Performed" in attrs or f"{modality}_Results" in attrs:
                modalities.add(modality)
            if attrs.get(f"{modality}_Performed") == "No":
                route_pending_or_not_performed = True
            if attrs.get(f"{modality}_Results") == "Unknown":
                route_broad_ambiguity = True
        if not attrs:
            route_broad_ambiguity = True
    if policy == SELECTIVE_POLICY_V02:
        return route_pending_or_not_performed
    if policy == SELECTIVE_POLICY_V01:
        return route_pending_or_not_performed or route_broad_ambiguity or (
            len(mentions) > 1 and len(modalities) > 1
        )
    raise ValueError(f"Unknown Investigations selective policy: {policy}")


def _capped_direct_risk_route_ids(
    rows: Sequence[Mapping[str, Any]],
) -> set[str]:
    max_routed = int(len(rows) * SELECTIVE_REVIEW_BURDEN_CEILING)
    if max_routed <= 0:
        return set()
    scored = [
        (score, str(row["letter_id"]))
        for row in rows
        if (score := _direct_investigations_risk_score(row)) > 0
    ]
    scored.sort(key=lambda item: (-item[0], item[1]))
    return {letter_id for _, letter_id in scored[:max_routed]}


def _direct_investigations_risk_score(row: Mapping[str, Any]) -> int:
    mentions = list(row.get("predicted_mentions", []))
    if not mentions:
        return 100
    score = 0
    modalities = set()
    for mention in mentions:
        attrs = dict(mention.get("attributes") or {})
        evidence = str(mention.get("evidence", ""))
        rationale = str(mention.get("rationale", ""))
        context = f"{evidence} {rationale}"
        if not attrs:
            score += 20
        if _PENDING_OR_PLANNED_RE.search(context):
            score += 40
        for modality in ("MRI", "CT", "EEG"):
            if f"{modality}_Performed" in attrs or f"{modality}_Results" in attrs:
                modalities.add(modality)
            if attrs.get(f"{modality}_Performed") == "No":
                score += 35
            if attrs.get(f"{modality}_Results") == "Unknown":
                score += 15
    if len(mentions) > 1 and len(modalities) > 1:
        score += 10
    return score


def _action_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        for action in row.get("arbitration_actions", []):
            counts[str(action.get("rule_id", "unknown"))] += 1
    return dict(sorted(counts.items()))
