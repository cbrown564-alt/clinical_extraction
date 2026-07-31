"""Reassemble saved Luna A/B/C producers under default Diagnosis/Prescription.

Decision 0045: active Luna comparisons use default/default. Existing structured
and SF suppression artifacts are reused; zero new model calls. Previous joint
assemblies are renamed with a ``_joint_archived`` suffix before overwrite.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
    build_finding_assembly,
    render_finding_assembly_markdown,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    has_blocking_parse_issue,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows as write_jsonl,
)
from scripts import run_exectv2_luna_prompt_variants_dev140 as dev140
from scripts import run_exectv2_luna_prompt_variants_test60 as test60

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATED_ON = "2026-07-31"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--split",
        choices=("dev140", "test60", "all"),
        default="all",
    )
    args = parser.parse_args()
    results: dict[str, Any] = {}
    if args.split in {"dev140", "all"}:
        results["dev140"] = _reassemble_dev140()
    if args.split in {"test60", "all"}:
        results["test60"] = _reassemble_test60()
    print(json.dumps(results, indent=2, sort_keys=True))


def _reassemble_dev140() -> dict[str, Any]:
    config = dev140._load_config(dev140.DEFAULT_CONFIG)
    gold = load_letters_for_split("dev")
    out: dict[str, Any] = {"variants": {}}
    for variant in config["variants"]:
        slug = str(variant["slug"])
        structured = dev140._structured_path(config, slug)
        sf_final = dev140._sf_final_path(config, slug)
        assembly_json = dev140._assembly_json_path(config, slug)
        assembly_jsonl = dev140._assembly_jsonl_path(config, slug)
        _archive_if_exists(assembly_json)
        _archive_if_exists(assembly_jsonl)
        _archive_if_exists(assembly_json.with_suffix(".md"))
        assembly = dev140._variant_assembly(config, slug, structured, sf_final)
        run = build_finding_assembly(
            assembly,
            generated_on=GENERATED_ON,
            gold_loader=lambda _split, letters=gold: list(letters),
            diagnosis_resolution_candidate=True,
            diagnosis_policy_variant="default",
            prescription_policy_variant="default",
        )
        report = dict(run.report)
        report["prompt_version"] = variant["prompt_version"]
        report["variant_slug"] = slug
        report["repair_policy"] = config["repair_policy"]
        report["claim_boundary"] = (
            "ExECTv2 Luna prompt-variant development comparison on dev140 under "
            "default Diagnosis/Prescription policy (decision 0045)."
        )
        write_jsonl(run.rows, assembly_jsonl)
        assembly_json.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        assembly_json.with_suffix(".md").write_text(
            render_finding_assembly_markdown(
                report,
                json_path=assembly_json,
                jsonl_path=assembly_jsonl,
            ),
            encoding="utf-8",
        )
        out["variants"][slug] = {
            "overall_f1": report["score_ladder"]["headline_target"]["overall"]["f1"]
        }
    panel_dir = REPO_ROOT / "experiments" / "exectv2_luna_prompt_variants_dev140_20260731"
    _archive_if_exists(panel_dir / "panel_summary.json")
    _archive_if_exists(panel_dir / "panel.jsonl")
    finalize = dev140.finalize(config)
    out["finalize"] = finalize
    return out


def _reassemble_test60() -> dict[str, Any]:
    config = test60._load_config(test60.DEFAULT_CONFIG)
    gold = load_letters_for_split("test")[: int(config["row_count"])]
    out: dict[str, Any] = {"variants": {}}
    for variant in config["variants"]:
        slug = str(variant["slug"])
        structured = test60._structured_path(config, slug)
        sf_final = test60._sf_final_path(config, slug)
        assembly_jsonl = test60._assembly_jsonl_path(config, slug)
        aggregate_path = test60._aggregate_path(config, slug)
        _archive_if_exists(assembly_jsonl)
        _archive_if_exists(aggregate_path)
        assembly = test60._variant_assembly(config, slug, structured, sf_final)
        run = build_finding_assembly(
            assembly,
            generated_on=GENERATED_ON,
            gold_loader=lambda _split, letters=gold: list(letters),
            diagnosis_resolution_candidate=True,
            diagnosis_policy_variant="default",
            prescription_policy_variant="default",
        )
        write_jsonl(run.rows, assembly_jsonl)
        counts = test60._aggregate_letter_counts(
            gold=gold,
            structured_path=structured,
            sf_direct_path=test60._sf_direct_path(config, slug),
            assembly_jsonl=assembly_jsonl,
        )
        headline = run.report["score_ladder"]["headline_target"]
        rows = test60._read_jsonl(structured)
        aggregate = {
            "schema_version": "exectv2.luna_prompt_variants_test60_aggregate.v1",
            "variant": slug,
            "model": config["model"],
            "split": "test60",
            "row_policy": "aggregate_only",
            "prompt_version": variant["prompt_version"],
            "repair_policy": config["repair_policy"],
            "call_mode": "saved_structured_no_call_reassemble_default",
            "new_model_calls": 0,
            "rows": int(config["row_count"]),
            "call_failures": sum(bool(row.get("call_error")) for row in rows),
            "parse_failures": sum(
                has_blocking_parse_issue(row.get("parse_errors")) for row in rows
            ),
            "joint_headline_f1": float(headline["overall"]["f1"]),
            "joint_family_f1": {
                family: float(headline["by_indicator"][family]["f1"])
                for family in test60.FAMILIES
            },
            "model_owned_letter_correct": counts["model_owned_letter_correct"],
            "joint_letter_correct": counts["joint_letter_correct"],
            "structured_sha256": test60._sha256(structured),
            "sf_final_sha256": test60._sha256(sf_final),
            "assembly_sha256": test60._sha256(assembly_jsonl),
            "claim_boundary": (
                "Aggregate-only Luna-versus-Luna test60 transfer evidence under "
                "default Diagnosis/Prescription policy (decision 0045)."
            ),
        }
        aggregate_path.write_text(
            json.dumps(aggregate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        out["variants"][slug] = {
            "overall_f1": aggregate["joint_headline_f1"],
            "sf_f1": aggregate["joint_family_f1"]["SeizureFrequency"],
        }
    panel_dir = REPO_ROOT / "experiments" / "exectv2_luna_prompt_variants_test60_20260731"
    _archive_if_exists(panel_dir / "panel.json")
    finalize = test60.finalize(config)
    out["finalize"] = {
        "complete": finalize.get("complete"),
        "panel": finalize.get("panel"),
        "report": finalize.get("report"),
        "comparison_vs_A": finalize.get("comparison_vs_A"),
    }
    return out


def _archive_if_exists(path: Path) -> None:
    if not path.exists():
        return
    archived = path.with_name(f"{path.stem}_joint_archived{path.suffix}")
    if archived.exists():
        return
    shutil.copy2(path, archived)


if __name__ == "__main__":
    main()
