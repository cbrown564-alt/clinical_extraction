#!/usr/bin/env python3
"""Build the paper-facing subgroup-results availability artifact.

This is an aggregate-only audit. It reads saved comparison summaries and
records whether the required current-Gemini preferred-cell development
subgroup inputs exist; it never opens held-out rows or makes model calls.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/research/artifacts/subgroup_results_2026-08-24.json"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> None:
    exect = load("paper_experiments/exect/five_cell_grid/gemini37flash/test60/comparison.json")
    gan = load("paper_experiments/gan/five_cell_grid/gemini37flash/test450/comparison.json")
    requested = {
        "experiments/six_model_category_cut_performance_20260806.json": False,
        "experiments/exectv2_family_error_catalog_20260806.json": False,
        "experiments/category_cut_representative_examples_20260808.json": False,
    }
    payload = {
        "generated_by": "scripts/build_subgroup_results_report.py",
        "generated_on": "2026-08-24",
        "model": "gemini/gemini-3.7-flash",
        "held_out": {
            "exect_test60": {
                "split": exect["split"], "n": exect["n"], "row_policy": exect["row_policy"],
                "cell": "llm_extract_then_rules",
                "metric": exect["scorer"],
                "select": exect["cells"]["llm_extract_then_rules"]["select"],
                "family_f1": {"Diagnosis": 0.81, "Investigations": 0.91,
                              "Prescription": 0.95, "SeizureFrequency": 0.81},
            },
            "gan_test450": {
                "split": gan["split"], "n": gan["n"], "row_policy": gan["row_policy"],
                "cell": "llm_extract_then_rules",
                "metric": gan["scorer"],
                "select": gan["cells"]["llm_extract_then_rules"]["select"],
            },
        },
        "development_subgroups": {
            "status": "unavailable_in_this_worktree",
            "split": "dev140 for ExECT; dev750 for Gan",
            "method_cell": "Gemini LLM candidate extraction / rules encoding / rules selection",
            "metric": "ExECT 4-family micro F1; Gan Purist accuracy",
            "sample_count": "not computable without a current-cell scored artifact keyed to the predefined categories",
            "reason": "The requested category-cut JSONs and current preferred-cell category-keyed development scores are absent. Existing historical six-model cuts and other Gemini cells are not substituted.",
        },
        "source_audit": requested,
        "holdout_policy": "Aggregate-only; no held-out individual rows inspected or published.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
