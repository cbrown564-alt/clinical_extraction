"""Run ExECTv2 self-consistency panels for the selected 2-call GPT-4.1-mini candidate.

The selected candidate regenerates only two live producer surfaces per letter:
the structured key-family event ledger and the Diagnosis decomposer. Seizure
Frequency no-SF-adjudicator projection, Prescription deterministic repair,
Investigations direct lensing, and final finding assembly are no-call rebuilds
from those producer artifacts.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
    build_finding_assembly,
    render_finding_assembly_markdown,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter, load_letters
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_diagnosis_decomposer as dx_decomposer,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_state_projection as sf_projection,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_union_arbitration as sf_union,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_unknown_suppression as sf_suppression,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    self_consistency,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.simplification_frontier import (
    _write_sf_structured_direct_artifact,
    load_simplification_config,
)
from scripts.run_exectv2_v08_full200_gpt41mini_audit import (
    _run_prescription_deterministic,
)

MODEL = "openai/gpt-4.1-mini"
CONFIG_PATH = Path("configs/exectv2/simplification_frontier/03_stage3_2call_no_sf_adjudicator.json")
OUT_DIR = Path("experiments")
REPORT_DIR = Path("docs/experiments/exectv2/reliability")


def main() -> None:
    args = _parse_args()
    run_date = args.date
    all_letters = load_letters()
    letters = _select_letters(all_letters, n=args.n, offset=args.offset)
    temperatures = [float(value) for value in args.temperatures]
    if args.repeats != len(temperatures):
        raise SystemExit("--repeats must match the number of --temperatures entries")

    assembly_paths: list[Path] = []
    structured_paths: list[Path] = []
    dx_paths: list[Path] = []

    for index, temperature in enumerate(temperatures, start=1):
        run_id = _run_id(args.panel_id, index, temperature)
        paths = _run_one_repeat(
            letters,
            run_id=run_id,
            panel_id=args.panel_id,
            run_date=run_date,
            temperature=temperature,
            model=args.model,
            resume=not args.no_resume,
            dspy_cache=not args.no_dspy_cache,
            progress_every=args.progress_every,
        )
        assembly_paths.append(paths["assembly_jsonl"])
        structured_paths.append(paths["structured_jsonl"])
        dx_paths.append(paths["diagnosis_decomposer_jsonl"])

    payload = self_consistency.build_self_consistency_report(
        assembly_jsonl_paths=assembly_paths,
        producer_jsonl_paths={
            "structured_key_family_event_ledger": structured_paths,
            "diagnosis_decomposer": dx_paths,
        },
        panel_id=args.panel_id,
        model=args.model,
        temperatures=temperatures,
        generated_on=date.today().isoformat(),
        letters=letters,
        claim_boundary=(
            "Selected GPT-4.1-mini lean-candidate self-consistency panel. "
            "Final readout is aggregate-only; saved JSONL artifacts preserve "
            "provenance but are not a full-200 row-level failure-analysis ledger."
        ),
    )
    json_path = OUT_DIR / f"exectv2_2call_no_sf_self_consistency_{args.panel_id}_{run_date}.json"
    md_path = REPORT_DIR / f"exectv2_2call_no_sf_self_consistency_{args.panel_id}_{run_date}.md"
    written = self_consistency.write_self_consistency_artifacts(
        payload,
        json_path=json_path,
        markdown_path=md_path,
    )
    print(json.dumps({key: value.as_posix() for key, value in written.items()}, indent=2))


def _run_one_repeat(
    letters: list[ExectLetter],
    *,
    run_id: str,
    panel_id: str,
    run_date: str,
    temperature: float,
    model: str,
    resume: bool,
    dspy_cache: bool,
    progress_every: int,
) -> dict[str, Path]:
    prefix = f"exectv2_2call_no_sf_self_consistency_{run_id}_{run_date}"
    structured_jsonl = OUT_DIR / f"{prefix}_structured.jsonl"
    structured_rows, structured_meta = structured.run_split(
        letters,
        split=panel_id,
        model=model,
        temperature=temperature,
        max_tokens=6000,
        mode="live",
        dspy_cache=dspy_cache,
        progress_every=progress_every,
        checkpoint_jsonl_path=structured_jsonl,
        checkpoint_report_path=structured_jsonl.with_suffix(".md"),
        resume=resume,
        prompt_profile="full",
    )
    write_jsonl(structured_rows, structured_jsonl)
    structured.write_report(
        structured_rows,
        structured_meta,
        structured_jsonl.with_suffix(".md"),
        jsonl_path=structured_jsonl,
    )

    dx_jsonl = OUT_DIR / f"{prefix}_diagnosis_decomposer.jsonl"
    dx_rows, dx_meta = dx_decomposer.run_split(
        letters,
        draft_rows=structured_rows,
        split=panel_id,
        model=model,
        temperature=temperature,
        max_tokens=2600,
        mode="live",
        dspy_cache=dspy_cache,
        progress_every=progress_every,
        checkpoint_jsonl_path=dx_jsonl,
        checkpoint_report_path=dx_jsonl.with_suffix(".md"),
        resume=resume,
    )
    write_jsonl(dx_rows, dx_jsonl)
    dx_decomposer.write_report(dx_rows, dx_meta, dx_jsonl.with_suffix(".md"), jsonl_path=dx_jsonl)

    sf_direct_jsonl = OUT_DIR / f"{prefix}_sf_structured_direct.jsonl"
    _write_sf_structured_direct_artifact(
        source=structured_jsonl,
        output=sf_direct_jsonl,
        letters=letters,
    )
    sf_projection_jsonl = OUT_DIR / f"{prefix}_sf_state_projection_combined.jsonl"
    sf_projection.write_rows_and_report(
        sf_projection.read_rows(sf_direct_jsonl),
        ablation="combined",
        jsonl_path=sf_projection_jsonl,
        report_path=sf_projection_jsonl.with_suffix(".md"),
    )
    sf_suppression_jsonl = OUT_DIR / f"{prefix}_sf_unknown_suppression.jsonl"
    sf_suppression.write_rows_and_report(
        sf_suppression.read_rows(sf_projection_jsonl),
        jsonl_path=sf_suppression_jsonl,
        report_path=sf_suppression_jsonl.with_suffix(".md"),
    )
    sf_union_jsonl = OUT_DIR / f"{prefix}_sf_union_arbitration.jsonl"
    sf_union.write_rows_and_report(
        sf_union.read_rows(sf_suppression_jsonl),
        sf_union.deterministic_rows_from_letters(letters, split=panel_id),
        jsonl_path=sf_union_jsonl,
        report_path=sf_union_jsonl.with_suffix(".md"),
    )

    prescription_jsonl = OUT_DIR / f"{prefix}_prescription_deterministic_repair_v03.jsonl"
    _run_prescription_deterministic(letters, prescription_jsonl)

    assembly_jsonl = OUT_DIR / f"{prefix}_assembly.jsonl"
    assembly_json = assembly_jsonl.with_suffix(".json")
    assembly_md = REPORT_DIR / f"{prefix}_assembly.md"
    _write_assembly(
        letters,
        panel_id=panel_id,
        run_id=run_id,
        structured_jsonl=structured_jsonl,
        diagnosis_jsonl=dx_jsonl,
        sf_jsonl=sf_union_jsonl,
        prescription_jsonl=prescription_jsonl,
        assembly_jsonl=assembly_jsonl,
        assembly_json=assembly_json,
        assembly_md=assembly_md,
    )
    return {
        "structured_jsonl": structured_jsonl,
        "diagnosis_decomposer_jsonl": dx_jsonl,
        "sf_union_jsonl": sf_union_jsonl,
        "prescription_jsonl": prescription_jsonl,
        "assembly_jsonl": assembly_jsonl,
        "assembly_json": assembly_json,
        "assembly_markdown": assembly_md,
    }


def _write_assembly(
    letters: list[ExectLetter],
    *,
    panel_id: str,
    run_id: str,
    structured_jsonl: Path,
    diagnosis_jsonl: Path,
    sf_jsonl: Path,
    prescription_jsonl: Path,
    assembly_jsonl: Path,
    assembly_json: Path,
    assembly_md: Path,
) -> None:
    config = load_simplification_config(CONFIG_PATH)
    base = config.assembly
    producers = dict(base.producers)
    producers["structured_key_family_event_ledger"] = replace(
        producers["structured_key_family_event_ledger"],
        artifact=structured_jsonl,
    )
    producers["diagnosis_decomposer"] = replace(
        producers["diagnosis_decomposer"],
        artifact=diagnosis_jsonl,
    )
    producers["sf_structured_union"] = replace(
        producers["sf_structured_union"],
        artifact=sf_jsonl,
    )
    producers["prescription_deterministic_repair"] = replace(
        producers["prescription_deterministic_repair"],
        artifact=prescription_jsonl,
    )
    manifest = replace(
        base,
        candidate_id=f"{config.candidate_id}_{run_id}",
        split=panel_id,
        row_count=len(letters),
        claim_boundary=(
            "Self-consistency repeat for selected GPT-4.1-mini 2-call no-SF-"
            "adjudicator candidate. Structured ledger and Diagnosis decomposer "
            "are live repeat surfaces; SF/Rx/Inv and final assembly are no-call "
            "deterministic rebuilds."
        ),
        producers=producers,
        promotion_decision="self-consistency-repeat",
    )
    run = build_finding_assembly(manifest, gold_loader=lambda _split: letters)
    assembly_jsonl.parent.mkdir(parents=True, exist_ok=True)
    assembly_json.parent.mkdir(parents=True, exist_ok=True)
    assembly_md.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(run.rows, assembly_jsonl)
    assembly_json.write_text(
        json.dumps(run.report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown = render_finding_assembly_markdown(
        run.report,
        json_path=assembly_json,
        jsonl_path=assembly_jsonl,
    )
    assembly_md.write_text(markdown, encoding="utf-8")
    headline = run.report["score_ladder"]["headline_target"]["overall"]
    print(
        f"[{run_id}] assembly F1={headline['f1']:.4f} "
        f"P={headline['precision']:.4f} R={headline['recall']:.4f}"
    )


def _select_letters(
    letters: list[ExectLetter],
    *,
    n: int,
    offset: int,
) -> list[ExectLetter]:
    if n <= 0:
        return letters[offset:]
    return letters[offset : offset + n]


def _run_id(panel_id: str, repeat_index: int, temperature: float) -> str:
    temp = str(temperature).replace(".", "p")
    clean_panel = re.sub(r"[^a-zA-Z0-9_]+", "_", panel_id).strip("_")
    return f"{clean_panel}_r{repeat_index}_temp{temp}"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run self-consistency repeats for the ExECTv2 2-call no-SF candidate."
    )
    parser.add_argument("--panel-id", required=True)
    parser.add_argument("--n", type=int, default=50, help="Number of letters; <=0 means all.")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--repeats", type=int, required=True)
    parser.add_argument("--temperatures", nargs="+", required=True)
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--date", default=date.today().isoformat().replace("-", ""))
    parser.add_argument("--progress-every", type=int, default=10)
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument(
        "--no-dspy-cache",
        action="store_true",
        help="Disable DSPy cache. Use this for genuine live repeat/entropy panels.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
