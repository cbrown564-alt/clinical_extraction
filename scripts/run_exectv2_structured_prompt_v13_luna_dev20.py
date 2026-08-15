"""Luna-only ExECT v13 short-extraction study on the frozen v10 dev20 sample.

``check`` builds the v13 payload and scores the two no-call arms.
``run --live`` is 20 Luna calls and is not authorized by the protocol
alone.
"""

# ruff: noqa: E501

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_attribute_encoding import (
    apply_sf_attribute_encoding,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    has_blocking_parse_issue,
)
from scripts import run_exectv2_structured_prompt_v10_luna_dev20 as v10_run

_ORIGINAL_ARM_ASSEMBLY = v10_run._arm_assembly

REPO_ROOT = Path(__file__).resolve().parents[1]
STUDY_DIR = REPO_ROOT / "experiments/exectv2_structured_prompt_v13_luna_dev20_20260815"
V10_SAMPLE = (
    REPO_ROOT / "experiments/exectv2_structured_prompt_v10_luna_dev20_20260815/sample.json"
)
V12_STRUCTURED = (
    REPO_ROOT
    / "experiments/exectv2_structured_prompt_v12_luna_dev20_20260815/v12_live/structured.jsonl"
)
V0924_STRUCTURED = (
    REPO_ROOT
    / "experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715_structured.jsonl"
)
PROTOCOL = (
    "docs/research/exectv2/structured_prompt_v13_luna_dev20_protocol_2026-08-15.md"
)
REPORT_PATH = (
    REPO_ROOT / "docs/research/exectv2/structured_prompt_v13_luna_dev20_2026-08-15.md"
)
MODEL = "openai/gpt-5.6-luna"
FROZEN_IDS = (
    "EA0002",
    "EA0004",
    "EA0005",
    "EA0006",
    "EA0007",
    "EA0008",
    "EA0009",
    "EA0010",
    "EA0011",
    "EA0012",
    "EA0015",
    "EA0016",
    "EA0047",
    "EA0074",
    "EA0093",
    "EA0120",
    "EA0131",
    "EA0133",
    "EA0154",
    "EA0158",
)
FORBIDDEN_PAYLOAD_TOKENS = (
    "several",
    "couple",
    "candidate_evidence_ledger",
    "architecture",
    "worked_examples",
    "LastClinic",
)
HEADLINE_DROP_LIMIT = 0.05
FAMILY_DROP_LIMIT = 0.08
NET_LOSS_LIMIT = 3


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check_parser = sub.add_parser(
        "check",
        help="Verify v13 payload and score the two no-call arms. No model calls.",
    )
    check_parser.add_argument("--overwrite", action="store_true")
    run_parser = sub.add_parser("run", help="Score saved arms; live only with --live")
    run_parser.add_argument(
        "--live",
        action="store_true",
        help="Make 20 Luna calls. Forbidden unless the protocol is explicitly authorized.",
    )
    run_parser.add_argument("--overwrite", action="store_true")
    run_parser.add_argument("--progress-every", type=int, default=1)
    run_parser.add_argument("--api-base")
    args = parser.parse_args(argv)
    if args.command == "check":
        print(
            json.dumps(
                check(overwrite=args.overwrite),
                indent=2,
                sort_keys=True,
            )
        )
        return
    print(
        json.dumps(
            run_study(
                live=args.live,
                overwrite=args.overwrite,
                progress_every=args.progress_every,
                api_base=args.api_base,
            ),
            indent=2,
            sort_keys=True,
        )
    )


def verify_payload() -> dict[str, Any]:
    sample = json.loads(V10_SAMPLE.read_text(encoding="utf-8"))
    if sample["letter_ids"] != list(FROZEN_IDS):
        raise RuntimeError("frozen v10 sample IDs drifted; protocol must not redraw")
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    original = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(structured.PROMPT_VERSION_V13)
        payload = json.loads(structured.build_prompt_input(letter))
    finally:
        structured.set_active_prompt_version(original)
    joined = (
        " ".join(payload["clinical_rules"])
        + " "
        + payload["task"]
        + " "
        + " ".join(payload["family_guidance"].values())
    )
    leaks = [token for token in FORBIDDEN_PAYLOAD_TOKENS if token in joined]
    if leaks:
        raise RuntimeError(f"v13 payload leaked codebook or ledger terms: {leaks}")
    if structured.PROMPT_VERSION != structured.PROMPT_VERSION_V0_9_24:
        raise RuntimeError("check must not leave v13 as the active default")
    if payload["prompt_version"] != structured.PROMPT_VERSION_V13:
        raise RuntimeError("v13 payload did not emit the v13 identity")
    if "letter's own words" not in joined:
        raise RuntimeError("v13 payload missing English-quantity permission")
    if "driving" in joined.lower() or "Completed tests only" in joined:
        raise RuntimeError("v13 payload restored the v12 scope sermon")
    if len(payload["clinical_rules"]) != 14:
        raise RuntimeError(
            f"v13 should have 14 hygiene rules, found {len(payload['clinical_rules'])}"
        )
    for key in (
        "architecture",
        "decision_procedure",
        "candidate_evidence_ledger",
        "event_lane_guide",
        "worked_examples",
    ):
        if key in payload:
            raise RuntimeError(f"v13 payload still contains {key}")
    return {
        "ok": True,
        "model_calls": 0,
        "prompt_version": payload["prompt_version"],
        "default_prompt_version": structured.PROMPT_VERSION,
        "n_rules": len(payload["clinical_rules"]),
        "letter_ids": list(FROZEN_IDS),
        "protocol": PROTOCOL,
    }


def check(*, overwrite: bool = False) -> dict[str, Any]:
    payload = verify_payload()
    scored = run_study(live=False, overwrite=overwrite)
    return {**payload, **scored, "model_calls": 0}


def run_study(
    *,
    live: bool,
    overwrite: bool = False,
    progress_every: int = 1,
    api_base: str | None = None,
) -> dict[str, Any]:
    verify_payload()
    sample = json.loads(V10_SAMPLE.read_text(encoding="utf-8"))
    letters = [
        letter
        for letter in load_letters_for_split("dev")
        if letter.letter_id in set(FROZEN_IDS)
    ]
    letters.sort(key=lambda item: item.letter_id)
    if len(letters) != 20:
        raise RuntimeError(f"expected 20 letters, found {len(letters)}")

    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    original_dir = v10_run.STUDY_DIR
    original_control = v10_run.CONTROL_STRUCTURED
    original_reason = v10_run.ESCALATION_REASON
    original_assembly = v10_run._arm_assembly
    try:
        v10_run.STUDY_DIR = STUDY_DIR
        v10_run.CONTROL_STRUCTURED = V0924_STRUCTURED
        v10_run.ESCALATION_REASON = (
            "Predeclared Luna-only ExECT v13 short-extraction study on the frozen "
            "v10 20-letter sample under " + PROTOCOL
        )
        v10_run._arm_assembly = _patched_arm_assembly
        control = _run_enriched_arm(
            slug="v0924_head",
            prompt_version=structured.PROMPT_VERSION_V0_9_24,
            letters=letters,
            call_mode="saved_structured_no_call",
            overwrite=overwrite,
            progress_every=progress_every,
            api_base=api_base,
        )
        v10_run.CONTROL_STRUCTURED = V12_STRUCTURED
        mechanism = _run_enriched_arm(
            slug="v12_head",
            prompt_version=structured.PROMPT_VERSION_V12,
            letters=letters,
            call_mode="saved_structured_no_call",
            overwrite=overwrite,
            progress_every=progress_every,
            api_base=api_base,
        )
        candidate: dict[str, Any] | None = None
        if live:
            candidate = _run_enriched_arm(
                slug="v13_live",
                prompt_version=structured.PROMPT_VERSION_V13,
                letters=letters,
                call_mode="live",
                overwrite=overwrite,
                progress_every=progress_every,
                api_base=api_base,
            )
    finally:
        v10_run.STUDY_DIR = original_dir
        v10_run.CONTROL_STRUCTURED = original_control
        v10_run.ESCALATION_REASON = original_reason
        v10_run._arm_assembly = original_assembly

    arms = {
        "v0924_head": control["summary"],
        "v12_head": mechanism["summary"],
    }
    artifact: dict[str, Any] = {
        "schema_version": "exectv2.structured_prompt_v13_luna_dev20.v1",
        "generated_on": "2026-08-15",
        "protocol": PROTOCOL,
        "model": MODEL,
        "split": "dev140",
        "row_count": 20,
        "sample": sample,
        "repair_policy": {
            "diagnosis_policy_variant": "default",
            "prescription_policy_variant": "default",
        },
        "replay_mode": {
            "v0924_head": "saved_structured_no_call",
            "v12_head": "saved_structured_no_call",
            "v13_live": "live" if live else "not_run",
        },
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": live,
        "model_calls": 20 if live else 0,
        "letter_ids": list(FROZEN_IDS),
        "default_prompt_version": structured.PROMPT_VERSION,
        "arms": arms,
        "comparison": {
            "v12_head_minus_v0924_head": _compare_pair(control, mechanism, letters)
        },
        "decision": {
            "status": "live_not_run",
            "verdict": None,
            "rule": (
                "topology sufficient on hybrid vs v0924_head if headline F1 "
                "drop < 0.05, no family F1 drop >= 0.08, and net four-family "
                "letter-exact losses < 3"
            ),
        },
        "claim_boundary": (
            "ExECTv2 Luna 20-letter development comparison of v13+HEAD "
            "against frozen v0.9.24 through the same stack. Not holdout, "
            "not a selected prompt, and not benchmark performance."
        ),
    }
    if candidate is not None:
        artifact["arms"]["v13_live"] = candidate["summary"]
        versus_control = _compare_pair(control, candidate, letters)
        versus_mechanism = _compare_pair(mechanism, candidate, letters)
        artifact["comparison"]["v13_live_minus_v0924_head"] = versus_control
        artifact["comparison"]["v13_live_minus_v12_head"] = versus_mechanism
        artifact["decision"] = decide_topology(versus_control, versus_mechanism)

    out = STUDY_DIR / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(_render_report(artifact), encoding="utf-8")
    return {
        "artifact": out.relative_to(REPO_ROOT).as_posix(),
        "report": REPORT_PATH.relative_to(REPO_ROOT).as_posix(),
        "live": live,
        "model_calls": artifact["model_calls"],
        "decision": artifact["decision"],
    }



def _patched_arm_assembly(slug: str, structured_path: Path, sf_final_path: Path) -> Any:
    cfg = _ORIGINAL_ARM_ASSEMBLY(slug, structured_path, sf_final_path)
    return replace(
        cfg,
        candidate_id=f"exectv2_structured_prompt_v13_luna_dev20_{slug}",
        claim_boundary=(
            "ExECTv2 Luna v13 short-extraction study on the frozen 20-letter v10 sample."
        ),
    )


def _run_enriched_arm(
    *,
    slug: str,
    prompt_version: str,
    letters: Sequence[Any],
    call_mode: str,
    overwrite: bool,
    progress_every: int,
    api_base: str | None,
) -> dict[str, Any]:
    arm = v10_run._run_arm(
        slug=slug,
        prompt_version=prompt_version,
        letters=letters,
        call_mode=call_mode,
        overwrite=overwrite,
        progress_every=progress_every,
        api_base=api_base,
    )
    structured_path = v10_run.STUDY_DIR / slug / "structured.jsonl"
    structured_rows = {
        str(row["letter_id"]): row for row in v10_run._read_jsonl(structured_path)
    }
    letter_rows = []
    for row in arm["letter_rows"]:
        structured_row = structured_rows[str(row["letter_id"])]
        letter_rows.append(
            {
                **row,
                "replay_mode": call_mode,
                "prompt_profile": structured_row.get("prompt_profile", "full"),
                "repair_policy": "default/default",
                "model": MODEL,
            }
        )
    metrics = _letter_metrics(letters, letter_rows, structured_rows, slug, prompt_version, call_mode)
    v10_run.write_jsonl(metrics, v10_run.STUDY_DIR / slug / "letter_metrics.jsonl")
    quality = _quality_counts(list(structured_rows.values()))
    encoding = _arm_encoding_counts(list(structured_rows.values()))
    raw_prf = _surface_prf(letter_rows, "raw_keys")
    hybrid_prf = _surface_prf(letter_rows, "hybrid_keys")
    summary = {
        **arm["summary"],
        "call_mode": call_mode,
        "raw_headline_prf": raw_prf["overall"],
        "raw_family_prf": raw_prf["by_family"],
        "hybrid_headline_prf": hybrid_prf["overall"],
        "hybrid_family_prf": hybrid_prf["by_family"],
        "quality": quality,
        "sf_encoding_rewrites": encoding,
        "raw_mention_count": sum(int(row.get("n_mentions_raw") or 0) for row in structured_rows.values()),
        "scored_mention_count": sum(
            int(row.get("n_mentions_scored") or 0) for row in structured_rows.values()
        ),
        "gate_event_count": sum(len(row.get("gate_warnings") or []) for row in structured_rows.values()),
    }
    return {"summary": summary, "letter_rows": letter_rows, "report": arm["report"]}


def _letter_metrics(
    letters: Sequence[Any],
    letter_rows: Sequence[Mapping[str, Any]],
    structured_rows: Mapping[str, Mapping[str, Any]],
    slug: str,
    prompt_version: str,
    call_mode: str,
) -> list[dict[str, Any]]:
    by_letter: dict[str, list[Mapping[str, Any]]] = {}
    for row in letter_rows:
        by_letter.setdefault(str(row["letter_id"]), []).append(row)
    out: list[dict[str, Any]] = []
    for letter in letters:
        letter_id = letter.letter_id
        family_rows = by_letter[letter_id]
        structured_row = structured_rows[letter_id]
        raw = _prf_from_family_rows(family_rows, "raw_keys")
        hybrid = _prf_from_family_rows(family_rows, "hybrid_keys")
        encoding = count_sf_encoding_rewrites(structured_row.get("predicted_mentions") or [])
        raw_count = sum(int(row["raw_mention_count"]) for row in family_rows)
        hybrid_count = sum(int(row["hybrid_mention_count"]) for row in family_rows)
        out.append(
            {
                "arm": slug,
                "prompt_version": prompt_version,
                "prompt_profile": structured_row.get("prompt_profile", "full"),
                "replay_mode": call_mode,
                "repair_policy": "default/default",
                "model": MODEL,
                "letter_id": letter_id,
                "raw_mention_count": int(structured_row.get("n_mentions_raw") or raw_count),
                "scored_mention_count": int(structured_row.get("n_mentions_scored") or raw_count),
                "hybrid_mention_count": hybrid_count,
                "hybrid_minus_raw_mention_count": hybrid_count - raw_count,
                "codebook_effect": _codebook_effect(family_rows, hybrid_count - raw_count),
                "gate_events": list(structured_row.get("gate_warnings") or []),
                "raw_headline_prf": raw,
                "hybrid_headline_prf": hybrid,
                "raw_four_family_letter_exact": all(
                    bool(row["raw_letter_exact"]) for row in family_rows
                ),
                "hybrid_four_family_letter_exact": all(
                    bool(row["hybrid_letter_exact"]) for row in family_rows
                ),
                "family_letter_exact": {
                    str(row["family"]): {
                        "raw": bool(row["raw_letter_exact"]),
                        "hybrid": bool(row["hybrid_letter_exact"]),
                    }
                    for row in family_rows
                },
                "sf_encoding_rewrites": encoding,
                "quality": _quality_counts([structured_row]),
            }
        )
    return out


def _codebook_effect(family_rows: Sequence[Mapping[str, Any]], delta_count: int) -> str:
    rewrote = any(bool(row["hybrid_rewrote"]) for row in family_rows)
    if delta_count > 0 and rewrote:
        return "add_and_rewrite"
    if delta_count < 0 and rewrote:
        return "drop_and_rewrite"
    if delta_count > 0:
        return "add"
    if delta_count < 0:
        return "drop"
    if rewrote:
        return "rewrite"
    return "none"


def count_sf_encoding_rewrites(mentions: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts = {
        "several": 0,
        "few": 0,
        "range_split": 0,
        "interval_missing_1": 0,
        "other_word_number": 0,
    }
    for mention in mentions:
        if str(mention.get("entity") or "") != SEIZURE_FREQUENCY.name:
            continue
        raw = str((mention.get("attributes") or {}).get("NumberOfSeizures") or "").strip()
        _rewritten, actions = apply_sf_attribute_encoding([mention])
        rules = {str(action.get("rule_id") or "") for action in actions}
        if "encoding.word_number" in rules:
            token = raw.lower()
            if token == "several":
                counts["several"] += 1
            elif token in {"few", "a few"}:
                counts["few"] += 1
            else:
                counts["other_word_number"] += 1
        if "encoding.range_split" in rules:
            counts["range_split"] += 1
        if "encoding.interval_completer" in rules:
            counts["interval_missing_1"] += 1
    return counts


def _arm_encoding_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    totals: Counter[str] = Counter()
    for row in rows:
        totals.update(count_sf_encoding_rewrites(row.get("predicted_mentions") or []))
    return dict(totals)


def _quality_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    schema = 0
    parse = 0
    illegal_enum = 0
    inexact = 0
    for row in rows:
        errors = [str(item) for item in (row.get("parse_errors") or [])]
        initial = [str(item) for item in (row.get("initial_parse_errors") or [])]
        warnings = [str(item) for item in (row.get("gate_warnings") or [])]
        if any(item.startswith("schema_validation_error:") for item in [*errors, *initial]):
            schema += 1
        if any(item.startswith("invalid_json:") for item in [*errors, *initial]):
            parse += 1
        if has_blocking_parse_issue(errors) and not (
            any(item.startswith("schema_validation_error:") for item in errors)
            or any(item.startswith("invalid_json:") for item in errors)
        ):
            schema += 1
        illegal_enum += sum(1 for item in warnings if "dropped_illegal_value:" in item)
        inexact += int(row.get("n_evidence_invalid") or 0)
        if not row.get("n_evidence_invalid"):
            inexact += sum(
                1
                for item in warnings
                if item.startswith("dropped_evidence_not_substring:")
                or item.startswith("dropped_empty_evidence:")
            )
    return {
        "schema": schema,
        "parse": parse,
        "illegal_enum": illegal_enum,
        "inexact_evidence": inexact,
    }


def _surface_prf(
    letter_rows: Sequence[Mapping[str, Any]], key_field: str
) -> dict[str, Any]:
    by_family: dict[str, dict[str, float]] = {}
    overall: Counter[str] = Counter()
    for family in v10_run.FAMILIES:
        counts: Counter[str] = Counter()
        for row in letter_rows:
            if row["family"] != family:
                continue
            gold = v10_run._counter_from_rows(row["gold_keys"])
            pred = v10_run._counter_from_rows(row[key_field])
            counts += v10_run._prf_counts(gold, pred)
        overall += counts
        by_family[family] = _prf(counts)
    return {"overall": _prf(overall), "by_family": by_family}


def _prf_from_family_rows(
    family_rows: Sequence[Mapping[str, Any]], key_field: str
) -> dict[str, float]:
    counts: Counter[str] = Counter()
    for row in family_rows:
        gold = v10_run._counter_from_rows(row["gold_keys"])
        pred = v10_run._counter_from_rows(row[key_field])
        counts += v10_run._prf_counts(gold, pred)
    return _prf(counts)


def _prf(counts: Mapping[str, int]) -> dict[str, float]:
    tp = int(counts.get("tp", 0))
    fp = int(counts.get("fp", 0))
    fn = int(counts.get("fn", 0))
    precision = 0.0 if tp + fp == 0 else round(tp / (tp + fp), 4)
    recall = 0.0 if tp + fn == 0 else round(tp / (tp + fn), 4)
    denom = 2 * tp + fp + fn
    f1 = 0.0 if denom == 0 else round(2 * tp / denom, 4)
    return {"precision": precision, "recall": recall, "f1": f1}


def _compare_pair(
    control: Mapping[str, Any],
    candidate: Mapping[str, Any],
    letters: Sequence[Any],
) -> dict[str, Any]:
    return v10_run._compare_arms(control, candidate, letters)


def decide_topology(
    versus_control: Mapping[str, Any],
    versus_mechanism: Mapping[str, Any],
) -> dict[str, Any]:
    hybrid = versus_control["surfaces"]["hybrid"]
    failures = topology_failures(hybrid)
    verdict = "topology_sufficient" if not failures else "still_missing_extraction"
    return {
        "status": "scored",
        "verdict": verdict,
        "failures": failures,
        "hybrid_vs_v0924_head": {
            "headline_f1_delta": hybrid["headline_f1_delta"],
            "family_f1_delta": hybrid["family_f1_delta"],
            "four_family_letter_exact_net": hybrid["four_family_letter_exact_net"],
            "four_family_letter_exact_wins": hybrid["four_family_letter_exact_wins"],
            "four_family_letter_exact_losses": hybrid["four_family_letter_exact_losses"],
        },
        "hybrid_vs_v12_head": {
            "headline_f1_delta": versus_mechanism["surfaces"]["hybrid"]["headline_f1_delta"],
            "family_f1_delta": versus_mechanism["surfaces"]["hybrid"]["family_f1_delta"],
            "four_family_letter_exact_net": versus_mechanism["surfaces"]["hybrid"][
                "four_family_letter_exact_net"
            ],
        },
        "note": (
            "A v13 hybrid gain vs v12_head with a remaining gap vs v0924_head "
            "means the short leftover contract helped and extraction is still "
            "weaker. That is not a reason to put List 11 back in the prompt."
        ),
    }


def topology_failures(hybrid: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    delta = float(hybrid["headline_f1_delta"])
    if delta <= -HEADLINE_DROP_LIMIT:
        failures.append(f"hybrid four-family F1 drop {delta}")
    for family, family_delta in dict(hybrid["family_f1_delta"]).items():
        if float(family_delta) <= -FAMILY_DROP_LIMIT:
            failures.append(f"hybrid {family} F1 drop {family_delta}")
    losses = int(hybrid["four_family_letter_exact_losses"])
    wins = int(hybrid["four_family_letter_exact_wins"])
    net_losses = losses - wins
    if net_losses >= NET_LOSS_LIMIT:
        failures.append(f"hybrid net four-family letter-exact losses {net_losses}")
    return failures


def _render_report(artifact: Mapping[str, Any]) -> str:
    live = bool(artifact["live"])
    decision = artifact["decision"]
    sample = artifact["sample"]
    ctrl = artifact["arms"]["v0924_head"]
    mech = artifact["arms"]["v12_head"]
    cand = artifact["arms"].get("v13_live")
    bands = "\n".join(
        f"- **{band}:** {', '.join(ids)}" for band, ids in sample["bands"].items()
    )
    if not live:
        status = "no-call check complete; live arm not run"
        verdict = (
            "Live Luna is not authorized by the protocol alone. "
            "The two no-call arms are scored through HEAD."
        )
        live_tables = (
            "Live arm not run. `v13_live` scores, the topology decision, "
            "and paired deltas versus `v0924_head` / `v12_head` are absent."
        )
    else:
        status = f"complete; {decision['verdict']}"
        verdict = (
            f"**{decision['verdict']}.** This is not a promotion and not a "
            "benchmark score. Failures: "
            + (", ".join(decision.get("failures") or ["none"]) + ".")
        )
        vs_ctrl = artifact["comparison"]["v13_live_minus_v0924_head"]
        vs_mech = artifact["comparison"]["v13_live_minus_v12_head"]
        raw = vs_ctrl["surfaces"]["raw"]
        hybrid = vs_ctrl["surfaces"]["hybrid"]
        hybrid_v12 = vs_mech["surfaces"]["hybrid"]
        live_tables = f"""## Headline F1 on the 20-letter pool

| Surface | v0.9.24 HEAD | v12 HEAD | v13 live | v13 − v0.9.24 | v13 − v12 |
| :--- | ---: | ---: | ---: | ---: | ---: |
| raw | {ctrl["raw_headline_f1"]:.4f} | {mech["raw_headline_f1"]:.4f} | {cand["raw_headline_f1"]:.4f} | {raw["headline_f1_delta"]:+.4f} | {vs_mech["surfaces"]["raw"]["headline_f1_delta"]:+.4f} |
| hybrid | {ctrl["hybrid_headline_f1"]:.4f} | {mech["hybrid_headline_f1"]:.4f} | {cand["hybrid_headline_f1"]:.4f} | {hybrid["headline_f1_delta"]:+.4f} | {hybrid_v12["headline_f1_delta"]:+.4f} |

## Family F1 delta (hybrid)

| Family | v13 − v0.9.24 | v13 − v12 |
| :--- | ---: | ---: |
| Diagnosis | {hybrid["family_f1_delta"]["Diagnosis"]:+.4f} | {hybrid_v12["family_f1_delta"]["Diagnosis"]:+.4f} |
| SeizureFrequency | {hybrid["family_f1_delta"]["SeizureFrequency"]:+.4f} | {hybrid_v12["family_f1_delta"]["SeizureFrequency"]:+.4f} |
| Prescription | {hybrid["family_f1_delta"]["Prescription"]:+.4f} | {hybrid_v12["family_f1_delta"]["Prescription"]:+.4f} |
| Investigations | {hybrid["family_f1_delta"]["Investigations"]:+.4f} | {hybrid_v12["family_f1_delta"]["Investigations"]:+.4f} |

## Four-family letter-exact wins / losses (v13 vs v0.9.24)

| Surface | wins | losses | net |
| :--- | ---: | ---: | ---: |
| raw | {raw["four_family_letter_exact_wins"]} | {raw["four_family_letter_exact_losses"]} | {raw["four_family_letter_exact_net"]} |
| hybrid | {hybrid["four_family_letter_exact_wins"]} | {hybrid["four_family_letter_exact_losses"]} | {hybrid["four_family_letter_exact_net"]} |

## SF encoding rewrites on model NumberOfSeizures

| Arm | several | few | range split | interval → 1 |
| :--- | ---: | ---: | ---: | ---: |
| v0.9.24 HEAD | {ctrl["sf_encoding_rewrites"]["several"]} | {ctrl["sf_encoding_rewrites"]["few"]} | {ctrl["sf_encoding_rewrites"]["range_split"]} | {ctrl["sf_encoding_rewrites"]["interval_missing_1"]} |
| v12 HEAD | {mech["sf_encoding_rewrites"]["several"]} | {mech["sf_encoding_rewrites"]["few"]} | {mech["sf_encoding_rewrites"]["range_split"]} | {mech["sf_encoding_rewrites"]["interval_missing_1"]} |
| v13 live | {cand["sf_encoding_rewrites"]["several"]} | {cand["sf_encoding_rewrites"]["few"]} | {cand["sf_encoding_rewrites"]["range_split"]} | {cand["sf_encoding_rewrites"]["interval_missing_1"]} |
"""
    return f"""# Luna `dev20` test of ExECT v13 short extraction leftover

Date: 2026-08-15
Status: {status}
Protocol: [structured_prompt_v13_luna_dev20_protocol_2026-08-15.md](structured_prompt_v13_luna_dev20_protocol_2026-08-15.md)
Model: `{artifact["model"]}`
Sample: frozen 20 letters from ExECT `dev140` (same IDs as v10 / v11 / v12); `test60` not touched

## Verdict

{verdict}

This study cannot promote v13 or change a fill.

## Frozen sample

Copied from the v10 freeze. Lowest `letter_id` within each band;
`EA0133` forced into hard. Not redrawn after scoring.

{bands}

Letter IDs: {", ".join(sample["letter_ids"])}

## Conditions

| Item | Value |
| :--- | :--- |
| Control | no-call reuse of the 15 Jul Luna `v0.9.24` structured sidecar through HEAD |
| Mechanism | no-call reuse of the saved v12 `dev20` structured sidecar through HEAD |
| Candidate | {"live Luna, `exectv2_hybrid_key_family_event_ledger_v13`, then HEAD" if live else "not run"} |
| Profile | `full` |
| Repair | default / default |
| Scorer | four-family `clinical_headline` unit keys; family-local letter exactness |
| Gold at prompt-build time | forbidden |
| Holdout | not touched |
| Default `PROMPT_VERSION` after run | `{artifact["default_prompt_version"]}` |

## No-call HEAD baselines on this cut

| Arm | raw F1 | hybrid F1 | hybrid four-family exact | SF several→N | SF few→N |
| :--- | ---: | ---: | ---: | ---: | ---: |
| v0924_head | {ctrl["raw_headline_f1"]:.4f} | {ctrl["hybrid_headline_f1"]:.4f} | {ctrl["hybrid_four_family_letter_exact"]}/20 | {ctrl["sf_encoding_rewrites"]["several"]} | {ctrl["sf_encoding_rewrites"]["few"]} |
| v12_head | {mech["raw_headline_f1"]:.4f} | {mech["hybrid_headline_f1"]:.4f} | {mech["hybrid_four_family_letter_exact"]}/20 | {mech["sf_encoding_rewrites"]["several"]} | {mech["sf_encoding_rewrites"]["few"]} |

{live_tables}

## Quality counts

| Arm | schema | parse | illegal enum | inexact evidence |
| :--- | ---: | ---: | ---: | ---: |
| v0924_head | {ctrl["quality"]["schema"]} | {ctrl["quality"]["parse"]} | {ctrl["quality"]["illegal_enum"]} | {ctrl["quality"]["inexact_evidence"]} |
| v12_head | {mech["quality"]["schema"]} | {mech["quality"]["parse"]} | {mech["quality"]["illegal_enum"]} | {mech["quality"]["inexact_evidence"]} |{"" if cand is None else chr(10) + f"| v13_live | {cand['quality']['schema']} | {cand['quality']['parse']} | {cand['quality']['illegal_enum']} | {cand['quality']['inexact_evidence']} |"}

## Boundary

Not `test60`. Not a selected prompt. Not a six-model claim. Parser, evidence
gate, attribute gate, and the Phase 3–5 hybrid codebook stayed at HEAD; only
the model-facing JSON changes on the v13 arm. v13 is not `PROMPT_VERSION`.
"""


if __name__ == "__main__":
    main()
