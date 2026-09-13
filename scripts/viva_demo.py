"""Build curated development demo records or replay their saved extraction locally.

No model calls, corpus loader, holdout access, or writes to research artifacts.
Run from the repository root using .venv/bin/python.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
from pathlib import Path

from clinical_extraction.tasks.shared.epilepsy.normalization import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredRepairConfig,
    parse_structured_json_with_trace,
)

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "frontend/lib/viva-data.json"
MODE = "llm_select_after_codebook"


def rule_snapshot(rule_id: str, function) -> dict:
    lines, start = inspect.getsourcelines(function)
    path = Path(inspect.getfile(function))
    return {
        "id": rule_id,
        "name": function.__name__,
        "source": "".join(lines),
        "path": str(path.relative_to(ROOT)),
        "line": start,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def rule_library() -> dict:
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        llm_structured_monthly_diary as diary,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        llm_structured_repair_families as families,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
        repair_prediction_label_format_preserving,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence import (
        codebook_encode,
    )

    encode = [rule_snapshot("gan.encode.format", repair_prediction_label_format_preserving)]
    encode.extend(
        rule_snapshot(rule.rule_id, rule.apply) for rule in codebook_encode._CODEBOOK_ENCODE_RULES
    )
    names = [
        ("usual_interval", "usual_interval_label_from_events"),
        ("typical_over_ytd", "typical_recurring_rate_over_ytd_from_events"),
        ("breakthrough", "breakthrough_label_from_events"),
        ("non_epileptic", "non_epileptic_label_from_events"),
        ("post_change_burst", "post_change_burst_label_from_events"),
        ("last_event_well_since", "last_event_well_since_label_from_events"),
        ("dated_sequence", "dated_sequence_label_from_events"),
    ]
    decide = [rule_snapshot(f"gan.select.{key}", getattr(families, name)) for key, name in names]
    decide.append(rule_snapshot("gan.select.monthly_diary", diary.monthly_diary_label_from_events))
    return {"encode": encode, "decide": decide}


def replay(raw: str) -> dict:
    # The decision executor receives the saved record only, never the letter.
    result, _, errors, trace = parse_structured_json_with_trace(
        raw, note_text=None, repair_config=StructuredRepairConfig.for_mode(MODE)
    )
    if result is None:
        raise ValueError(f"Cannot replay saved extraction: {errors}")
    return {
        "selection": result.selection.model_dump(),
        "hops": trace["answer_states"][1:],
        "repair_notes": errors,
    }


def rows(path: Path) -> dict:
    return {r["source_row_index"]: r for r in map(json.loads, path.read_text().splitlines())}


def build(ids: list[int]) -> None:
    base = ROOT / "results/letter-benchmarks/gan"
    source = ROOT / "experiments/paper/gan_llm_extract/gemini37flash/dev750/rows.jsonl"
    originals = rows(source)
    extracts = rows(base / "gan_llm_extract/gemini37flash/dev750/rows.jsonl")
    selected = rows(base / "gan_llm_select_from_extract/gemini37flash/dev750/rows.jsonl")
    decision_inputs = rows(
        ROOT / "experiments/paper/gan_llm_select_from_extract/gemini37flash/dev750/rows.jsonl"
    )
    scores = rows(base / "gan_llm_select_from_extract/gemini37flash/dev750/scored.jsonl")
    rungs = rows(base / "rungs/gemini37flash/dev750/scored.jsonl")
    ordered = sorted(extracts)
    batch_ids = [ordered[i * (len(ordered) - 1) // 24] for i in range(25)]
    cases = []
    prompt_templates = None
    for index in dict.fromkeys(ids + batch_ids):
        original, extract = originals[index], extracts[index]
        assert original["paper_split"] == "dev750"
        assert original["raw_output"] == extract["raw_output"]
        assert decision_inputs[index]["raw_output"] == selected[index]["raw_output"]
        note = json.loads(original["prompt_input_json"])["note_text"]
        extract_prompt = json.loads(original["prompt_input_json"])
        extract_prompt.pop("note_text")
        decide_prompt = json.loads(decision_inputs[index]["prompt_input_json"])
        decide_input = {key: decide_prompt.pop(key) for key in ("events", "first_choice")}
        templates = {"extract": extract_prompt, "decide": decide_prompt}
        if prompt_templates is None:
            prompt_templates = templates
        assert prompt_templates == templates, "Prompt version varies within demo records"
        parsed, _, errors, _ = parse_structured_json_with_trace(
            extract["raw_output"], repair_config=StructuredRepairConfig.for_mode("raw_model")
        )
        assert parsed is not None and not errors
        record = parsed.model_dump()
        for event in record["events"]:
            assert event["evidence"] and event["evidence"] in note, (index, event["event_id"])
        hybrid = replay(extract["raw_output"])
        expected = rungs[index]["rungs"]["llm_select"]
        assert hybrid["selection"]["final_label"] == expected["predicted_label"]
        raw_llm = selected[index]["raw_output"]
        llm = json.loads(raw_llm[raw_llm.index("{") : raw_llm.rindex("}") + 1])
        # The saved decision response echoes the same candidate IDs and quotes.
        assert [(e["event_id"], e["evidence"]) for e in llm["events"]] == [
            (e["event_id"], e["evidence"]) for e in record["events"]
        ]
        cases.append(
            {
                "id": index,
                "note": note,
                "record": record,
                "raw": extract["raw_output"],
                "hybrid": hybrid,
                "llm": {
                    "label": scores[index]["predicted_label"],
                    "selected_event_ids": llm["selection"]["selected_event_ids"],
                    "raw": raw_llm,
                    "purist_correct": scores[index]["purist_correct"],
                },
                "gold": rungs[index]["gold_label"],
                "hybrid_correct": expected["purist_correct"],
                "category": map_pragmatic(
                    label_to_frequency_record(hybrid["selection"]["final_label"]).monthly_frequency
                ),
                "source": str(source.relative_to(ROOT)),
                "extract_source": (
                    "results/letter-benchmarks/gan/gan_llm_extract/gemini37flash/dev750/rows.jsonl"
                ),
                "decision_source": (
                    "results/letter-benchmarks/gan/gan_llm_select_from_extract/"
                    "gemini37flash/dev750/rows.jsonl"
                ),
                "sha256": hashlib.sha256(extract["raw_output"].encode()).hexdigest(),
                "prompt_version": extract["prompt_version"],
            }
        )
        cases[-1]["decide_input"] = decide_input
    BUNDLE.write_text(
        json.dumps(
            {
                "dataset": "Gan 2026 synthetic",
                "split": "dev750",
                "model": "Gemini 3.7 Flash",
                "repair_mode": MODE,
                "guided_ids": ids,
                "batch_ids": batch_ids,
                "batch_policy": (
                    "25 evenly spaced positions in the sorted saved dev750 extraction IDs; "
                    "selected without reading outcomes."
                ),
                "cases": cases,
            },
            indent=2,
        )
        + "\n"
    )
    (ROOT / "frontend/lib/viva-method.json").write_text(
        json.dumps(
            {
                "prompts": prompt_templates,
                "rules": rule_library(),
                "note": (
                    "Saved prompt payloads from development runs. "
                    "Framework message wrappers are not included. "
                    "Rule source is a snapshot of the local program at export time."
                ),
            },
            indent=2,
        )
        + "\n"
    )
    print(f"Exported and checked {len(cases)} development cases.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", nargs="+", type=int)
    parser.add_argument("--decide", type=int)
    args = parser.parse_args()
    if args.build:
        build(args.build)
    elif args.decide is not None:
        bundle = json.loads(BUNDLE.read_text())
        case = next(c for c in bundle["cases"] if c["id"] == args.decide)
        print(
            json.dumps(
                {
                    "mode": "live_rules",
                    "id": case["id"],
                    "sha256": case["sha256"],
                    **replay(case["raw"]),
                }
            )
        )
    else:
        parser.error("Choose --build or --decide")
