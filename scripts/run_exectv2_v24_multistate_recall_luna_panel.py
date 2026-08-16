"""Run the predeclared v24/v25 multi-state recall panel on Luna."""

# ruff: noqa: E501

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters_for_split
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from scripts import run_exectv2_structured_prompt_v10_luna_dev20 as v10_run
from scripts import run_exectv2_structured_prompt_v13_luna_dev20 as v13
from scripts import run_exectv2_structured_prompt_v17_luna_dev20 as v17_run

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/exectv2/structured_prompt_v24_multistate_recall_luna_panel_protocol_2026-08-16.md"
TRANSFER_PROTOCOL = "docs/research/exectv2/structured_prompt_v24_multistate_recall_luna_dev140_transfer_protocol_2026-08-16.md"
PANEL_SOURCE = ROOT / "experiments/exectv2_v19_sf_priority_study_dev140_20260816/targeted_rows.jsonl"
RESIDUAL_SOURCE = ROOT / "experiments/exectv2_v19_sf_residual_analysis_dev140_20260816/rows.jsonl"
V19_SOURCE = ROOT / "experiments/exectv2_structured_prompt_v19_luna_dev140_20260815/v19_live/structured.jsonl"
STUDY_DIR = ROOT / "experiments/exectv2_v24_multistate_recall_luna_panel_20260816"
TRANSFER_DIR = ROOT / "experiments/exectv2_structured_prompt_v24_luna_dev140_20260816"
V25_STUDY_DIR = ROOT / "experiments/exectv2_v25_cui_first_luna_panel_20260816"
V25_TRANSFER_DIR = ROOT / "experiments/exectv2_structured_prompt_v25_cui_first_luna_dev140_20260816"
MODEL = "openai/gpt-5.6-luna"


def _panel_ids() -> list[str]:
    targets = [json.loads(line) for line in PANEL_SOURCE.read_text(encoding="utf-8").splitlines() if line]
    residuals = [json.loads(line) for line in RESIDUAL_SOURCE.read_text(encoding="utf-8").splitlines() if line]
    ids = [row["source_row_index"] for row in targets if row["study_category"] == "multi_state_recall"]
    if len(ids) != 32:
        raise RuntimeError(f"expected 32 multi-state target rows, found {len(ids)}")
    empty_gold = [
        row["source_row_index"]
        for row in residuals
        if row["failure_bucket"] == "accepted_false_positive_empty_gold"
    ]
    ids = sorted(set(ids) | set(empty_gold))
    if len(ids) != 41:
        raise RuntimeError(f"expected 41 panel rows, found {len(ids)}")
    return ids


def _letters(ids: set[str]) -> list[Any]:
    letters = sorted(load_letters_for_split("dev"), key=lambda letter: letter.letter_id)
    return [letter for letter in letters if letter.letter_id in ids]


def verify_payload(prompt_version: str) -> dict[str, Any]:
    letter = _letters({"EA0002"})[0]
    payload_str = structured.build_prompt_input(letter, prompt_version=prompt_version)
    payload = json.loads(payload_str)
    instructions = json.dumps({key: value for key, value in payload.items() if key != "letter_text"}).lower()
    required = [
        "one separate mention for each independent",
        "do not collapse those facts into one generic",
        "do not omit an unknown state",
    ]
    if prompt_version == structured.PROMPT_VERSION_V25:
        required.extend(("most specific seizure-type wording", "do not add a phrase-only duplicate"))
    if any(phrase not in instructions for phrase in required):
        raise RuntimeError(f"{prompt_version} rule missing from rendered payload")
    if "ea0002" in instructions or "prompt_version" in payload or "letter_id" in payload:
        raise RuntimeError(f"{prompt_version} leaked research metadata into the model-facing payload")
    user_content = str(structured.DspyKeyEntitiesStructuredExtractor(prompt_version=prompt_version).render_messages(prompt_input_json=payload_str)[1]["content"])
    if user_content.count(payload_str) != 1:
        raise RuntimeError(f"{prompt_version} payload was duplicated or omitted in rendered request")
    return {
        "prompt_version": prompt_version,
        "payload_sha256": hashlib.sha256(payload_str.encode()).hexdigest(),
        "user_message_sha256": hashlib.sha256(user_content.encode()).hexdigest(),
        "required_phrases": required,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transfer", action="store_true")
    parser.add_argument("--v25", action="store_true")
    args = parser.parse_args()
    candidate_prompt_version = structured.PROMPT_VERSION_V25 if args.v25 else structured.PROMPT_VERSION_V24
    if args.transfer:
        ids = [letter.letter_id for letter in sorted(load_letters_for_split("dev"), key=lambda letter: letter.letter_id)]
        study_dir = V25_TRANSFER_DIR if args.v25 else TRANSFER_DIR
        protocol = (
            "docs/research/exectv2/structured_prompt_v25_cui_first_luna_dev140_transfer_protocol_2026-08-16.md"
            if args.v25
            else TRANSFER_PROTOCOL
        )
    else:
        ids = _panel_ids()
        study_dir = V25_STUDY_DIR if args.v25 else STUDY_DIR
        protocol = (
            "docs/research/exectv2/structured_prompt_v25_cui_first_luna_panel_protocol_2026-08-16.md"
            if args.v25
            else PROTOCOL
        )
    letters = _letters(set(ids))
    expected_n = 140 if args.transfer else 41
    if len(letters) != expected_n:
        raise RuntimeError(f"expected {expected_n} loaded letters, found {len(letters)}")
    request_shape = verify_payload(candidate_prompt_version)
    study_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    original_dir = v10_run.STUDY_DIR
    original_control = v10_run.CONTROL_STRUCTURED
    original_assembly = v10_run._arm_assembly
    try:
        v10_run.STUDY_DIR = study_dir

        def _patched_assembly(slug: str, structured_path: Path, sf_final_path: Path) -> Any:
            cfg = original_assembly(slug, structured_path, sf_final_path)
            return replace(
                cfg,
                candidate_id=f"exectv2_{'v25_cui_first' if args.v25 else 'v24_multistate_recall'}_luna_panel_{slug}",
                split="dev",
                row_count=expected_n,
                claim_boundary=(
                    (
                        "ExECT v25 CUI-first multi-state recall transfer on dev140."
                        if args.v25
                        else "ExECT v24 multi-state recall transfer on dev140."
                    )
                    if args.transfer
                    else (
                        "Focused ExECT v25 CUI-first multi-state recall panel on dev140."
                        if args.v25
                        else "Focused ExECT v24 multi-state recall panel on dev140."
                    )
                ),
            )

        v10_run._arm_assembly = _patched_assembly
        v10_run.CONTROL_STRUCTURED = V19_SOURCE
        control = v13._run_enriched_arm(
            slug="v19_head",
            prompt_version=structured.PROMPT_VERSION_V19,
            letters=letters,
            call_mode="saved_structured_no_call",
            overwrite=True,
            progress_every=10,
            api_base=None,
        )
        candidate = v13._run_enriched_arm(
            slug="v25_live" if args.v25 else "v24_live",
            prompt_version=candidate_prompt_version,
            letters=letters,
            call_mode="live",
            overwrite=True,
            progress_every=5,
            api_base=None,
        )
    finally:
        v10_run.STUDY_DIR = original_dir
        v10_run.CONTROL_STRUCTURED = original_control
        v10_run._arm_assembly = original_assembly

    candidate_slug = "v25_live" if args.v25 else "v24_live"
    for result, slug in ((control, "v19_head"), (candidate, candidate_slug)):
        v17_run._add_sink_summary(result, study_dir / slug / "structured.jsonl")
    artifact = {
        "schema_version": "exectv2.v25_cui_first_luna_panel.v1" if args.v25 else "exectv2.v24_multistate_recall_luna_panel.v1",
        "generated_on": "2026-08-16",
        "protocol": protocol,
        "model": MODEL,
        "split": "dev140",
        "row_policy": f"{expected_n} permitted development rows; test60 sealed",
        "panel_ids": ids,
        "model_calls": 41,
        "request_shape": request_shape,
        "control": control["summary"],
        "candidate": candidate["summary"],
        "source_artifacts": {"v19_structured": str(V19_SOURCE.relative_to(ROOT))},
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
    }
    (study_dir / "comparison.json").write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
