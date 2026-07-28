"""Build a deterministic ExECTv2 semantic-support sample for independent review."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_STUDY = Path("experiments/exectv2_six_model_sf_overinference_dev140_20260718.json")
OUTPUT = Path("experiments/exectv2_semantic_support_review_substrate_dev140_20260718.json")
PROTOCOL = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_semantic_support_review_substrate_protocol_2026-07-18.md"
)
FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")
SAMPLE_PER_MODEL_FAMILY = 2
TEXT_SUFFIXES = frozenset({".json", ".jsonl", ".md", ".py", ".txt", ".yaml", ".yml"})


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _sha256(path: Path) -> str:
    content = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        content = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest()


def _stable_rank(*parts: str) -> str:
    return hashlib.sha256("\x1f".join(parts).encode()).hexdigest()


def _candidate_items(
    *,
    rows: list[dict[str, Any]],
    model: Mapping[str, Any],
    family: str,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    source_artifact = str(model["final_rows_artifact"])
    source_sha256 = str(model["final_rows_sha256"])
    runtime_model = str(model["runtime_model"])

    for row in rows:
        letter_id = str(row["letter_id"])
        for mention in row.get("predicted_mentions", []):
            if mention.get("entity") != family:
                continue
            evidence = str(mention.get("evidence", "")).strip()
            if mention.get("evidence_valid") is not True or not evidence:
                continue
            finding_id = str(mention.get("finding_id", ""))
            rank = _stable_rank(runtime_model, family, letter_id, finding_id)
            candidates.append(
                {
                    "rank": rank,
                    "letter_id": letter_id,
                    "finding_id": finding_id,
                    "mention": mention,
                    "source_artifact": source_artifact,
                    "source_sha256": source_sha256,
                }
            )
    return sorted(candidates, key=lambda item: (item["rank"], item["finding_id"]))


def _select_distinct_letters(
    candidates: list[dict[str, Any]], *, count: int
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen_letters: set[str] = set()
    for candidate in candidates:
        letter_id = str(candidate["letter_id"])
        if letter_id in seen_letters:
            continue
        selected.append(candidate)
        seen_letters.add(letter_id)
        if len(selected) == count:
            return selected
    raise ValueError(f"could not select {count} evidence-bearing findings from distinct letters")


def build_review_substrate(repo_root: Path = ROOT) -> dict[str, Any]:
    """Return the unreviewed, hash-ranked six-model by four-family sample."""

    source_study_path = repo_root / SOURCE_STUDY
    study = _read_json(source_study_path)
    review_items: list[dict[str, Any]] = []
    source_hashes = {SOURCE_STUDY.as_posix(): _sha256(source_study_path)}

    for model in study["models"]:
        source_path = repo_root / str(model["final_rows_artifact"])
        actual_sha256 = _sha256(source_path)
        expected_sha256 = str(model["final_rows_sha256"])
        if actual_sha256 != expected_sha256:
            raise ValueError(f"source hash drift: {source_path.relative_to(repo_root)}")
        source_hashes[source_path.relative_to(repo_root).as_posix()] = actual_sha256

        rows = _read_jsonl(source_path)
        if len(rows) != 140 or {row.get("split") for row in rows} != {"dev140"}:
            raise ValueError(f"review source is not exactly dev140: {source_path}")

        for family in FAMILIES:
            candidates = _candidate_items(rows=rows, model=model, family=family)
            selected = _select_distinct_letters(
                candidates,
                count=SAMPLE_PER_MODEL_FAMILY,
            )
            for candidate in selected:
                mention = candidate["mention"]
                review_item_id = (
                    f"{model['runtime_model']}|{family}|{candidate['letter_id']}|"
                    f"{candidate['finding_id']}"
                )
                review_items.append(
                    {
                        "review_item_id": review_item_id,
                        "model": model["model"],
                        "runtime_model": model["runtime_model"],
                        "runtime": model["runtime"],
                        "family": family,
                        "letter_id": candidate["letter_id"],
                        "finding_id": candidate["finding_id"],
                        "score_stage": "final",
                        "selected_conclusion": {
                            "text": mention.get("text"),
                            "normalized_concept": mention.get("normalized_concept"),
                            "assertion": mention.get("assertion"),
                            "attributes": mention.get("attributes", {}),
                        },
                        "evidence_text": mention["evidence"],
                        "evidence_valid": True,
                        "rationale": mention.get("rationale"),
                        "component_owner": mention.get("component_owner"),
                        "fact_origin": mention.get("fact_origin"),
                        "source_artifact": candidate["source_artifact"],
                        "source_sha256": candidate["source_sha256"],
                        "semantic_support": None,
                        "evidence_decisive": None,
                        "current_fact_warranted": None,
                        "unsupported_inference": None,
                        "reviewer_id": None,
                        "reviewed_at": None,
                        "review_notes": None,
                    }
                )

    payload: dict[str, Any] = {
        "schema_version": "exectv2-semantic-support-review-v1",
        "generated_date": "2026-07-18",
        "dataset": "ExECTv2 2025 broad epilepsy phenotyping corpus",
        "split": "dev140",
        "split_manifest": "data/ExECTv2 (2025)/splits/exectv2_split_v1.json",
        "row_scope": "development_rows_permitted",
        "row_inspection_policy": "dev140 rows permitted; no test60 source is used",
        "review_status": "pending_independent_clinical_review",
        "independent_clinical_review": "not_started",
        "review_question": (
            "Does the cited evidence sufficiently and decisively support the final "
            "clinical conclusion, including its temporal and assertion status?"
        ),
        "selection": {
            "method": "sha256_rank_without_outcome_or_review_labels",
            "strata": ["runtime_model", "family"],
            "sample_per_model_family": SAMPLE_PER_MODEL_FAMILY,
            "distinct_letters_within_stratum": True,
            "eligible_findings": "final evidence-valid findings with non-empty evidence",
            "outcome_labels_used_for_selection": False,
        },
        "models": [model["runtime_model"] for model in study["models"]],
        "families": list(FAMILIES),
        "source_study": SOURCE_STUDY.as_posix(),
        "source_hashes": dict(sorted(source_hashes.items())),
        "review_items": sorted(review_items, key=lambda item: item["review_item_id"]),
        "claim_boundary": (
            "Unreviewed development sampling substrate only. It is not semantic-support "
            "evidence, independent clinical validation, or a six-model comparative result."
        ),
    }
    validate_review_substrate(payload, repo_root=repo_root)
    return payload


def validate_review_substrate(substrate: Mapping[str, Any], *, repo_root: Path = ROOT) -> None:
    """Reject split leakage, source drift, incomplete strata, or self-certification."""

    if substrate.get("split") != "dev140":
        raise ValueError("semantic review substrate must use dev140 only")
    if substrate.get("review_status") != "pending_independent_clinical_review":
        raise ValueError("semantic review substrate cannot self-certify review")

    items = list(substrate.get("review_items", []))
    expected_count = 6 * len(FAMILIES) * SAMPLE_PER_MODEL_FAMILY
    if len(items) != expected_count:
        raise ValueError(f"semantic review substrate must contain {expected_count} items")

    counts = Counter((item["runtime_model"], item["family"]) for item in items)
    if set(counts.values()) != {SAMPLE_PER_MODEL_FAMILY} or len(counts) != 24:
        raise ValueError("semantic review strata are incomplete")
    if len({item["review_item_id"] for item in items}) != len(items):
        raise ValueError("semantic review item identifiers must be unique")

    for item in items:
        if item["family"] not in FAMILIES:
            raise ValueError("semantic review item has an unknown family")
        if item["evidence_valid"] is not True:
            raise ValueError("semantic review items require exact evidence presence")
        if "test60" in str(item["source_artifact"]).lower():
            raise ValueError("semantic review substrate cannot use test60 rows")
        if any(
            item[field] is not None
            for field in (
                "semantic_support",
                "evidence_decisive",
                "current_fact_warranted",
                "unsupported_inference",
                "reviewer_id",
                "reviewed_at",
            )
        ):
            raise ValueError("unreviewed substrate contains a review conclusion")

    for relative_path, expected_sha256 in substrate.get("source_hashes", {}).items():
        source_path = repo_root / relative_path
        if not source_path.is_file() or _sha256(source_path) != expected_sha256:
            raise ValueError(f"semantic review source hash drift: {relative_path}")


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    payload = build_review_substrate(ROOT)
    rendered = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"semantic review substrate is stale: {output}")
        print(f"semantic review substrate valid: {output.relative_to(ROOT)}")
        return 0

    _write_json(output, payload)
    print(f"wrote {output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
