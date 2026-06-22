"""Render the ExECTv2 frontend review data to the committed dev fallback.

Thin CLI wrapper over
``clinical_extraction.tasks.epilepsy_phenotyping.exectv2.frontend_review`` — the
shared source of truth that the live ``GET /exectv2/runs`` API route also uses.
Running this script writes the same payload to ``frontend/public/mock-data`` so
the committed fallback matches exactly what the backend serves; updating the
canonical ``docs/experiments/final_artifact_index_*.md`` and re-running this is
the only step needed to incorporate a new architecture.
"""

from __future__ import annotations

import json
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.frontend_review import (
    FALLBACK_TEXT_SOURCES,
    REPO_ROOT,
    _architecture_family,
    _decision_from_heading,
    _promotion_slug,
    build_exectv2_runs,
    find_index_path,
    index_date,
    load_run_specs_from_index,
    parse_canonical_exectv2_runs,
    validate_specs,
)

# Re-exported for the generator's unit tests, which load this script by path.
__all__ = [
    "FALLBACK_TEXT_SOURCES",
    "_architecture_family",
    "_decision_from_heading",
    "_promotion_slug",
    "find_index_path",
    "index_date",
    "load_run_specs_from_index",
    "parse_canonical_exectv2_runs",
    "update_registry",
    "validate_specs",
    "main",
]

ROOT = REPO_ROOT
MOCK_ROOT = ROOT / "frontend" / "public" / "mock-data"
EXECTV2_ROOT = MOCK_ROOT / "exectv2"
ARTIFACT_ROOT = MOCK_ROOT / "artifacts"


def update_registry(runs: list[dict[str, Any]]) -> None:
    registry_path = MOCK_ROOT / "registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    existing_runs = [
        run for run in registry.get("runs", []) if run.get("task", "gan2026") != "exectv2"
    ]
    exectv2_entries = []
    for run in runs:
        exectv2_entries.append(
            {
                "task": "exectv2",
                "run_id": run["run_id"],
                "pipeline_family": run["pipeline_family"],
                "architecture_family": run["architecture_family"],
                "date": run["date"],
                "row_count": run["row_count"],
                "artifact_paths": run["artifact_paths"],
                "mode": run["label"],
                "model": run["model"],
                "model_role": run["promotion_decision"],
                "split": run["split"],
                "decision": run["decision"],
                "claim_boundary": run["claim_boundary"],
                "scorer_view": run["scorer_view"],
            }
        )
    registry["runs"] = existing_runs + exectv2_entries
    registry_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    EXECTV2_ROOT.mkdir(parents=True, exist_ok=True)
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

    index_path, runs = build_exectv2_runs(strict=True)

    for run in runs:
        (ARTIFACT_ROOT / f"{run['run_id']}.json").write_text(
            json.dumps(
                {
                    "run_id": run["run_id"],
                    "artifact_path": run["artifact_paths"][-1],
                    "artifact_type": "exectv2_frontend_letters",
                    "content": run["letters"],
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    payload = {
        "generated_on": index_date(index_path),
        "source_index": index_path.relative_to(ROOT).as_posix(),
        "runs": runs,
    }
    (EXECTV2_ROOT / "runs.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    update_registry(runs)

    print(
        f"Wrote {len(runs)} ExECTv2 frontend runs from "
        f"{index_path.relative_to(ROOT).as_posix()}:"
    )
    for run in runs:
        print(f"  [{run['decision']:>14}] {run['split']:>6}  {run['run_id']}")


if __name__ == "__main__":
    main()
