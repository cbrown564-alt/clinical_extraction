"""Archived no-call six-model ExECTv2 default-vs-joint policy replay.

Decision 0045 demotes joint (`combined`/`combined`) from active comparison use.
This script remains for historical reproduction only and requires
``--allow-archived-joint-policy``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
    build_finding_assembly,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import model_swap

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = (
    REPO_ROOT / "configs/exectv2/six_model_joint_policy_replay_20260731.json"
)
ARCHIVED_NOTICE = (
    "Archived by decision 0045: joint/combined is not the active ExECT "
    "comparison policy. Pass --allow-archived-joint-policy to reproduce the "
    "historical default-vs-joint panel."
)
FAMILIES = (
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY.name,
    PRESCRIPTION.name,
    INVESTIGATIONS.name,
)
SPLIT_SPECS = {
    "dev140": {"gold_split": "dev", "row_count": 140, "row_policy": "dev_rows_permitted"},
    "test60": {
        "gold_split": "test",
        "row_count": 59,
        "row_policy": "aggregate_only",
    },
}


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--split",
        choices=("dev140", "test60", "all"),
        default="all",
    )
    parser.add_argument(
        "--allow-archived-joint-policy",
        action="store_true",
        help="Required opt-in; joint/combined is archived (decision 0045).",
    )
    args = parser.parse_args(argv)
    if not args.allow_archived_joint_policy:
        raise SystemExit(ARCHIVED_NOTICE)
    config = _load_config(args.config)
    splits = ("dev140", "test60") if args.split == "all" else (args.split,)
    payload = run(config, splits=splits)
    out_root = REPO_ROOT / str(config["artifact_root"])
    out_root.mkdir(parents=True, exist_ok=True)
    panel_path = out_root / "panel_summary.json"
    panel_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    deltas_path = out_root / "dev140_deltas.json"
    if "dev140" in payload["splits"]:
        deltas_path.write_text(
            json.dumps(payload["splits"]["dev140"]["deltas"], indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
    print(
        json.dumps(
            {
                "status": payload["gates"]["status"],
                "panel_summary": panel_path.as_posix(),
                "splits": {
                    split: {
                        "models": len(payload["splits"][split]["models"]),
                        "default_gate_failures": payload["splits"][split][
                            "default_gate_failures"
                        ],
                    }
                    for split in payload["splits"]
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


def _load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    protocol = REPO_ROOT / str(config["protocol"])
    if not protocol.is_file():
        raise FileNotFoundError(protocol)
    if config.get("call_mode") != "saved_producers_no_call":
        raise ValueError("call_mode must be saved_producers_no_call")
    if int(config.get("new_model_calls", -1)) != 0:
        raise ValueError("new_model_calls must be 0")
    if len(config.get("models") or []) != 6:
        raise ValueError("config must declare exactly six models")
    return config


def run(
    config: Mapping[str, Any],
    *,
    splits: Sequence[str],
) -> dict[str, Any]:
    base = model_swap.load_model_swap_config(
        REPO_ROOT / str(config["base_assembly_config"])
    ).assembly
    started = datetime.now(UTC).isoformat()
    split_payloads: dict[str, Any] = {}
    gate_failures: list[str] = []
    for split in splits:
        split_result = _run_split(config, base=base, split=split)
        split_payloads[split] = split_result
        gate_failures.extend(split_result["default_gate_failures"])
    status = "pass" if not gate_failures else "fail"
    return {
        "schema_version": "exectv2.six_model_joint_policy_replay_panel.v1",
        "generated_on": config["generated_on"],
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "protocol": config["protocol"],
        "call_mode": "saved_producers_no_call",
        "new_model_calls": 0,
        "scorer": config["scorer"],
        "policies": config["policies"],
        "gates": {
            "status": status,
            "default_f1_tolerance": config["default_f1_tolerance"],
            "failures": gate_failures,
        },
        "splits": split_payloads,
        "claim_boundary": (
            "No-call ExECTv2 six-model Diagnosis/Prescription policy reassembly "
            "of saved producers under default versus joint bounded "
            "(combined/combined). test60 is aggregate-only. Not a prompt change, "
            "not clinical validation, and not automatic replacement of the "
            "historical default-panel hashes."
        ),
    }


def _run_split(
    config: Mapping[str, Any],
    *,
    base: Any,
    split: str,
) -> dict[str, Any]:
    spec = SPLIT_SPECS[split]
    gold = load_letters_for_split(spec["gold_split"])
    if len(gold) < int(spec["row_count"]):
        raise ValueError(
            f"{split}: expected at least {spec['row_count']} letters, found {len(gold)}"
        )
    gold = gold[: int(spec["row_count"])]
    models: list[dict[str, Any]] = []
    failures: list[str] = []
    for model in config["models"]:
        cell = _score_model(
            config,
            base=base,
            model=model,
            split=split,
            gold=gold,
            row_count=int(spec["row_count"]),
            row_policy=str(spec["row_policy"]),
        )
        models.append(cell)
        if not cell["default_gate"]["pass"]:
            failures.append(
                f"{split}/{model['slug']}: default F1 "
                f"{cell['default']['overall_f1']} vs expected "
                f"{cell['default_gate']['expected_overall_f1']}"
            )
    ranked_default = sorted(
        models, key=lambda item: (-item["default"]["overall_f1"], item["slug"])
    )
    ranked_joint = sorted(
        models, key=lambda item: (-item["joint"]["overall_f1"], item["slug"])
    )
    deltas = {
        item["slug"]: {
            "model_label": item["model_label"],
            "delta_overall_f1": item["delta_overall_f1"],
            "delta_family_f1": item["delta_family_f1"],
        }
        for item in models
    }
    return {
        "split": split,
        "row_count": int(spec["row_count"]),
        "row_policy": spec["row_policy"],
        "models": models,
        "rank_order_default": [item["slug"] for item in ranked_default],
        "rank_order_joint": [item["slug"] for item in ranked_joint],
        "rank_order_changed": [item["slug"] for item in ranked_default]
        != [item["slug"] for item in ranked_joint],
        "deltas": deltas,
        "default_gate_failures": failures,
    }


def _score_model(
    config: Mapping[str, Any],
    *,
    base: Any,
    model: Mapping[str, Any],
    split: str,
    gold: Sequence[Any],
    row_count: int,
    row_policy: str,
) -> dict[str, Any]:
    producer = model[split]
    structured = REPO_ROOT / str(producer["structured"])
    sf_final = REPO_ROOT / str(producer["sf_unknown_suppression"])
    if not structured.is_file():
        raise FileNotFoundError(structured)
    if not sf_final.is_file():
        raise FileNotFoundError(sf_final)
    assembly = _assembly_for(
        base,
        slug=str(model["slug"]),
        split=split,
        row_count=row_count,
        structured=structured,
        sf_final=sf_final,
    )
    scores: dict[str, dict[str, Any]] = {}
    for policy_name, policy in config["policies"].items():
        run = build_finding_assembly(
            assembly,
            generated_on=str(config["generated_on"]),
            gold_loader=lambda _split, letters=gold: list(letters),
            diagnosis_resolution_candidate=bool(
                model["diagnosis_resolution_candidate"]
            ),
            diagnosis_policy_variant=str(policy["diagnosis_policy_variant"]),
            prescription_policy_variant=str(policy["prescription_policy_variant"]),
        )
        headline = run.report["score_ladder"]["headline_target"]
        scores[policy_name] = {
            "overall_f1": float(headline["overall"]["f1"]),
            "family_f1": {
                family: float(headline["by_indicator"][family]["f1"])
                for family in FAMILIES
            },
            "diagnosis_policy_variant": policy["diagnosis_policy_variant"],
            "prescription_policy_variant": policy["prescription_policy_variant"],
        }
        if split == "test60":
            _write_test60_aggregate(
                config,
                model=model,
                policy_name=policy_name,
                scores=scores[policy_name],
                structured=structured,
                sf_final=sf_final,
            )
        elif split == "dev140" and policy_name == "joint":
            # Keep sealed test60 rows out of experiments; for development only
            # store aggregate scores (already in panel).
            pass

    expected = float(producer["expected_default_overall_f1"])
    tolerance = float(config["default_f1_tolerance"])
    observed = scores["default"]["overall_f1"]
    gate_pass = abs(observed - expected) <= tolerance
    delta_family = {
        family: round(
            scores["joint"]["family_f1"][family] - scores["default"]["family_f1"][family],
            4,
        )
        for family in FAMILIES
    }
    return {
        "slug": model["slug"],
        "model_label": model["model_label"],
        "model": model["model"],
        "row_policy": row_policy,
        "structured_sha256": _sha256(structured),
        "sf_unknown_suppression_sha256": _sha256(sf_final),
        "default": scores["default"],
        "joint": scores["joint"],
        "delta_overall_f1": round(
            scores["joint"]["overall_f1"] - scores["default"]["overall_f1"], 4
        ),
        "delta_family_f1": delta_family,
        "default_gate": {
            "expected_overall_f1": expected,
            "observed_overall_f1": observed,
            "tolerance": tolerance,
            "pass": gate_pass,
        },
        "producer_note": producer.get("producer_note"),
    }


def _assembly_for(
    base: Any,
    *,
    slug: str,
    split: str,
    row_count: int,
    structured: Path,
    sf_final: Path,
) -> Any:
    gold_split = "dev" if split == "dev140" else "test"
    producers = {
        "structured_key_family_event_ledger": replace(
            base.producers["structured_key_family_event_ledger"],
            artifact=structured,
        ),
        "sf_model_projection_suppression": replace(
            base.producers["sf_model_projection_suppression"],
            artifact=sf_final,
        ),
    }
    return replace(
        base,
        candidate_id=f"exectv2_six_model_joint_policy_replay_{slug}_{split}",
        split=gold_split,
        row_count=row_count,
        producers=producers,
        claim_boundary=(
            "No-call six-model joint-policy reassembly; not clinical validation."
        ),
    )


def _write_test60_aggregate(
    config: Mapping[str, Any],
    *,
    model: Mapping[str, Any],
    policy_name: str,
    scores: Mapping[str, Any],
    structured: Path,
    sf_final: Path,
) -> None:
    root = (
        REPO_ROOT
        / str(config["test60_scratch_root"])
        / str(model["slug"])
        / str(policy_name)
    )
    root.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "exectv2.six_model_joint_policy_replay_test60_aggregate.v1",
        "model": model["model"],
        "model_label": model["model_label"],
        "split": "test60",
        "row_policy": "aggregate_only",
        "row_count": 59,
        "policy": policy_name,
        "diagnosis_policy_variant": scores["diagnosis_policy_variant"],
        "prescription_policy_variant": scores["prescription_policy_variant"],
        "overall_f1": scores["overall_f1"],
        "family_f1": scores["family_f1"],
        "structured_sha256": _sha256(structured),
        "sf_unknown_suppression_sha256": _sha256(sf_final),
        "claim_boundary": (
            "Aggregate-only sealed test60 reassembly; no letter identifiers, "
            "notes, predictions, or failure cases."
        ),
    }
    (root / "aggregate.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
