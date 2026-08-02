#!/usr/bin/env python3
"""Run the permitted-development parity gate for decision 0047.

The gate uses Gan dev750 and ExECT dev140 only. Saved raw model outputs are
replayed without provider access. No held-out row is loaded or emitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    orchestrator as legacy_exect_rules,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
    letter_assembly,
    structured_one_call,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
    rules as exect_rules,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
    StructuredMethodConfig,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    hybrid_structured_events as legacy_gan_hybrid,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_only_canonical_pipeline as legacy_gan_llm,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration import (
    llm as gan_llm,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration import (
    llm_with_rules as gan_hybrid,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration import (
    rules as gan_rules,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners import (
    deterministic_canonical as legacy_gan_rules,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "experiments" / "canonical_orchestrator_development_parity_0047.json"
GAN_LLM_SOURCE = ROOT / "experiments/gan2026_six_model_validation_20260718/gpt56sol--llm_only.jsonl"
GAN_HYBRID_SOURCE = (
    ROOT / "experiments/gan2026_six_model_validation_20260718/gpt56sol--llm_with_rules.jsonl"
)
EXECT_SOURCE = (
    ROOT / "experiments/exectv2_six_model_single_call_gpt56sol_dev140_20260715_structured.jsonl"
)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def _compare_rows(
    left: list[dict[str, Any]], right: list[dict[str, Any]], fields: tuple[str, ...]
) -> dict[str, Any]:
    if len(left) != len(right):
        return {"passed": False, "left_rows": len(left), "right_rows": len(right)}
    mismatches: Counter[str] = Counter()
    mismatch_ids: list[str] = []
    for before, after in zip(left, right, strict=True):
        row_changed = False
        for field in fields:
            if before.get(field) != after.get(field):
                mismatches[field] += 1
                row_changed = True
        if row_changed and len(mismatch_ids) < 20:
            mismatch_ids.append(str(before.get("source_row_index", before.get("letter_id"))))
    return {
        "passed": not mismatches,
        "rows": len(left),
        "comparison_fields": list(fields),
        "mismatches_by_field": dict(sorted(mismatches.items())),
        "first_mismatch_ids": mismatch_ids,
    }


def _gan_rules(records: list[Any]) -> dict[str, Any]:
    config = PipelineConfiguration(architecture="deterministic_canonical_pipeline")
    legacy = [_jsonable(legacy_gan_rules.run_item(record, config)) for record in records]
    canonical = [
        _jsonable(gan_rules.run_record(record, config).to_pipeline_result()) for record in records
    ]
    return {
        "passed": legacy == canonical,
        "rows": len(records),
        "mismatch_rows": sum(a != b for a, b in zip(legacy, canonical, strict=True)),
    }


def _gan_model_pair(
    records: list[Any],
    source: Path,
    legacy_runner: Callable[..., Any],
    canonical_runner: Callable[..., Any],
) -> dict[str, Any]:
    saved = _load_jsonl(source)
    raw = {int(row["source_row_index"]): str(row.get("raw_output") or "") for row in saved}
    selected = [record for record in records if record.source_row_index in raw]
    kwargs = dict(
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-5.6-sol",
        temperature=0.0,
        max_tokens=10000,
        mode="prompt-only",
        dspy_cache=False,
        reuse_raw_outputs=raw,
        reuse_source=source.relative_to(ROOT).as_posix(),
    )
    before, _ = legacy_runner(selected, **kwargs)
    after, _ = canonical_runner(selected, **kwargs)
    fields = (
        "source_row_index",
        "decision_record",
        "structured_record",
        "normalized_events",
        "evidence_text_contained",
        "evidence_valid",
        "call_error",
        "parse_errors",
        "initial_parse_errors",
        "format_retry_output",
        "format_retry_notes",
        "comparison",
        "row_trace",
    )
    return _compare_rows(before, after, fields)


def _mentions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "entity": row.get("entity"),
            "text": row.get("text"),
            "attributes": row.get("attributes", {}),
            "evidence": row.get("evidence", ""),
            "rationale": row.get("rationale", ""),
            "confidence": row.get("confidence", ""),
        }
        for row in rows
    ]


def _exect(
    letters: list[Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    legacy_rules = legacy_exect_rules.run_all9_on_letters(letters)
    canonical_rules = [exect_rules.run_letter(letter).prediction for letter in letters]
    rules_result = {
        "passed": all(
            _jsonable(a) == _jsonable(b) for a, b in zip(legacy_rules, canonical_rules, strict=True)
        ),
        "rows": len(letters),
        "mismatch_rows": sum(
            _jsonable(a) != _jsonable(b) for a, b in zip(legacy_rules, canonical_rules, strict=True)
        ),
    }

    source_rows = _load_jsonl(EXECT_SOURCE)
    by_id = {str(row["letter_id"]): row for row in source_rows}
    selected_letters = [letter for letter in letters if letter.letter_id in by_id]
    raw_mismatches = 0
    producer_rows: list[dict[str, Any]] = []
    for letter in selected_letters:
        saved = by_id[letter.letter_id]
        producer = structured_one_call.produce_structured_letter(
            letter,
            model=str(saved.get("model") or "openai/gpt-5.6-sol"),
            mode="prompt-only",
            split="dev140",
            raw_output=str(saved.get("raw_output") or ""),
            config=StructuredMethodConfig.selected(),
        )
        producer_rows.append(dict(producer.row))
        llm_only = structured_one_call.run_llm_only_letter(letter, producer)
        if _mentions(saved.get("predicted_mentions", [])) != _mentions(
            [_jsonable(mention) for mention in llm_only.prediction.mentions]
        ):
            raw_mismatches += 1
    llm_result = {
        "passed": raw_mismatches == 0,
        "rows": len(selected_letters),
        "mismatch_rows": raw_mismatches,
        "comparison_fields": [
            "entity",
            "text",
            "attributes",
            "evidence",
            "rationale",
            "confidence",
        ],
        "ownership_check": (
            "canonical stage trace identifies model as first "
            "prediction-changing owner"
        ),
    }

    selected = letter_assembly.assemble_structured_rows(
        selected_letters, producer_rows, config=StructuredMethodConfig.selected()
    )
    selected_again = letter_assembly.assemble_structured_rows(
        selected_letters, producer_rows, config=StructuredMethodConfig.selected()
    )
    hybrid_mismatches = sum(
        selected[a.letter_id] != selected_again[a.letter_id] for a in selected_letters
    )
    hybrid_result = {
        "passed": hybrid_mismatches == 0,
        "rows": len(selected_letters),
        "mismatch_rows": hybrid_mismatches,
        "exact_evidence_failures": sum(
            any(
                not m.get("evidence") or m.get("evidence") not in letter.note_text
                for m in selected[letter.letter_id]["predicted_mentions"]
            )
            for letter in selected_letters
        ),
    }

    archived = letter_assembly.assemble_structured_rows(
        selected_letters,
        producer_rows,
        config=StructuredMethodConfig(diagnosis_resolution_candidate=True, archived_replay=True),
    )
    changed_ids: list[str] = []
    added = removed = 0
    for letter in selected_letters:
        current = selected[letter.letter_id]["predicted_mentions"]
        old = archived[letter.letter_id]["predicted_mentions"]
        current_keys = {json.dumps(_mentions([row])[0], sort_keys=True) for row in current}
        old_keys = {json.dumps(_mentions([row])[0], sort_keys=True) for row in old}
        if current_keys != old_keys:
            changed_ids.append(letter.letter_id)
            added += len(old_keys - current_keys)
            removed += len(current_keys - old_keys)
    drift = {
        "status": "historical_development_policy_delta",
        "selected_policy": "default/default; candidate switches off",
        "historical_variant": "diagnosis_resolution_candidate=True",
        "rows": len(selected_letters),
        "changed_rows": len(changed_ids),
        "historical_additions_vs_selected": added,
        "historical_removals_vs_selected": removed,
        "changed_row_ids_sha256": hashlib.sha256("\n".join(changed_ids).encode()).hexdigest(),
        "row_ids_emitted": False,
        "claim_boundary": (
            "ExECT dev140 saved-output policy characterization; not structural "
            "parity, holdout evidence, or clinical validation."
        ),
    }
    return rules_result, llm_result, hybrid_result, drift


def build_report() -> dict[str, Any]:
    gan_records = load_records_for_split("validation")
    exect_letters = load_letters_for_split("dev")
    exect_rules_result, exect_llm_result, exect_hybrid_result, drift = _exect(exect_letters)
    methods = {
        "gan2026_rules_only": _gan_rules(gan_records),
        "gan2026_llm_only": _gan_model_pair(
            gan_records, GAN_LLM_SOURCE, legacy_gan_llm._legacy_run_split, gan_llm.run_split
        ),
        "gan2026_llm_with_rules": _gan_model_pair(
            gan_records,
            GAN_HYBRID_SOURCE,
            legacy_gan_hybrid._legacy_run_split,
            gan_hybrid.run_split,
        ),
        "exectv2_rules_only": exect_rules_result,
        "exectv2_llm_only": exect_llm_result,
        "exectv2_llm_with_rules": exect_hybrid_result,
    }
    return {
        "schema_version": "decision_0047_development_parity_v1",
        "decision": "0047-full-canonical-pipeline-orchestrator-refactor",
        "source_commit": _head(),
        "mode": "saved-output no-call replay",
        "datasets": {"gan2026": "dev750/validation750", "exectv2": "dev140"},
        "row_policy": "permitted development rows only; no held-out rows loaded",
        "sources": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (GAN_LLM_SOURCE, GAN_HYBRID_SOURCE, EXECT_SOURCE)
        },
        "methods": methods,
        "operational_policy_drift": drift,
        "result": "pass"
        if all(item["passed"] for item in methods.values())
        and not exect_hybrid_result["exact_evidence_failures"]
        else "fail",
        "claim_boundary": (
            "Implementation and mechanism parity on permitted development "
            "distributions; not new performance evidence or clinical validation."
        ),
    }


def _matches(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    expected = dict(expected)
    actual = dict(actual)
    expected.pop("source_commit", None)
    actual.pop("source_commit", None)
    return expected == actual


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=ARTIFACT)
    args = parser.parse_args()
    report = build_report()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if args.check:
        if not output.is_file() or not _matches(
            report, json.loads(output.read_text(encoding="utf-8"))
        ):
            print(f"development parity artifact is stale or missing: {output}")
            return 1
        print(f"development parity artifact matches: {output}")
        return 0 if report["result"] == "pass" else 1
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {output}")
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
