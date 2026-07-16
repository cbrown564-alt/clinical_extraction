"""Retry named permitted ExECT development rows and merge only clean replacements."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines import (
    key_entities_structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    has_blocking_parse_issue,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import model_swap
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from scripts.run_exectv2_six_model_comparison import (
    build_six_model_lm,
    configure_declared_runtime,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--letter-id", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    config = model_swap.load_model_swap_config(args.config)
    if config.assembly.split.lower() not in {"dev", "dev140"}:
        raise SystemExit("targeted retry is restricted to permitted development rows")
    requested = list(dict.fromkeys(args.letter_id))
    by_id = {letter.letter_id: letter for letter in load_letters_for_split("dev")}
    missing = sorted(set(requested) - set(by_id))
    if missing:
        raise SystemExit(f"requested IDs are not in dev140: {missing}")

    configure_declared_runtime(args.config)
    key_entities_structured.runner.build_dspy_lm = build_six_model_lm
    rows, _ = structured.run_split(
        [by_id[letter_id] for letter_id in requested],
        split="dev140_targeted_retry",
        model=config.model,
        temperature=config.temperature,
        max_tokens=int(config.max_tokens["structured_key_family_event_ledger"]),
        mode="live",
        dspy_cache=False,
        prompt_profile=config.prompt_profile,  # type: ignore[arg-type]
        checkpoint_jsonl_path=args.output,
        checkpoint_report_path=args.output.with_suffix(".md"),
    )
    write_jsonl_rows(rows, args.output)
    failures = [
        row["letter_id"]
        for row in rows
        if row.get("call_error") or has_blocking_parse_issue(row.get("parse_errors"))
    ]
    if len(rows) != len(requested) or failures:
        raise RuntimeError(
            f"targeted retry did not produce clean replacements: rows={len(rows)}, "
            f"failures={failures}"
        )

    target = config.assembly.producers["structured_key_family_event_ledger"].artifact
    original = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines()]
    replacements = {row["letter_id"]: row for row in rows}
    if set(replacements) != set(requested):
        raise RuntimeError("targeted retry returned an unexpected row identity set")
    backup = target.with_suffix(".pre_ctx_retry.jsonl")
    if not backup.exists():
        shutil.copy2(target, backup)
    merged = [replacements.get(row["letter_id"], row) for row in original]
    write_jsonl_rows(merged, target)
    print(json.dumps({"replaced": requested, "target": target.as_posix()}, sort_keys=True))


if __name__ == "__main__":
    main()
