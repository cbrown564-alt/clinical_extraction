"""Living paper comparison envelope. Adapter for historical files."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

ReplayMode = Literal["live", "no_call"]
PaperCell = Literal[1, 2, 3, 4, 5, "ablation"]

LIVING_SCHEMA_VERSION = "paper.living_cell.v1"
HEADLINE_STAGE = "select"
GAN_SCORER = "purist"
EXECT_SCORER = "clinical_inventory_unit_keys"
FORBIDDEN_LIVING_PRIMARY = frozenset(
    {"hybrid_headline_f1", "four_family_headline_f1", "raw_headline_f1"}
)

CELL_FOR_METHOD: dict[str, PaperCell] = {
    "gan_rules": 1,
    "exect_rules": 1,
    "gan_llm_and_rules_extract": 2,
    "exect_llm_pre_post": 2,
    "gan_llm_extract": 3,
    "exect_llm_extract": 3,
    "gan_llm_encode": 4,
    "exect_llm_encode": 4,
    "exect_rule_select_after_llm_encode": 4,
    "gan_llm_select": 5,
    "gan_llm_select_from_extract": 5,
    "exect_llm_select": 5,
    "gan_llm_only": "ablation",
    "gan_llm_extract_raw": "ablation",
    "exect_llm_extract_and_select": "ablation",
    "exect_llm_extract_filtered": "ablation",
}

TASK_FOR_METHOD: dict[str, str] = {
    "gan_rules": "gan2026",
    "gan_llm_and_rules_extract": "gan2026",
    "gan_llm_extract": "gan2026",
    "gan_llm_encode": "gan2026",
    "gan_llm_select": "gan2026",
    "gan_llm_select_from_extract": "gan2026",
    "gan_llm_only": "gan2026",
    "gan_llm_extract_raw": "gan2026",
    "exect_rules": "exectv2",
    "exect_llm_pre_post": "exectv2",
    "exect_llm_extract": "exectv2",
    "exect_llm_encode": "exectv2",
    "exect_rule_select_after_llm_encode": "exectv2",
    "exect_llm_select": "exectv2",
    "exect_llm_extract_and_select": "exectv2",
    "exect_llm_extract_filtered": "exectv2",
}

REQUIRED_IDENTITY = (
    "task",
    "method",
    "cell",
    "model_slug",
    "split",
    "row_policy",
    "scorer",
    "prompt_version",
    "replay_mode",
    "headline",
)
REQUIRED_STAGES = ("extract", "encode", "select")


def scorer_for_task(task: str) -> str:
    """Return the cited living scorer for one paper task."""

    if task == "gan2026":
        return GAN_SCORER
    if task == "exectv2":
        return EXECT_SCORER
    raise ValueError(f"unsupported paper task {task!r}")


def gan_stage(
    *,
    purist_correct: int,
    n: int,
    pragmatic_correct: int | None = None,
) -> dict[str, Any]:
    """One Gan stage stop in living field names."""

    accuracy = round(purist_correct / n, 4) if n else 0.0
    payload: dict[str, Any] = {
        "purist_correct": purist_correct,
        "n": n,
        "purist_accuracy": accuracy,
    }
    if pragmatic_correct is not None:
        payload["pragmatic_correct"] = pragmatic_correct
        payload["pragmatic_accuracy"] = round(pragmatic_correct / n, 4) if n else 0.0
    return payload


def living_exect_stages_from_surfaces(
    summary: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    """Map a live ExECT arm summary onto extract / encode / select stops."""

    raw_prf = summary.get("raw_headline_prf")
    hybrid_prf = summary.get("hybrid_headline_prf")
    extract = exect_stage(
        four_family_micro_f1=float(summary.get("raw_headline_f1") or 0.0),
        family_f1=summary.get("raw_family_f1")
        if isinstance(summary.get("raw_family_f1"), Mapping)
        else None,
        precision=raw_prf.get("precision") if isinstance(raw_prf, Mapping) else None,
        recall=raw_prf.get("recall") if isinstance(raw_prf, Mapping) else None,
    )
    select = exect_stage(
        four_family_micro_f1=float(summary.get("hybrid_headline_f1") or 0.0),
        family_f1=summary.get("hybrid_family_f1")
        if isinstance(summary.get("hybrid_family_f1"), Mapping)
        else None,
        precision=hybrid_prf.get("precision") if isinstance(hybrid_prf, Mapping) else None,
        recall=hybrid_prf.get("recall") if isinstance(hybrid_prf, Mapping) else None,
    )
    encode_f1 = summary.get("encode_headline_f1")
    encode = (
        exect_stage(four_family_micro_f1=float(encode_f1))
        if encode_f1 is not None
        else dict(extract)
    )
    return {"extract": extract, "encode": encode, "select": select}


def exect_stage(
    *,
    four_family_micro_f1: float,
    family_f1: Mapping[str, float] | None = None,
    precision: float | None = None,
    recall: float | None = None,
) -> dict[str, Any]:
    """One ExECT stage stop in living field names."""

    payload: dict[str, Any] = {"four_family_micro_f1": four_family_micro_f1}
    if family_f1 is not None:
        payload["family_f1"] = dict(family_f1)
    if precision is not None:
        payload["precision"] = precision
    if recall is not None:
        payload["recall"] = recall
    return payload


def attach_living_envelope(
    artifact: Mapping[str, Any],
    *,
    method: str,
    stages: Mapping[str, Mapping[str, Any]],
    replay_mode: ReplayMode,
    prompt_version: str | None = None,
) -> dict[str, Any]:
    """Copy a runner artifact and attach the living envelope."""

    task = TASK_FOR_METHOD[method]
    payload = dict(artifact)
    payload["living_schema_version"] = LIVING_SCHEMA_VERSION
    payload["task"] = task
    payload["method"] = method
    payload["cell"] = CELL_FOR_METHOD[method]
    payload["headline"] = HEADLINE_STAGE
    payload["replay_mode"] = replay_mode
    payload["scorer"] = scorer_for_task(task)
    if prompt_version is not None:
        payload["prompt_version"] = prompt_version
    payload["stages"] = {name: dict(stages[name]) for name in REQUIRED_STAGES}
    select = payload["stages"]["select"]
    if task == "gan2026":
        payload["score"] = {
            "purist_correct": select["purist_correct"],
            "purist_accuracy": select["purist_accuracy"],
            "n": select["n"],
        }
    else:
        payload["score"] = {
            "four_family_micro_f1": select["four_family_micro_f1"],
        }
    validate_living_comparison(payload)
    return payload


def validate_living_comparison(payload: Mapping[str, Any]) -> None:
    """Raise if a living envelope is missing required facts or uses retired names."""

    if payload.get("living_schema_version") != LIVING_SCHEMA_VERSION:
        raise ValueError("living comparison is missing living_schema_version")
    missing = [key for key in REQUIRED_IDENTITY if key not in payload]
    if missing:
        raise ValueError(f"living comparison missing {missing}")
    if payload["headline"] != HEADLINE_STAGE:
        raise ValueError("living headline must be select")
    stages = payload.get("stages")
    if not isinstance(stages, Mapping):
        raise ValueError("living comparison missing stages")
    for name in REQUIRED_STAGES:
        if name not in stages or not isinstance(stages[name], Mapping):
            raise ValueError(f"living comparison missing stage {name}")
    scorer = payload["scorer"]
    select = stages["select"]
    if scorer == GAN_SCORER:
        if "purist_accuracy" not in select or "purist_correct" not in select:
            raise ValueError("Gan select stop must carry Purist")
    elif scorer == EXECT_SCORER:
        if "four_family_micro_f1" not in select:
            raise ValueError("ExECT select stop must carry four_family_micro_f1")
        primary = payload.get("score") or {}
        overlap = FORBIDDEN_LIVING_PRIMARY.intersection(primary)
        if overlap:
            raise ValueError(f"living ExECT primary still uses {sorted(overlap)}")
    else:
        raise ValueError(f"unsupported living scorer {scorer!r}")


def adapt_legacy_comparison(payload: Mapping[str, Any]) -> dict[str, Any] | None:
    """Best-effort living view of a historical comparison. None if unreadable."""

    if payload.get("living_schema_version") == LIVING_SCHEMA_VERSION:
        return dict(payload)
    method = str(payload.get("method") or "")
    if method not in CELL_FOR_METHOD:
        arms = payload.get("arms")
        if isinstance(arms, Mapping):
            for key in (
                "exect_llm_extract",
                "exect_llm_pre_post",
                "exect_llm_with_rules",
                "exect_llm_only",
                "compact_ledger",
            ):
                if key in arms:
                    method = (
                        "exect_llm_extract_and_select"
                        if key in {
                            "exect_llm_only",
                            "exect_llm_extract_filtered",
                            "compact_ledger",
                        }
                        else ("exect_llm_pre_post" if key != "exect_llm_extract" else key)
                    )
                    break
    if method not in CELL_FOR_METHOD:
        return None
    task = TASK_FOR_METHOD[method]
    n = int(payload.get("row_count") or payload.get("n") or 0)
    if task == "gan2026":
        summary = payload.get("summary") or {}
        if not isinstance(summary, Mapping):
            return None
        correct = int(summary.get("purist_correct") or 0)
        pragmatic = summary.get("pragmatic_correct")
        stage = gan_stage(
            purist_correct=correct,
            n=n or int(summary.get("examples") or 0),
            pragmatic_correct=None if pragmatic is None else int(pragmatic),
        )
        stages = {"extract": dict(stage), "encode": dict(stage), "select": dict(stage)}
        return attach_living_envelope(
            payload,
            method=method,
            stages=stages,
            replay_mode="live" if payload.get("live") else "no_call",
            prompt_version=str(payload.get("prompt_version") or method),
        )
    arm = _legacy_exect_arm(payload)
    if arm is None:
        later = payload.get("four_family_headline_f1")
        if later is None:
            return None
        stage = exect_stage(four_family_micro_f1=float(later))
        stages = {"extract": dict(stage), "encode": dict(stage), "select": dict(stage)}
        return attach_living_envelope(
            payload,
            method=method,
            stages=stages,
            replay_mode="live" if payload.get("live") else "no_call",
            prompt_version=str(payload.get("prompt_version") or method),
        )
    extract = exect_stage(
        four_family_micro_f1=float(arm.get("raw_headline_f1") or 0.0),
        family_f1=arm.get("raw_family_f1")
        if isinstance(arm.get("raw_family_f1"), Mapping)
        else None,
    )
    select = exect_stage(
        four_family_micro_f1=float(arm.get("hybrid_headline_f1") or 0.0),
        family_f1=arm.get("hybrid_family_f1")
        if isinstance(arm.get("hybrid_family_f1"), Mapping)
        else None,
    )
    encode_f1 = arm.get("encode_headline_f1")
    encode = (
        exect_stage(four_family_micro_f1=float(encode_f1))
        if encode_f1 is not None
        else dict(extract)
    )
    return attach_living_envelope(
        payload,
        method=method,
        stages={"extract": extract, "encode": encode, "select": select},
        replay_mode="live" if payload.get("live") else "no_call",
        prompt_version=str(
            arm.get("prompt_version") or payload.get("prompt_version") or method
        ),
    )


def stage_metric(payload: Mapping[str, Any], stage: str) -> float | None:
    """Return the cited metric for one stage from a living or adapted file."""

    living = (
        payload
        if payload.get("living_schema_version") == LIVING_SCHEMA_VERSION
        else adapt_legacy_comparison(payload)
    )
    if living is None:
        return None
    block = (living.get("stages") or {}).get(stage)
    if not isinstance(block, Mapping):
        return None
    if "four_family_micro_f1" in block:
        return float(block["four_family_micro_f1"])
    if "purist_accuracy" in block:
        return float(block["purist_accuracy"])
    return None


def _legacy_exect_arm(payload: Mapping[str, Any]) -> Mapping[str, Any] | None:
    arms = payload.get("arms")
    if not isinstance(arms, Mapping):
        return None
    for key in (
        "exect_llm_extract",
        "exect_llm_pre_post",
        "exect_llm_with_rules",
        "exect_llm_only",
        "compact_ledger",
    ):
        arm = arms.get(key)
        if isinstance(arm, Mapping):
            return arm
    return None
