"""No-call replay of 2026-07-15 DeepSeek ExECTv2 structured outputs on current rules.

Re-derives the SF projection/suppression chain and finding assembly under the
working-tree deterministic stack. Does not make model calls. Used as the
ruleset-matched comparator for the DeepSeek-V4-Flash-0731 update study.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import model_swap

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from scripts import run_exectv2_2call_model_swap as swap_runner  # noqa: E402
CONFIG_PATH = (
    REPO_ROOT
    / "configs/exectv2/six_model_comparison"
    / "deepseek_v4_flash_20260715_model_current_rules_dev140.json"
)
SOURCE_STRUCTURED = (
    REPO_ROOT
    / "experiments/exectv2_six_model_single_call_deepseek_v4_flash_dev140_20260715_structured.jsonl"
)
GENERATED_ON = "2026-07-31"


def main() -> None:
    config = model_swap.load_model_swap_config(CONFIG_PATH)
    if not SOURCE_STRUCTURED.is_file():
        raise FileNotFoundError(SOURCE_STRUCTURED)
    structured_path = config.assembly.producers[
        "structured_key_family_event_ledger"
    ].artifact
    if structured_path.resolve() != SOURCE_STRUCTURED.resolve():
        raise ValueError(
            "config structured producer must point at the frozen 2026-07-15 artifact: "
            f"{SOURCE_STRUCTURED}"
        )
    letters = load_letters_for_split("dev")
    if len(letters) != config.assembly.row_count:
        raise ValueError(
            f"expected {config.assembly.row_count} dev letters, found {len(letters)}"
        )
    sf_output = config.assembly.producers["sf_model_projection_suppression"].artifact
    swap_runner._run_model_led_sf_chain(
        structured_jsonl=structured_path,
        sf_output_jsonl=sf_output,
        letters=letters,
    )
    run = model_swap.write_model_swap_candidate_artifacts(
        config,
        generated_on=GENERATED_ON,
        gold_loader=lambda _split: letters,
    )
    # Ensure policy fields reflect the active default/default stack.
    report = dict(run.report)
    report["diagnosis_policy_variant"] = report.get("diagnosis_policy_variant", "default")
    report["prescription_policy_variant"] = report.get(
        "prescription_policy_variant", "default"
    )
    report["claim_boundary"] = config.claim_boundary
    report["runtime"] = {
        "mode": "saved_structured_no_call_current_rules",
        "source_structured": SOURCE_STRUCTURED.as_posix(),
        "new_model_calls": 0,
    }
    config.output_json.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    headline = report["score_ladder"]["headline_target"]
    print(
        json.dumps(
            {
                "candidate_id": config.candidate_id,
                "source_structured": SOURCE_STRUCTURED.as_posix(),
                "json": config.output_json.as_posix(),
                "jsonl": config.output_jsonl.as_posix(),
                "markdown": config.output_markdown.as_posix(),
                "overall_clinical_headline_f1": headline["overall"]["f1"],
                "by_indicator_f1": {
                    entity: payload["f1"]
                    for entity, payload in headline["by_indicator"].items()
                },
                "new_model_calls": 0,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
