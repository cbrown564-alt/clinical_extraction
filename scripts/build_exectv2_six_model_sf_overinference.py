"""Build the no-call ExECTv2 six-model SF over-inference study."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    frequency_state_faithful,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "experiments/exectv2_six_model_sf_overinference_dev140_20260718.json"
OUTPUT_REPORT = (
    ROOT / "docs/experiments/exectv2/reliability/exectv2_six_model_sf_overinference_2026-07-18.md"
)
PROTOCOL = (
    "docs/experiments/exectv2/reliability/exectv2_six_model_sf_overinference_protocol_2026-07-18.md"
)

MODEL_SPECS = (
    ("GPT-4.1-mini", "gpt41mini"),
    ("GPT-5.6 Luna", "gpt56luna"),
    ("GPT-5.6 Sol", "gpt56sol"),
    ("DeepSeek V4 Flash, thinking enabled", "deepseek_v4_flash"),
    ("Qwen 3.6:35B", "qwen36_35b"),
    ("Gemma 4 26B", "gemma4_26b"),
)


def state_set(mentions: Iterable[Mapping[str, Any]]) -> set[str]:
    """Return the deduplicated change-aware SF states in a mention sequence."""

    return {
        frequency_state_faithful(mention.get("attributes", {}))
        for mention in mentions
        if mention.get("entity") == "SeizureFrequency"
    }


def classify_gold_band(states: set[str]) -> str:
    if not states:
        return "empty_gold"
    if states == {"unknown"}:
        return "unknown_only"
    if "active-rate" in states:
        return "active_rate_containing"
    if "seizure-free" in states:
        return "seizure_free_containing"
    if states == {"changed"}:
        return "changed_only"
    return "other_rate_absent"


def classify_transition(
    *, gold: set[str], comparator: set[str], candidate: set[str]
) -> dict[str, object]:
    changed = comparator != candidate
    comparator_correct = comparator == gold
    candidate_correct = candidate == gold

    if not changed:
        correctness = "unchanged_correct" if candidate_correct else "unchanged_wrong"
    elif not comparator_correct and candidate_correct:
        correctness = "wrong_to_correct"
    elif comparator_correct and not candidate_correct:
        correctness = "correct_to_wrong"
    else:
        correctness = "changed_still_wrong"

    if classify_gold_band(gold) != "unknown_only":
        overread = "not_primary_band"
    else:
        comparator_overread = "active-rate" in comparator
        candidate_overread = "active-rate" in candidate
        if comparator_overread and not candidate_overread:
            overread = "overread_rescued"
        elif not comparator_overread and candidate_overread:
            overread = "overread_introduced"
        elif comparator_overread and candidate_overread:
            overread = "persistent_overread"
        else:
            overread = "no_overread"

    return {
        "candidate_changed": changed,
        "overread_transition": overread,
        "correctness_transition": correctness,
    }


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_revision() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _evidence(mentions: Sequence[Mapping[str, Any]]) -> list[str]:
    return list(
        dict.fromkeys(
            str(mention.get("evidence", "")).strip()
            for mention in mentions
            if mention.get("entity") == "SeizureFrequency"
            and str(mention.get("evidence", "")).strip()
        )
    )


def _prf(rows: Sequence[Mapping[str, Any]], stage: str) -> dict[str, float | int]:
    tp = fp = fn = 0
    for row in rows:
        gold = set(row["gold_states"])
        predicted = set(row[f"{stage}_states"])
        tp += len(gold & predicted)
        fp += len(predicted - gold)
        fn += len(gold - predicted)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def _aggregate(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    primary = [row for row in rows if row["gold_band"] == "unknown_only"]
    bands: dict[str, dict[str, int | float]] = {}
    for band in sorted({str(row["gold_band"]) for row in rows}):
        band_rows = [row for row in rows if row["gold_band"] == band]
        bands[band] = {
            "letters": len(band_rows),
            "comparator_active_rate": sum(
                "active-rate" in row["comparator_states"] for row in band_rows
            ),
            "candidate_active_rate": sum(
                "active-rate" in row["candidate_states"] for row in band_rows
            ),
        }

    final_sf_mentions = sum(int(row["candidate_sf_mentions"]) for row in rows)
    exact_final_mentions = sum(int(row["candidate_exact_evidence_mentions"]) for row in rows)
    return {
        "row_count": len(rows),
        "unknown_only_denominator": len(primary),
        "comparator_unknown_only_active_rate_overreads": sum(
            "active-rate" in row["comparator_states"] for row in primary
        ),
        "candidate_unknown_only_active_rate_overreads": sum(
            "active-rate" in row["candidate_states"] for row in primary
        ),
        "comparator_unknown_only_active_rate_overread_rate": round(
            sum("active-rate" in row["comparator_states"] for row in primary) / len(primary),
            4,
        )
        if primary
        else None,
        "candidate_unknown_only_active_rate_overread_rate": round(
            sum("active-rate" in row["candidate_states"] for row in primary) / len(primary),
            4,
        )
        if primary
        else None,
        "comparator_exact_state_set": sum(
            row["gold_states"] == row["comparator_states"] for row in rows
        ),
        "candidate_exact_state_set": sum(
            row["gold_states"] == row["candidate_states"] for row in rows
        ),
        "comparator_state_profile": _prf(rows, "comparator"),
        "candidate_state_profile": _prf(rows, "candidate"),
        "correctness_transitions": dict(
            Counter(str(row["correctness_transition"]) for row in rows)
        ),
        "primary_overread_transitions": dict(
            Counter(str(row["overread_transition"]) for row in primary)
        ),
        "gold_bands": bands,
        "candidate_sf_mentions": final_sf_mentions,
        "candidate_exact_evidence_mentions": exact_final_mentions,
        "candidate_exact_evidence_rate": round(exact_final_mentions / final_sf_mentions, 4)
        if final_sf_mentions
        else None,
        "call_failure_rows": sum(bool(row["call_error"]) for row in rows),
        "structured_parse_error_rows": sum(bool(row["parse_errors"]) for row in rows),
    }


def build_payload() -> dict[str, Any]:
    models: list[dict[str, Any]] = []
    canonical_ids: set[str] | None = None
    canonical_gold: dict[str, list[dict[str, Any]]] | None = None

    for display_name, slug in MODEL_SPECS:
        stem = f"exectv2_six_model_single_call_{slug}_dev140_20260715"
        structured_path = ROOT / f"experiments/{stem}_structured.jsonl"
        final_rows_path = ROOT / f"experiments/{stem}.jsonl"
        final_aggregate_path = ROOT / f"experiments/{stem}.json"

        structured_by_id = {row["letter_id"]: row for row in _read_jsonl(structured_path)}
        final_by_id = {row["letter_id"]: row for row in _read_jsonl(final_rows_path)}
        if set(structured_by_id) != set(final_by_id) or len(final_by_id) != 140:
            raise ValueError(f"{display_name}: expected the same 140 dev140 IDs at both stages")
        if canonical_ids is None:
            canonical_ids = set(final_by_id)
            canonical_gold = {
                letter_id: final_by_id[letter_id]["gold_mentions"] for letter_id in final_by_id
            }
        elif set(final_by_id) != canonical_ids:
            raise ValueError(f"{display_name}: model panel does not share one ID set")

        final_aggregate = json.loads(final_aggregate_path.read_text(encoding="utf-8"))
        row_records: list[dict[str, Any]] = []
        for letter_id in sorted(final_by_id):
            structured = structured_by_id[letter_id]
            final = final_by_id[letter_id]
            if final["gold_mentions"] != canonical_gold[letter_id]:
                raise ValueError(f"{display_name}/{letter_id}: gold differs across models")

            gold_mentions = final["gold_mentions"]
            comparator_mentions = structured["predicted_mentions"]
            candidate_mentions = final["predicted_mentions"]
            gold_states = state_set(gold_mentions)
            comparator_states = state_set(comparator_mentions)
            candidate_states = state_set(candidate_mentions)
            transition = classify_transition(
                gold=gold_states,
                comparator=comparator_states,
                candidate=candidate_states,
            )
            candidate_sf = [
                mention
                for mention in candidate_mentions
                if mention.get("entity") == "SeizureFrequency"
            ]
            row_records.append(
                {
                    "letter_id": letter_id,
                    "gold_band": classify_gold_band(gold_states),
                    "gold_states": sorted(gold_states),
                    "comparator_states": sorted(comparator_states),
                    "candidate_states": sorted(candidate_states),
                    **transition,
                    "first_prediction_changing_owner": (
                        "deterministic_sf_projection_or_suppression"
                        if transition["candidate_changed"]
                        else "no_state_change"
                    ),
                    "comparator_evidence": _evidence(comparator_mentions),
                    "candidate_evidence": _evidence(candidate_mentions),
                    "candidate_sf_mentions": len(candidate_sf),
                    "candidate_exact_evidence_mentions": sum(
                        mention.get("evidence_valid") is True for mention in candidate_sf
                    ),
                    "call_error": structured.get("call_error"),
                    "parse_errors": structured.get("parse_errors", []),
                }
            )

        aggregate = _aggregate(row_records)
        aggregate["final_sf_parse_schema_failures"] = final_aggregate["lane_diagnostics"][
            "SeizureFrequency"
        ]["parse_schema_failures"]
        models.append(
            {
                "model": display_name,
                "runtime_model": final_aggregate["model_swap"]["model"],
                "runtime": final_aggregate["model_swap"]["runtime"],
                "structured_artifact": str(structured_path.relative_to(ROOT)).replace("\\", "/"),
                "structured_sha256": _sha256(structured_path),
                "final_rows_artifact": str(final_rows_path.relative_to(ROOT)).replace("\\", "/"),
                "final_rows_sha256": _sha256(final_rows_path),
                "aggregate": aggregate,
                "rows": row_records,
            }
        )

    denominator = {model["aggregate"]["unknown_only_denominator"] for model in models}
    if len(denominator) != 1:
        raise ValueError("unknown-only denominator must be identical for every model")
    primary_n = denominator.pop()
    return {
        "schema_version": "exectv2_six_model_sf_overinference_v1",
        "date": "2026-07-18",
        "question": (
            "Do the six fixed model conditions over-read active rate on gold "
            "unknown-only ExECTv2 dev140 letters, and what does deterministic "
            "SF projection/suppression change?"
        ),
        "protocol": PROTOCOL,
        "dataset": "ExECTv2",
        "split": "manifest-defined dev140",
        "split_manifest": "data/ExECTv2 (2025)/splits/exectv2_split_v1.json",
        "row_inspection_policy": "dev140 permitted; no test60 row access",
        "call_mode": "saved-output replay; zero model calls",
        "scorer": "frequency_state_faithful per-letter state set",
        "prompt_version": "exectv2_hybrid_key_family_event_ledger_v0.9.24",
        "comparator": "structured model predicted_mentions before SF projection/suppression",
        "candidate": "final assembled predicted_mentions",
        "repair_policy": (
            "selected joint bounded policy; SF state projection v0.6 and "
            "unsupported-state suppression v0.7"
        ),
        "source_revision": _git_revision(),
        "dirty_tree_note": (
            "Generated from the current working tree; source artifacts are hash-recorded."
        ),
        "primary_denominator": primary_n,
        "primary_evidence_state": "development_answer" if primary_n >= 10 else "diagnostic",
        "models": models,
        "claim_boundary": (
            "ExECTv2 dev140 development evidence for the named six model conditions "
            "and fixed state transform; not Gan-to-ExECT transfer validation, test60 "
            "evidence, clinical validation, or an empty-gold factuality estimate."
        ),
    }


def _rate(value: Any) -> str:
    return "n/a" if value is None else f"{float(value):.4f}"


def render_report(payload: Mapping[str, Any]) -> str:
    models = payload["models"]
    protocol_name = Path(str(payload["protocol"])).name
    primary_n = payload["primary_denominator"]
    primary_state = payload["primary_evidence_state"]
    lines = [
        "# ExECTv2 six-model Seizure Frequency over-inference result",
        "",
        "Date: 2026-07-18  ",
        "Status: completed no-call dev140 study",
        "",
        f"Protocol: [{protocol_name}]({protocol_name})  ",
        (
            "Machine-readable result: "
            "`experiments/exectv2_six_model_sf_overinference_dev140_20260718.json`"
        ),
        "",
        "## Answer",
        "",
        (
            f"The primary gold unknown-only denominator contains **{primary_n} letters**, "
            f"so the result is classified as **{primary_state}**."
        ),
        "",
        (
            "| Model | Comparator over-read | Final over-read | Comparator state F1 | "
            "Final state F1 | W→C | C→W |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for model in models:
        aggregate = model["aggregate"]
        transitions = aggregate["correctness_transitions"]
        denominator = aggregate["unknown_only_denominator"]
        comparator_overreads = aggregate["comparator_unknown_only_active_rate_overreads"]
        candidate_overreads = aggregate["candidate_unknown_only_active_rate_overreads"]
        comparator_rate = aggregate["comparator_unknown_only_active_rate_overread_rate"]
        candidate_rate = aggregate["candidate_unknown_only_active_rate_overread_rate"]
        lines.append(
            f"| {model['model']} | "
            f"{comparator_overreads}/{denominator} ({_rate(comparator_rate)}) | "
            f"{candidate_overreads}/{denominator} ({_rate(candidate_rate)}) | "
            f"{aggregate['comparator_state_profile']['f1']:.4f} | "
            f"{aggregate['candidate_state_profile']['f1']:.4f} | "
            f"{transitions.get('wrong_to_correct', 0)} | "
            f"{transitions.get('correct_to_wrong', 0)} |"
        )

    lines.extend(
        [
            "",
            (
                "The comparator is the model's structured output after schema and "
                "evidence validation."
            ),
            (
                "The final stage adds the named deterministic Seizure Frequency "
                "projection and suppression path."
            ),
            "",
            "## Component evidence",
            "",
            (
                "| Model | Over-reads rescued | Introduced | Persistent | "
                "Changed-still-wrong | Exact final evidence | SF parse/schema failures |"
            ),
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for model in models:
        aggregate = model["aggregate"]
        overread = aggregate["primary_overread_transitions"]
        transitions = aggregate["correctness_transitions"]
        lines.append(
            f"| {model['model']} | {overread.get('overread_rescued', 0)} | "
            f"{overread.get('overread_introduced', 0)} | "
            f"{overread.get('persistent_overread', 0)} | "
            f"{transitions.get('changed_still_wrong', 0)} | "
            f"{_rate(aggregate['candidate_exact_evidence_rate'])} | "
            f"{aggregate['final_sf_parse_schema_failures']} |"
        )

    lines.extend(
        [
            "",
            (
                "Every state-changing row is attributed to "
                "`deterministic_sf_projection_or_suppression`;"
            ),
            "unchanged rows remain model-selected facts passing through the final adapter. ",
            "Exact evidence means source-text presence, not independent clinical confirmation.",
            "",
            "## Gold-band diagnostics",
            "",
            (
                "Empty-gold rows remain separate because missing annotation is not proof "
                "that a supported prediction is false."
            ),
            ("The following counts are diagnostics, not factuality prevalence estimates."),
            "",
            (
                "| Model | Empty-gold active-rate | Seizure-free-band active-rate | "
                "Changed-only active-rate |"
            ),
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for model in models:
        bands = model["aggregate"]["gold_bands"]
        lines.append(
            f"| {model['model']} | "
            f"{bands.get('empty_gold', {}).get('candidate_active_rate', 0)}/"
            f"{bands.get('empty_gold', {}).get('letters', 0)} | "
            f"{bands.get('seizure_free_containing', {}).get('candidate_active_rate', 0)}/"
            f"{bands.get('seizure_free_containing', {}).get('letters', 0)} | "
            f"{bands.get('changed_only', {}).get('candidate_active_rate', 0)}/"
            f"{bands.get('changed_only', {}).get('letters', 0)} |"
        )

    primary_examples: list[tuple[str, Mapping[str, Any]]] = []
    correctness_examples: list[tuple[str, Mapping[str, Any]]] = []
    for model in models:
        for row in model["rows"]:
            if row["overread_transition"] in {
                "overread_rescued",
                "overread_introduced",
                "persistent_overread",
            }:
                primary_examples.append((str(model["model"]), row))
            if row["correctness_transition"] in {"wrong_to_correct", "correct_to_wrong"}:
                correctness_examples.append((str(model["model"]), row))
    lines.extend(["", "## Permitted development examples", ""])
    if primary_examples:
        for model_name, row in primary_examples[:4]:
            evidence = (row["candidate_evidence"] or row["comparator_evidence"] or [""])[0]
            lines.append(
                f"- `{row['letter_id']}` / {model_name}: `{row['overread_transition']}`; "
                f"gold `{row['gold_states']}`, comparator `{row['comparator_states']}`, "
                f"final `{row['candidate_states']}`; evidence: “{evidence}”"
            )
    else:
        lines.append(
            "No primary-band over-read example exists because the gold unknown-only "
            "denominator is empty. Component-transition examples remain available:"
        )
    for model_name, row in correctness_examples[:6]:
        evidence = (row["candidate_evidence"] or row["comparator_evidence"] or [""])[0]
        lines.append(
            f"- `{row['letter_id']}` / {model_name}: `{row['correctness_transition']}`; "
            f"gold `{row['gold_states']}`, comparator `{row['comparator_states']}`, "
            f"final `{row['candidate_states']}`; evidence: “{evidence}”"
        )

    lines.extend(
        [
            "",
            "## Interpretation and claim boundary",
            "",
            (
                "This study measures an ExECT-specific analogue of unknown-versus-rate "
                "behavior. It does not prove that the Gan mechanism transfers, because "
                "Gan uses one exhaustive label per note while ExECT permits multiple "
                "mentions and has documented annotation omissions and conventions."
            ),
            "",
            str(payload["claim_boundary"]),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    payload = build_payload()
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUTPUT_REPORT.write_text(render_report(payload), encoding="utf-8")


if __name__ == "__main__":
    main()
