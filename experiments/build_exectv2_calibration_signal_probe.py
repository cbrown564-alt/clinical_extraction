"""Phase-0 data-validation probe for the calibration strengthening plan.

Replays saved dev140 artifacts to score the two candidate calibration signals
(cross-model agreement and self-consistency entropy) and runs the predeclared
falsification checks for hypotheses H1 and H2 from
`docs/plans/calibration_abstention_review_routing_strengthening_plan_2026-07-01.md`.

No model calls, no full-200/holdout rows. dev140 replay only.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability import (
    external_signals,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.cells import (
    iter_reliability_cells,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.constants import (
    FAMILIES,
    RICH_SCHEMA_RUNS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.io import (
    REPO_ROOT,
    load_jsonl,
)

OUT_JSON = REPO_ROOT / "experiments/exectv2_calibration_signal_probe_2026-07-07.json"
OUT_MD = (
    REPO_ROOT
    / "docs/experiments/exectv2/reliability/exectv2_calibration_signal_probe_2026-07-07.md"
)

# AUROC usefulness bar carried over from the wall-transfer probe / plan.
_AUROC_USEFULNESS_BAR = 0.70
# H2 redundancy threshold (plan §2): above this Spearman rho the two signals are
# treated as redundant and only the stronger is kept for the combined fit.
_H2_REDUNDANCY_RHO = 0.70


def main() -> None:
    rich_rows = {run.candidate: load_jsonl(REPO_ROOT / run.rows_path) for run in RICH_SCHEMA_RUNS}
    cells = list(iter_reliability_cells(rich_rows))

    agreement = external_signals.load_dev140_cross_model_agreement()
    entropy = external_signals.load_dev140_self_consistency_entropy()

    per_family = _per_family_signal_auroc(cells, agreement, entropy)
    pooled = _pooled_signal_auroc(cells, agreement, entropy)
    correlation = _spearman_correlation(cells, agreement, entropy)
    distributions = _signal_distributions(cells, agreement, entropy)

    # H1 falsification: cross-model agreement must beat 0.5 (uninformative) on at
    # least two of the three non-SF families to generalize beyond the SF-only result.
    non_sf_families = [f for f in FAMILIES if f != "SeizureFrequency"]
    h1_generalizing = [
        f
        for f in non_sf_families
        if per_family[f]["cross_model_agreement"]["auroc_error"] > _AUROC_USEFULNESS_BAR
    ]
    h1_verdict = (
        "supported"
        if len(h1_generalizing) >= 2
        or pooled["cross_model_agreement"]["auroc_error"] > _AUROC_USEFULNESS_BAR
        else "refuted_does_not_generalize"
    )

    # H2 falsification: high correlation with cross-model agreement means redundancy.
    h2_verdict = (
        "redundant_with_cross_model_agreement"
        if abs(correlation["spearman_rho"]) > _H2_REDUNDANCY_RHO
        else "adds_orthogonal_signal"
    )

    payload = {
        "probe_kind": "exectv2_calibration_signal_probe_dev140",
        "generated_on": "2026-07-07",
        "generated_by": "experiments/build_exectv2_calibration_signal_probe.py",
        "claim_boundary": (
            "dev140 replay over saved same-core model-swap and multi-temperature "
            "artifacts; no model calls, no full-200 or holdout rows."
        ),
        "cell_count": len(cells),
        "signal_sources": {
            "cross_model_agreement": {
                "artifacts": [
                    "experiments/exectv2_2call_no_sf_adjudicator_{gpt41mini,deepseek,qwen36}_dev140_20260625.jsonl",
                ],
                "definition": (
                    "Size of the largest identical-headline-keyset cluster across "
                    "the three same-core models (1..3); risk = (3 - agreement)/3."
                ),
            },
            "self_consistency_entropy": {
                "artifacts": [
                    "experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_"
                    "temps_r{1..4}_temp*_20260625_assembly.jsonl",
                ],
                "definition": (
                    "Normalized Shannon entropy of the headline-keyset "
                    "distribution across the four temperature runs, in [0, 1]."
                ),
            },
        },
        "per_family_auroc": per_family,
        "pooled_auroc": pooled,
        "h2_correlation": correlation,
        "signal_distributions": distributions,
        "predeclared_verdicts": {
            "H1_cross_model_agreement_generalizes": {
                "verdict": h1_verdict,
                "bar": (
                    f"AUROC > {_AUROC_USEFULNESS_BAR} on >=2 of the 3 non-SF "
                    "families, or on the pooled population."
                ),
                "non_sf_families_above_bar": h1_generalizing,
            },
            "H2_self_consistency_orthogonal": {
                "verdict": h2_verdict,
                "bar": f"|Spearman rho| <= {_H2_REDUNDANCY_RHO}",
                "spearman_rho": correlation["spearman_rho"],
            },
        },
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_markdown(payload), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


def _per_family_signal_auroc(
    cells: list[dict[str, Any]],
    agreement: dict[tuple[str, str], dict[str, float]],
    entropy: dict[tuple[str, str], float],
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for family in FAMILIES:
        family_cells = [c for c in cells if c["family"] == family]
        out[family] = {
            "cell_count": len(family_cells),
            "cross_model_agreement": _signal_auroc(
                family_cells,
                lambda c: agreement.get((c["letter_id"], c["family"]), {}).get("risk", 0.0),
            ),
            "self_consistency_entropy": _signal_auroc(
                family_cells,
                lambda c: entropy.get((c["letter_id"], c["family"]), 0.0),
            ),
        }
    return out


def _pooled_signal_auroc(
    cells: list[dict[str, Any]],
    agreement: dict[tuple[str, str], dict[str, float]],
    entropy: dict[tuple[str, str], float],
) -> dict[str, Any]:
    return {
        "cross_model_agreement": _signal_auroc(
            cells,
            lambda c: agreement.get((c["letter_id"], c["family"]), {}).get("risk", 0.0),
        ),
        "self_consistency_entropy": _signal_auroc(
            cells, lambda c: entropy.get((c["letter_id"], c["family"]), 0.0)
        ),
    }


def _signal_auroc(cells: list[dict[str, Any]], risk_fn: Any) -> dict[str, float]:
    risks = [float(risk_fn(c)) for c in cells]
    labels = [not bool(c["correct"]) for c in cells]
    return {
        "auroc_error": round(external_signals.auroc(risks, labels), 4),
        "coverage": round(sum(1 for r in risks if r > 0.0) / len(risks), 4) if risks else 0.0,
    }


def _spearman_correlation(
    cells: list[dict[str, Any]],
    agreement: dict[tuple[str, str], dict[str, float]],
    entropy: dict[tuple[str, str], float],
) -> dict[str, Any]:
    pairs = [
        (
            agreement.get((c["letter_id"], c["family"]), {}).get("risk", 0.0),
            entropy.get((c["letter_id"], c["family"]), 0.0),
        )
        for c in cells
    ]
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    rho = _spearman_rho(xs, ys)
    return {
        "n": len(pairs),
        "spearman_rho": round(rho, 4),
        "threshold_for_redundancy": _H2_REDUNDANCY_RHO,
    }


def _spearman_rho(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return 0.0
    rx = _ranks(xs)
    ry = _ranks(ys)
    n = float(len(xs))
    mean_x = sum(rx) / n
    mean_y = sum(ry) / n
    num = sum((a - mean_x) * (b - mean_y) for a, b in zip(rx, ry, strict=True))
    den_x = math.sqrt(sum((a - mean_x) ** 2 for a in rx))
    den_y = math.sqrt(sum((b - mean_y) ** 2 for b in ry))
    if den_x == 0.0 or den_y == 0.0:
        return 0.0
    return num / (den_x * den_y)


def _ranks(values: list[float]) -> list[float]:
    ordered = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(ordered):
        j = i
        while j + 1 < len(ordered) and values[ordered[j + 1]] == values[ordered[i]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[ordered[k]] = avg_rank
        i = j + 1
    return ranks


def _signal_distributions(
    cells: list[dict[str, Any]],
    agreement: dict[tuple[str, str], dict[str, float]],
    entropy: dict[tuple[str, str], float],
) -> dict[str, Any]:
    agreement_counts = Counter(
        agreement.get((c["letter_id"], c["family"]), {}).get("agreement", 3.0) for c in cells
    )
    return {
        "cross_model_agreement_cluster_sizes": {
            str(int(k)): v for k, v in sorted(agreement_counts.items())
        },
        "self_consistency_entropy_mean": round(
            sum(entropy.get((c["letter_id"], c["family"]), 0.0) for c in cells) / len(cells),
            4,
        )
        if cells
        else 0.0,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# ExECTv2 Calibration Signal Probe (dev140)",
        "",
        f"- Generated: `{payload['generated_on']}` by `{payload['generated_by']}`",
        f"- Cells: `{payload['cell_count']}`",
        f"- Boundary: {payload['claim_boundary']}",
        "",
        "## Per-family AUROC (error vs correct)",
        "",
        "| Family | Cells | Cross-model agreement | Self-consistency entropy |",
        "| --- | ---: | ---: | ---: |",
    ]
    for family, row in payload["per_family_auroc"].items():
        lines.append(
            f"| {family} | {row['cell_count']} | "
            f"{row['cross_model_agreement']['auroc_error']:.4f} | "
            f"{row['self_consistency_entropy']['auroc_error']:.4f} |"
        )
    pooled = payload["pooled_auroc"]
    lines.append(
        f"| **pooled** | {payload['cell_count']} | "
        f"**{pooled['cross_model_agreement']['auroc_error']:.4f}** | "
        f"**{pooled['self_consistency_entropy']['auroc_error']:.4f}** |"
    )
    corr = payload["h2_correlation"]
    verdicts = payload["predeclared_verdicts"]
    lines.extend(
        [
            "",
            "## Predeclared verdicts",
            "",
            f"- **H1 (cross-model agreement generalizes):** "
            f"`{verdicts['H1_cross_model_agreement_generalizes']['verdict']}`. "
            f"{verdicts['H1_cross_model_agreement_generalizes']['bar']} "
            f"Non-SF families above bar: "
            f"`{verdicts['H1_cross_model_agreement_generalizes']['non_sf_families_above_bar']}`.",
            f"- **H2 (self-consistency is orthogonal):** "
            f"`{verdicts['H2_self_consistency_orthogonal']['verdict']}`. "
            f"Spearman rho = `{corr['spearman_rho']}` "
            f"(redundancy bar |rho| > {corr['threshold_for_redundancy']}).",
            "",
            "## Signal distributions",
            "",
            f"- Cross-model agreement cluster sizes: "
            f"`{payload['signal_distributions']['cross_model_agreement_cluster_sizes']}`",
            f"- Self-consistency entropy mean: "
            f"`{payload['signal_distributions']['self_consistency_entropy_mean']}`",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
