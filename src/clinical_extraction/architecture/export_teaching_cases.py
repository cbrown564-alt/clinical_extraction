"""Write frontend/public/mock-data/teaching-cases.json from paper letters."""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.architecture.paper_cell_teaching import PAPER_METHOD_IDS
from clinical_extraction.architecture.paper_teaching_cases import (
    build_paper_teaching_letters,
)
from clinical_extraction.core.paths import discover_repo_root

ROOT = discover_repo_root(start=Path(__file__))
DEFAULT_OUT = ROOT / "frontend/public/mock-data/teaching-cases.json"

ONE_SENTENCE = {
    "gan_rules": "Rules extract, encode, and select the Gan label.",
    "gan_llm_pre_post_label_forms": "Both extract, then rule encode and select.",
    "gan_llm_extract_label_forms": "LLM codebook extract, then rule encode and select.",
    "gan_llm_encode": "Same codebook extract already in form; rule select only.",
    "gan_llm_select_from_extract": "LLM extract, encode form, and select.",
    "exect_rules": "Rules extract, encode, and select four-family findings.",
    "exect_llm_pre_post": "Both extract, then rule encode and select.",
    "exect_llm_only": "LLM extract, then rule encode and select.",
    "exect_llm_encode": "LLM extract and encode, then accepted select rules.",
    "exect_llm_select": "LLM extract, encode, and select.",
}


def _manifest_from_run(run_payload: dict) -> dict:
    stages = []
    for obs in run_payload["observations"]:
        stages.append(
            {
                "stage_id": obs["stage_id"],
                "name": obs["stage_name"],
                "operation": obs.get("note") or obs["stage_name"],
                "owner": obs["owner"],
                "effect_class": obs["effect_class"],
                "may_change_clinical_meaning": obs["effect_class"] == "clinical_meaning",
                "input_type": "text",
                "input_example": "",
                "output_type": "text",
                "output_example": "",
                "implementation": {"path": "", "symbol": ""},
                "governing_test": "",
                "trace_fields": [],
                "paper_wording": obs.get("note") or "",
            }
        )
    return {
        "method_id": run_payload["method_id"],
        "task": "gan2026" if run_payload["method_id"].startswith("gan_") else "exectv2",
        "task_label": "Gan 2026" if run_payload["method_id"].startswith("gan_") else "ExECTv2",
        "method": run_payload["method_id"],
        "method_label": run_payload["method_label"],
        "role": "paper cell",
        "entry_point": {"path": "", "symbol": ""},
        "one_sentence": ONE_SENTENCE.get(
            run_payload["method_id"], run_payload.get("one_sentence") or ""
        ),
        "sixty_second": "",
        "prediction_owner": run_payload.get("prediction_owner") or "",
        "scored_representation": "",
        "stages": stages,
    }


def build_payload() -> dict:
    cases = []
    manifests_by_id: dict[str, dict] = {}
    for case in build_paper_teaching_letters():
        payload = case.to_dict()
        payload["runs"] = [
            run
            for run in payload["runs"]
            if run["method_id"] in PAPER_METHOD_IDS
        ]
        for run in payload["runs"]:
            run["one_sentence"] = ONE_SENTENCE.get(run["method_id"], run["one_sentence"])
            manifests_by_id.setdefault(run["method_id"], _manifest_from_run(run))
        cases.append(payload)
    order = list(PAPER_METHOD_IDS)
    manifests = [manifests_by_id[key] for key in order if key in manifests_by_id]
    return {"cases": cases, "manifests": manifests}


def write_teaching_cases(path: Path | None = None) -> Path:
    out = path or DEFAULT_OUT
    out.write_text(json.dumps(build_payload(), indent=2) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    written = write_teaching_cases()
    print(written)
