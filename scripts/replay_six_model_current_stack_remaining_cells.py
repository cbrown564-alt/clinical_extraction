#!/usr/bin/env python3
"""No-call current-stack replay of the three remaining six-model hybrid cells.

See docs/research/shared/six_model_current_stack_remaining_cells_replay_protocol_2026-08-13.md.
Zero model calls. Gan test450 and ExECT test60 are aggregate-only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    aggregate_scores,
    annotation_from_mapping,
    clinical_headline_scores,
    headline_keys,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import hybrid_structured_events

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "experiments/six_model_current_stack_remaining_cells_replay_20260813"
SCRATCH_DIR = REPO_ROOT / "scratch/validation/six_model_current_stack_remaining_cells_20260813"
PROTOCOL = (
    "docs/research/shared/six_model_current_stack_remaining_cells_replay_protocol_2026-08-13.md"
)

MODELS = [
    ("gemini37flash", "gemini/gemini-3.7-flash", "Gemini 3.7 Flash", 0.0, 16_000),
    ("gpt56luna", "openai/gpt-5.6-luna", "GPT-5.6 Luna", 1.0, 10_000),
    ("gpt56sol", "openai/gpt-5.6-sol", "GPT-5.6 Sol", 0.0, 10_000),
    ("deepseek_v4_flash", "deepseek/deepseek-v4-flash", "DeepSeek V4 Flash", 0.0, 32_000),
    ("qwen36_35b", "ollama_chat/qwen3.6:35b", "Qwen 3.6:35B", 0.0, 16_000),
    ("gemma4_26b", "ollama_chat/gemma4:26b", "Gemma 4 26B", 0.0, 16_000),
]

def _inventory() -> dict[str, Any]:
    return json.loads(
        (REPO_ROOT / "experiments/current_stack/SOURCES.json").read_text(encoding="utf-8")
    )


def _cell_paths(cell_id: str, field: str) -> dict[str, Path]:
    return {
        slug: REPO_ROOT / spec[field]
        for slug, spec in _inventory()["cells"][cell_id]["sources"].items()
        if field in spec
    }


def _source_path(cell_id: str, slug: str, field: str) -> Path:
    return REPO_ROOT / _inventory()["cells"][cell_id]["sources"][slug][field]


def _model_source_map(cell_id: str, field: str) -> dict[str, Path]:
    """Paths for the six active roster slugs (mapping deepseek_v4_flash to 0731 holdouts)."""

    roster = {slug for slug, *_rest in MODELS}
    paths: dict[str, Path] = {}
    sources = _inventory()["cells"][cell_id]["sources"]
    for slug in roster:
        if cell_id in {"gan_test450", "exect_test60"} and slug == "deepseek_v4_flash" and "deepseek_v4_flash_0731" in sources:
            spec = sources["deepseek_v4_flash_0731"]
        elif slug in sources:
            spec = sources[slug]
        else:
            continue
        if field in spec:
            paths[slug] = REPO_ROOT / spec[field]
    return paths

GAN_STORED_BEFORE = {
    "gemini37flash": {"purist": 373, "pragmatic": 385, "parse_missing": 0},
    "gpt56luna": {"purist": 362, "pragmatic": 375, "parse_missing": 3},
    "gpt56sol": {"purist": 373, "pragmatic": 384, "parse_missing": 0},
    "deepseek_v4_flash": {"purist": 368, "pragmatic": 377, "parse_missing": 0},
    "qwen36_35b": {"purist": 362, "pragmatic": 384, "parse_missing": 2},
    "gemma4_26b": {"purist": 355, "pragmatic": 374, "parse_missing": 2},
}

GAN_FINAL_PANEL_TEST450 = {
    "gemini37flash": {"purist_accuracy": 0.8289, "pragmatic_accuracy": 0.8556},
    "gpt56luna": {"purist_accuracy": 0.8089, "pragmatic_accuracy": 0.84},
    "gpt56sol": {"purist_accuracy": 0.8467, "pragmatic_accuracy": 0.8711},
    "deepseek_v4_flash": {"purist_accuracy": 0.8178, "pragmatic_accuracy": 0.8378},
    "qwen36_35b": {"purist_accuracy": 0.8, "pragmatic_accuracy": 0.8444},
    "gemma4_26b": {"purist_accuracy": 0.7911, "pragmatic_accuracy": 0.8333},
}

EXECT_DEV140_PUBLISHED = {
    "gemini37flash": 0.9010,
    "gpt56luna": 0.8832,
    "gpt56sol": 0.8920,
    "deepseek_v4_flash": 0.8994,
    "qwen36_35b": 0.8571,
    "gemma4_26b": 0.8016,
}

EXECT_TEST60_PUBLISHED = {
    "gemini37flash": 0.8459,
    "gpt56luna": 0.7950,
    "gpt56sol": 0.8047,
    "deepseek_v4_flash": 0.8118,
    "qwen36_35b": 0.7872,
    "gemma4_26b": 0.7169,
}

GAN_DEEPSEEK_0731_STORED = {"purist": 368, "pragmatic": 377, "parse_missing": 0}
EXECT_DEEPSEEK_0731_PUBLISHED = 0.8118

FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")

_STAGE_PATH = REPO_ROOT / "scripts/build_exectv2_hybrid_stage_ablation.py"
_SPEC = importlib.util.spec_from_file_location("exect_hybrid_stage_ablation", _STAGE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Cannot import replay helpers from {_STAGE_PATH}")
stage = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(stage)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_note() -> dict[str, Any]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty_tree": None}
    return {"commit": commit, "dirty_tree": dirty}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _correct(row: dict[str, Any], key: str) -> bool:
    comparison = row.get("comparison")
    return bool(comparison and comparison.get(key))


def _parse_missing(row: dict[str, Any]) -> bool:
    return row.get("comparison") is None


def _score_gan_rows(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "rows": len(rows),
        "purist": sum(_correct(row, "purist_correct") for row in rows),
        "pragmatic": sum(_correct(row, "pragmatic_correct") for row in rows),
        "parse_missing": sum(_parse_missing(row) for row in rows),
    }


def _gan_transitions(
    before: list[dict[str, Any]], after: list[dict[str, Any]]
) -> dict[str, int]:
    before_by_id = {int(row["source_row_index"]): row for row in before}
    after_by_id = {int(row["source_row_index"]): row for row in after}
    if before_by_id.keys() != after_by_id.keys():
        raise ValueError("Gan replay source IDs differ from the original artifact")
    counts = {
        "purist_wrong_to_correct": 0,
        "purist_correct_to_wrong": 0,
        "pragmatic_wrong_to_correct": 0,
        "pragmatic_correct_to_wrong": 0,
        "parse_missing_rescued": 0,
    }
    for source_id, old in before_by_id.items():
        new = after_by_id[source_id]
        old_p = _correct(old, "purist_correct")
        new_p = _correct(new, "purist_correct")
        old_g = _correct(old, "pragmatic_correct")
        new_g = _correct(new, "pragmatic_correct")
        counts["purist_wrong_to_correct"] += int(not old_p and new_p)
        counts["purist_correct_to_wrong"] += int(old_p and not new_p)
        counts["pragmatic_wrong_to_correct"] += int(not old_g and new_g)
        counts["pragmatic_correct_to_wrong"] += int(old_g and not new_g)
        counts["parse_missing_rescued"] += int(_parse_missing(old) and not _parse_missing(new))
    return counts


def _round_family(scores: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for family, score in scores.items():
        out[family] = {
            **score,
            "f1": round(float(score["f1"]), 4),
            "precision": round(float(score["precision"]), 4),
            "recall": round(float(score["recall"]), 4),
        }
    return out


def _gold_mentions(letter: ExectLetter) -> list[dict[str, Any]]:
    return [
        {
            "entity": annotation.entity,
            "text": annotation.text,
            "attributes": dict(annotation.attributes),
        }
        for annotation in letter.annotations
        if annotation.entity in FAMILIES
    ]


def _pred_letter(letter_id: str, mentions: list[dict[str, Any]]) -> ExectLetter:
    return ExectLetter(
        letter_id=letter_id,
        note_text="",
        annotations=tuple(
            annotation_from_mapping(mention)
            for mention in mentions
            if mention.get("entity") in FAMILIES
        ),
    )


def _all_family_exact(gold: list[dict[str, Any]], pred: list[dict[str, Any]]) -> bool:
    payload = {"gold_mentions": gold, "predicted_mentions": pred}
    for family in FAMILIES:
        gold_keys = headline_keys(payload, family, field="gold_mentions")
        pred_keys = headline_keys(payload, family, field="predicted_mentions")
        if sorted(gold_keys) != sorted(pred_keys):
            return False
    return True


def replay_gan_test450(*, overwrite: bool) -> dict[str, Any]:
    records = load_records_for_split("test")
    expected = {int(record.source_row_index) for record in records}
    if len(expected) != 450:
        raise ValueError(f"Gan test split is {len(expected)} rows, expected 450")
    manifest = load_split_manifest()
    cells: dict[str, Any] = {}
    for slug, model, display, temperature, max_tokens in MODELS:
        source = _model_source_map("gan_test450", "path")[slug]
        if not source.is_file():
            raise FileNotFoundError(source)
        print(f"replaying Gan test450 {slug} from {source.relative_to(REPO_ROOT)}", flush=True)
        source_rows = load_jsonl_rows(source)
        source_ids = [int(row["source_row_index"]) for row in source_rows]
        if len(source_rows) != 450 or set(source_ids) != expected:
            raise ValueError(f"{slug} is not a complete unique test450 artifact")
        versions = {row.get("prompt_version") for row in source_rows}
        if versions != {hybrid_structured_events.PROMPT_VERSION_V0_5}:
            raise ValueError(f"{slug} prompt versions {versions} != v0.5")
        raw_outputs = {
            int(row["source_row_index"]): str(row.get("raw_output") or "")
            for row in source_rows
        }
        if any(not value.strip() for value in raw_outputs.values()):
            raise ValueError(f"{slug} has empty raw outputs")

        scratch = SCRATCH_DIR / "gan_test450" / slug
        rows_path = scratch / "test450.rows.jsonl"
        if rows_path.exists() and not overwrite:
            replay_rows = load_jsonl_rows(rows_path)
            reused = True
        else:
            hybrid_structured_events.set_active_prompt_version(
                hybrid_structured_events.PROMPT_VERSION_V0_5
            )
            replay_rows, _metadata = hybrid_structured_events.run_split(
                records,
                split="test",
                split_manifest=str(manifest.get("manifest_version", "gan2026_split_v1")),
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                mode="prompt-only",
                dspy_cache=False,
                escalation_reason=(
                    "Predeclared 2026-08-13 six-model current-stack no-call replay"
                ),
                reuse_raw_outputs=raw_outputs,
                reuse_source=str(source.relative_to(REPO_ROOT).as_posix()),
                repair_config=hybrid_structured_events.StructuredRepairConfig.for_mode(
                    "hybrid_full_stack"
                ),
                progress_every=150,
            )
            scratch.mkdir(parents=True, exist_ok=True)
            hybrid_structured_events.write_jsonl(replay_rows, rows_path)
            reused = False

        before = _score_gan_rows(source_rows)
        after = _score_gan_rows(replay_rows)
        declared = GAN_STORED_BEFORE[slug]
        if (
            before["purist"] != declared["purist"]
            or before["pragmatic"] != declared["pragmatic"]
            or before["parse_missing"] != declared["parse_missing"]
        ):
            raise ValueError(
                f"{slug} stored scores {before} != protocol declaration {declared}"
            )
        transitions = _gan_transitions(source_rows, replay_rows)
        cells[slug] = {
            "slug": slug,
            "model": model,
            "label": display,
            "prompt_version": hybrid_structured_events.PROMPT_VERSION_V0_5,
            "source_artifact": source.relative_to(REPO_ROOT).as_posix(),
            "source_sha256": _sha256(source),
            "reused_scratch": reused,
            "before": before,
            "after": after,
            "delta_purist": after["purist"] - before["purist"],
            "delta_pragmatic": after["pragmatic"] - before["pragmatic"],
            "transitions": transitions,
            "historical_not_same_raw": {
                "final_panel_20260803": GAN_FINAL_PANEL_TEST450[slug],
                "cluster_v2_pooled_purist": 0.8074,
            },
        }
        print(
            f"  {slug}: {before['purist']} -> {after['purist']} Purist "
            f"({after['purist'] - before['purist']:+d})",
            flush=True,
        )

    pooled_before_p = sum(cell["before"]["purist"] for cell in cells.values())
    pooled_after_p = sum(cell["after"]["purist"] for cell in cells.values())
    pooled_before_g = sum(cell["before"]["pragmatic"] for cell in cells.values())
    pooled_after_g = sum(cell["after"]["pragmatic"] for cell in cells.values())
    return {
        "split": "test450",
        "split_machine": "test",
        "row_policy": "aggregate_only",
        "prompt_version": hybrid_structured_events.PROMPT_VERSION_V0_5,
        "repair_mode": "hybrid_full_stack",
        "models": cells,
        "pooled": {
            "rows": 2700,
            "before_purist": pooled_before_p,
            "after_purist": pooled_after_p,
            "delta_purist": pooled_after_p - pooled_before_p,
            "before_pragmatic": pooled_before_g,
            "after_pragmatic": pooled_after_g,
            "delta_pragmatic": pooled_after_g - pooled_before_g,
            "before_parse_missing": sum(
                cell["before"]["parse_missing"] for cell in cells.values()
            ),
            "after_parse_missing": sum(
                cell["after"]["parse_missing"] for cell in cells.values()
            ),
            "purist_wrong_to_correct": sum(
                cell["transitions"]["purist_wrong_to_correct"] for cell in cells.values()
            ),
            "purist_correct_to_wrong": sum(
                cell["transitions"]["purist_correct_to_wrong"] for cell in cells.values()
            ),
            "pragmatic_wrong_to_correct": sum(
                cell["transitions"]["pragmatic_wrong_to_correct"] for cell in cells.values()
            ),
            "pragmatic_correct_to_wrong": sum(
                cell["transitions"]["pragmatic_correct_to_wrong"] for cell in cells.values()
            ),
        },
    }


def _replay_exect_cell(
    *,
    split_name: str,
    machine_split: str,
    expected_n: int,
    structured_paths: dict[str, Path],
    assembly_paths: dict[str, Path] | None,
    published: dict[str, float],
    record_letter_transitions: bool,
    models_override: tuple[tuple[str, str, str, float, int], ...] | None = None,
) -> dict[str, Any]:
    letters = {letter.letter_id: letter for letter in load_letters_for_split(machine_split)}
    if len(letters) != expected_n:
        raise ValueError(
            f"ExECT {split_name} loaded {len(letters)} letters, expected {expected_n}"
        )
    cells: dict[str, Any] = {}
    model_iter = models_override if models_override is not None else MODELS
    for slug, model, display, _temperature, _max_tokens in model_iter:
        structured_path = structured_paths[slug]
        if not structured_path.is_file():
            raise FileNotFoundError(structured_path)
        print(
            f"replaying ExECT {split_name} {slug} from "
            f"{structured_path.relative_to(REPO_ROOT)}",
            flush=True,
        )
        structured_rows = _read_jsonl(structured_path)
        if len(structured_rows) != expected_n:
            raise ValueError(
                f"{slug} {split_name} has {len(structured_rows)} rows, expected {expected_n}"
            )
        saved_rows = {}
        if assembly_paths is not None:
            saved_rows = {
                str(row["letter_id"]): row for row in _read_jsonl(assembly_paths[slug])
            }

        gold_letters: list[ExectLetter] = []
        pred_letters: list[ExectLetter] = []
        empty_events = 0
        unreplayable = 0
        rescue = harm = unchanged = 0
        letter_transitions: list[dict[str, Any]] = []

        for structured_row in structured_rows:
            letter_id = str(structured_row["letter_id"])
            letter = letters.get(letter_id)
            if letter is None:
                raise ValueError(f"{slug} {split_name} letter not in split loader")
            gold = _gold_mentions(letter)
            events = structured_row.get("structured_events") or []
            if not events:
                empty_events += 1
                mentions: list[dict[str, Any]] = []
                replayable = False
            else:
                replay = stage.replay_letter(structured_row, letter, gold_mentions=gold)
                replayable = bool(replay.get("replayable"))
                mentions = list(replay.get("final_mentions") or []) if replayable else []
                if not replayable:
                    unreplayable += 1
            gold_letters.append(letter)
            pred_letters.append(_pred_letter(letter_id, mentions))

            if record_letter_transitions and saved_rows:
                saved = saved_rows.get(letter_id) or {}
                saved_pred = list(saved.get("predicted_mentions") or [])
                before_exact = _all_family_exact(gold, saved_pred)
                after_exact = _all_family_exact(gold, mentions)
                if before_exact and after_exact:
                    unchanged += 1
                    effect = "unchanged_correct"
                elif (not before_exact) and after_exact:
                    rescue += 1
                    effect = "rescue"
                elif before_exact and (not after_exact):
                    harm += 1
                    effect = "harm"
                else:
                    unchanged += 1
                    effect = "unchanged_wrong"
                letter_transitions.append(
                    {
                        "letter_id": letter_id,
                        "effect": effect,
                    }
                )

        family_scores = _round_family(clinical_headline_scores(gold_letters, pred_letters))
        overall = aggregate_scores(family_scores.values())
        payload: dict[str, Any] = {
            "slug": slug,
            "model": model,
            "label": display,
            "source_artifact": structured_path.relative_to(REPO_ROOT).as_posix(),
            "source_sha256": _sha256(structured_path),
            "prompt_version": "exectv2_hybrid_key_family_event_ledger_v0.9.24",
            "letters": expected_n,
            "empty_structured_events": empty_events,
            "unreplayable": unreplayable,
            "published_hybrid_f1": published[slug],
            "after_four_family_f1": overall["f1"],
            "after_four_family": overall,
            "after_by_family": {family: family_scores[family] for family in FAMILIES},
            "delta_f1_vs_published": round(overall["f1"] - published[slug], 4),
        }
        if record_letter_transitions:
            payload["transitions"] = {
                "all_family_key_exact_rescue": rescue,
                "all_family_key_exact_harm": harm,
                "all_family_key_exact_unchanged": unchanged,
            }
            changed_path = SCRATCH_DIR / f"exect_dev140_{slug}_changed_letters.jsonl"
            changed_path.parent.mkdir(parents=True, exist_ok=True)
            changed_path.write_text(
                "".join(
                    json.dumps(item, ensure_ascii=False) + "\n"
                    for item in letter_transitions
                    if item["effect"] in {"rescue", "harm"}
                ),
                encoding="utf-8",
            )
            payload["changed_letters_path"] = changed_path.relative_to(REPO_ROOT).as_posix()
        cells[slug] = payload
        print(
            f"  {slug}: published {published[slug]:.4f} -> {overall['f1']:.4f} "
            f"({overall['f1'] - published[slug]:+.4f})",
            flush=True,
        )

    return {
        "split": split_name,
        "split_machine": machine_split,
        "row_policy": "development_review_permitted"
        if record_letter_transitions
        else "aggregate_only",
        "assembly": "StructuredMethodConfig.selected default/default",
        "models": cells,
    }


def replay_deepseek_0731(*, overwrite: bool) -> dict[str, Any]:
    """Current-stack no-call replay of the selected DeepSeek 0731 holdout raws."""

    slug = "deepseek_v4_flash"
    model = "deepseek/deepseek-v4-flash"
    display = "DeepSeek V4 Flash"
    source = _source_path("gan_test450", "deepseek_v4_flash_0731", "path")
    if not source.is_file():
        raise FileNotFoundError(source)
    print(f"replaying Gan test450 DeepSeek 0731 from {source.relative_to(REPO_ROOT)}", flush=True)
    records = load_records_for_split("test")
    expected = {int(record.source_row_index) for record in records}
    source_rows = load_jsonl_rows(source)
    source_ids = [int(row["source_row_index"]) for row in source_rows]
    if len(source_rows) != 450 or set(source_ids) != expected:
        raise ValueError("DeepSeek 0731 is not a complete unique test450 artifact")
    versions = {row.get("prompt_version") for row in source_rows}
    if versions != {hybrid_structured_events.PROMPT_VERSION_V0_5}:
        raise ValueError(f"DeepSeek 0731 prompt versions {versions} != v0.5")
    raw_outputs = {
        int(row["source_row_index"]): str(row.get("raw_output") or "") for row in source_rows
    }
    if any(not value.strip() for value in raw_outputs.values()):
        raise ValueError("DeepSeek 0731 has empty raw outputs")

    scratch = SCRATCH_DIR / "gan_test450_deepseek_0731"
    rows_path = scratch / "test450.rows.jsonl"
    if rows_path.exists() and not overwrite:
        replay_rows = load_jsonl_rows(rows_path)
        reused = True
    else:
        hybrid_structured_events.set_active_prompt_version(
            hybrid_structured_events.PROMPT_VERSION_V0_5
        )
        manifest = load_split_manifest()
        replay_rows, _metadata = hybrid_structured_events.run_split(
            records,
            split="test",
            split_manifest=str(manifest.get("manifest_version", "gan2026_split_v1")),
            model=model,
            temperature=0.0,
            max_tokens=32_000,
            mode="prompt-only",
            dspy_cache=False,
            escalation_reason=(
                "Predeclared 2026-08-13 DeepSeek 0731 current-stack no-call replay"
            ),
            reuse_raw_outputs=raw_outputs,
            reuse_source=str(source.relative_to(REPO_ROOT).as_posix()),
            repair_config=hybrid_structured_events.StructuredRepairConfig.for_mode(
                "hybrid_full_stack"
            ),
            progress_every=150,
        )
        scratch.mkdir(parents=True, exist_ok=True)
        hybrid_structured_events.write_jsonl(replay_rows, rows_path)
        reused = False

    before = _score_gan_rows(source_rows)
    after = _score_gan_rows(replay_rows)
    declared = GAN_DEEPSEEK_0731_STORED
    if (
        before["purist"] != declared["purist"]
        or before["pragmatic"] != declared["pragmatic"]
        or before["parse_missing"] != declared["parse_missing"]
    ):
        raise ValueError(f"DeepSeek 0731 stored scores {before} != {declared}")
    transitions = _gan_transitions(source_rows, replay_rows)
    gan_cell = {
        "slug": slug,
        "model": model,
        "label": display,
        "provider_revision": "DeepSeek-V4-Flash-0731",
        "prompt_version": hybrid_structured_events.PROMPT_VERSION_V0_5,
        "source_artifact": source.relative_to(REPO_ROOT).as_posix(),
        "source_sha256": _sha256(source),
        "reused_scratch": reused,
        "before": before,
        "after": after,
        "delta_purist": after["purist"] - before["purist"],
        "delta_pragmatic": after["pragmatic"] - before["pragmatic"],
        "transitions": transitions,
    }
    print(
        f"  gan0731: {before['purist']} -> {after['purist']} Purist "
        f"({after['purist'] - before['purist']:+d})",
        flush=True,
    )

    exect = _replay_exect_cell(
        split_name="test60_deepseek_0731",
        machine_split="test",
        expected_n=59,
        structured_paths={
            slug: _source_path("exect_test60", "deepseek_v4_flash_0731", "structured")
        },
        assembly_paths=None,
        published={slug: EXECT_DEEPSEEK_0731_PUBLISHED},
        record_letter_transitions=False,
        models_override=(
            ("deepseek_v4_flash", "deepseek/deepseek-v4-flash", "DeepSeek V4 Flash", 0.0, 32_000),
        ),
    )
    return {"gan2026_test450": gan_cell, "exectv2_test60": exect["models"][slug]}


def main() -> None:
    global OUT_DIR, SCRATCH_DIR
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cell",
        choices=("gan_test450", "exect_dev140", "exect_test60", "all"),
        default="all",
    )
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--scratch-dir", type=Path, default=None)
    args = parser.parse_args()
    if args.out_dir is not None:
        OUT_DIR = args.out_dir
    if args.scratch_dir is not None:
        SCRATCH_DIR = args.scratch_dir
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    missing = []
    wanted_paths: list[Path] = []
    if args.cell in {"gan_test450", "all"}:
        wanted_paths.extend(_cell_paths("gan_test450", "path").values())
    if args.cell in {"exect_dev140", "all"}:
        wanted_paths.extend(_cell_paths("exect_dev140", "structured").values())
        wanted_paths.extend(_cell_paths("exect_dev140", "assembly").values())
    if args.cell in {"exect_test60", "all"}:
        wanted_paths.extend(_cell_paths("exect_test60", "structured").values())
    for path in wanted_paths:
        if not path.is_file():
            missing.append(path.as_posix())
    if missing:
        raise SystemExit("missing source files:\n" + "\n".join(missing))

    summary_path = OUT_DIR / "replay_summary.json"
    if summary_path.exists() and not args.overwrite and args.cell != "all":
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    else:
        summary = {
            "schema_version": "six_model.current_stack_remaining_cells_replay.v1",
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "protocol": PROTOCOL,
            "git": _git_note(),
            "method": "llm_with_rules",
            "call_mode": "saved_raw_or_structured_no_call",
            "claim_boundary": (
                "No-call current-repair readout. Gan test450 uses v0.5 saved raw. "
                "ExECT uses v0.9.24 structured sidecars through HEAD default/default. "
                "Holdout cells are aggregate-only. Does not rewrite Decision 0046/0047 "
                "or C16 holdout fills."
            ),
        }

    if args.cell in {"gan_test450", "all"}:
        summary["gan2026_test450"] = replay_gan_test450(overwrite=args.overwrite)
    if args.cell in {"exect_dev140", "all"}:
        summary["exectv2_dev140"] = _replay_exect_cell(
            split_name="dev140",
            machine_split="dev",
            expected_n=140,
            structured_paths=_model_source_map("exect_dev140", "structured"),
            assembly_paths=_model_source_map("exect_dev140", "assembly"),
            published=EXECT_DEV140_PUBLISHED,
            record_letter_transitions=True,
        )
    if args.cell in {"exect_test60", "all"}:
        summary["exectv2_test60"] = _replay_exect_cell(
            split_name="test60",
            machine_split="test",
            expected_n=59,
            structured_paths=_model_source_map("exect_test60", "structured"),
            assembly_paths=None,
            published=EXECT_TEST60_PUBLISHED,
            record_letter_transitions=False,
        )

    summary["generated_at_utc"] = datetime.now(UTC).isoformat()
    summary["git"] = _git_note()
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"wrote {summary_path.relative_to(REPO_ROOT)}", flush=True)


if __name__ == "__main__":
    main()
