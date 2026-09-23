"""Offline fictional Jev/LLM comparison. No network, corpus access or semantic repair."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "examples/jev_comparison"
VERSION = "jev_candidate_comparison_v1"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def question(instructions, criteria):
    return {"type": "choice", "instructions": instructions, "criteria": criteria}


def prepare(source, model, omitted=()):
    # All sentences are candidates; no clinical filtering and no access to gold.
    text = source["text"]
    candidates = []
    for i, match in enumerate(re.finditer(r"[^\n]+", text)):
        if f"s{i}" not in omitted:
            candidates.append(
                {"id": f"s{i}", "text": match[0], "start": match.start(), "end": match.end()}
            )
    choices = {c["id"]: c["text"] for c in candidates}
    choices.update(
        no_current="The letter does not establish a current seizure burden.",
        unsupported="Current burden exists but the candidates cannot represent it.",
        ambiguous="Several incompatible or complementary candidates prevent a single selection.",
    )
    questions = {
        "primary": question(
            "Read the entire letter. Select the candidate best representing the patient's current "
            "epileptic seizure burden. Exclude superseded history, future thresholds, treatment "
            "and other people. Do not replace positive burden with absence between episodes. "
            "Use unsupported when evidence is missing from candidates; use ambiguous when a "
            "single candidate cannot faithfully represent the burden.",
            choices,
        )
    }
    for c in candidates:
        prefix = f"For candidate {c['id']} ({c['text']}) in the context of the entire letter: "
        quantities = {
            f"v{i}": m[0]
            for i, m in enumerate(
                re.finditer(r"\b\d+(?:\.\d+)?(?:[-–]\d+(?:\.\d+)?)?\b", c["text"])
            )
        }
        quantities.update(
            not_established="Relevant quantity is not stated or cannot be represented.",
            not_applicable="This quantity does not apply to this candidate.",
        )
        questions[c["id"] + ".role"] = question(
            prefix + "Classify its clinical role.",
            {
                "current": "Describes the patient's present or ongoing epileptic seizure burden.",
                "historical": (
                    "Describes an earlier epileptic seizure burden, superseded or historical."
                ),
                "future": "A prospective or conditional statement, not observed current burden.",
                "other": (
                    "Treatment, another person, non-epileptic events or unrelated information."
                ),
                "unknown": (
                    "The clinical role or current epileptic seizure burden is not established."
                ),
            },
        )
        questions[c["id"] + ".structure"] = question(
            prefix + "Classify the measurement structure.",
            {
                "rate": "Individual seizure events recur per stated time denominator.",
                "count": (
                    "Finite observed events in an observation window; recurrence is not asserted."
                ),
                "cluster": (
                    "Grouped seizure episodes distinguish group recurrence from individual events."
                ),
                "seizure_free": (
                    "Absence of the relevant seizures over a stated interval or anchor."
                ),
                "qualitative": "Seizure frequency expressed without a numerical measurement.",
                "unsupported": "No supported measurement in these categories.",
            },
        )
        questions[c["id"] + ".outer_value"] = question(
            prefix
            + "Select the exact source quantity for individual event recurrence, group recurrence "
            "or observed event count. Do not select a duration, dose or within-group count. "
            "Use not_applicable for seizure freedom or non-seizure statements.",
            quantities,
        )
        questions[c["id"] + ".inner_value"] = question(
            prefix + "Select the exact source quantity of individual seizures within a group. "
            "Use not_applicable when there is no grouped seizure measurement.",
            quantities,
        )
        questions[c["id"] + ".denominator"] = question(
            prefix + "Identify the recurring denominator for the outer event or group rate. "
            "An observation window alone does not establish recurrence.",
            {
                "day": "Recurrence per day.",
                "week": "Recurrence per week.",
                "month": "Recurrence per month.",
                "year": "Recurrence per year.",
                "not_established": "A relevant recurring denominator is absent or unrepresentable.",
                "not_applicable": "The measurement is not a recurring rate or group rate.",
            },
        )
    common = {"state": text, "questions": questions}
    return {
        "id": source["id"],
        "version": VERSION,
        "source_sha256": digest(text),
        "request_sha256": digest(common),
        "candidates": candidates,
        "jev": {"model": model, **common},
        "llm": {
            "messages": [
                {
                    "role": "system",
                    "content": "Answer each Choice question against the supplied state. "
                    "Return only a JSON object mapping each question ID to one allowed option key. "
                    "Questions are independent; do not assume access to another answer.",
                },
                {"role": "user", "content": json.dumps(common, ensure_ascii=False)},
            ]
        },
        "policy": {
            "dataset": "fictional_jev_v1",
            "split": "fictional-development",
            "row_policy": "all fixtures including missing outputs",
            "repair": "none",
            "native_gan_scoring": False,
        },
    }


def expected(pack, gold):
    answers = {"primary": gold["primary"]}
    questions = pack["jev"]["questions"]
    for c in pack["candidates"]:
        answers[c["id"] + ".role"] = gold["roles"][int(c["id"][1:])]
    if gold["primary"] not in {c["id"] for c in pack["candidates"]}:
        if gold["primary"].startswith("s"):
            answers["primary"] = "unsupported"
        return answers
    for field, value in gold["selected"].items():
        qid = gold["primary"] + "." + field
        options = questions[qid]["criteria"]
        if value in options:
            answers[qid] = value
        else:
            answers[qid] = next(k for k, v in options.items() if v == value)
    return answers


def score(pack, gold, response):
    # Accept raw Jev response or the LLM's decoded mapping, without fixing outputs.
    supplied = response.get("answers", response) if isinstance(response, dict) else {}
    if not isinstance(supplied, dict):
        supplied = {}
    expected_answers = expected(pack, gold)
    diagnostics = {}
    for qid, target in expected_answers.items():
        answer = supplied.get(qid)
        choice = answer.get("choice") if isinstance(answer, dict) else answer
        valid = isinstance(choice, str) and choice in pack["jev"]["questions"][qid]["criteria"]
        diagnostics[qid] = {
            "expected": target,
            "choice": choice,
            "valid": valid,
            "correct": valid and choice == target,
        }
    final_ids = ["primary"] + [
        k
        for k in expected_answers
        if k.startswith(gold["primary"] + ".") and not k.endswith(".role")
    ]
    return {
        "id": pack["id"],
        "correct": sum(d["correct"] for d in diagnostics.values()),
        "total": len(diagnostics),
        "missing_or_invalid": sum(not d["valid"] for d in diagnostics.values()),
        "final_selection_and_attributes_correct": all(diagnostics[k]["correct"] for k in final_ids),
        "diagnostics": diagnostics,
    }


def build(model):
    sources = json.loads((FIXTURES / "sources.json").read_text())
    packs = [prepare(s, model) for s in sources]
    omitted = prepare(sources[0], model, omitted=("s1",))
    omitted["id"] = "cluster_missing_candidate"
    packs.append(omitted)
    return packs


def check(packs, gold):
    checks = []
    for pack in packs:
        reference = gold["cluster" if pack["id"] == "cluster_missing_candidate" else pack["id"]]
        key = expected(pack, reference)
        assert score(pack, reference, key)["correct"] == len(key)
        assert score(pack, reference, {})["correct"] == 0
        assert score(pack, reference, {})["total"] == len(key)
        assert score(pack, reference, {"answers": None})["correct"] == 0
        bad = dict(key, primary="invented_option")
        assert not score(pack, reference, bad)["final_selection_and_attributes_correct"]
        jev = {"answers": {k: {"choice": v} for k, v in key.items()}}
        assert score(pack, reference, jev)["correct"] == len(key)
        llm_input = json.loads(pack["llm"]["messages"][1]["content"])
        assert llm_input == {k: pack["jev"][k] for k in ("state", "questions")}
        for c in pack["candidates"]:
            assert pack["jev"]["state"][c["start"] : c["end"]] == c["text"]
        checks.append({"id": pack["id"], "scored_questions": len(key), "offline_checks": "passed"})
    omitted_key = expected(packs[-1], gold["cluster"])
    assert omitted_key["primary"] == "unsupported"
    # Wrong valid values and mixed-finding attributes must fail the final tuple.
    pack = packs[0]
    key = expected(pack, gold["cluster"])
    key["s1.inner_value"] = "v2"  # 24-hour duration incorrectly used as seizure count.
    assert not score(pack, gold["cluster"], key)["final_selection_and_attributes_correct"]
    assert build(packs[0]["jev"]["model"]) == packs
    return {
        "version": VERSION,
        "model_calls": 0,
        "performance_result": False,
        "checks": checks,
        "candidate_omission": "passed",
        "wrong_quantity_binding": "passed",
        "deterministic_rebuild": "passed",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "score"])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="jev-1.13.0")
    parser.add_argument(
        "--prepared", type=Path, help="Saved prepare directory; required for scoring"
    )
    parser.add_argument(
        "--responses",
        type=Path,
        help="JSON: fixture ID -> raw Jev response or decoded LLM choice mapping",
    )
    args = parser.parse_args()
    packs = build(args.model)
    gold = json.loads((FIXTURES / "gold.json").read_text())
    if args.command == "prepare":
        # Refuse overwrite so prepared requests remain attributable.
        verification = check(packs, gold)
        args.output.mkdir(parents=True, exist_ok=False)
        for pack in packs:
            (args.output / (pack["id"] + ".json")).write_text(json.dumps(pack, indent=2) + "\n")
        (args.output / "verification.json").write_text(json.dumps(verification, indent=2) + "\n")
        print(json.dumps(verification, indent=2))
    else:
        if args.responses is None or args.prepared is None:
            parser.error("--responses and --prepared are required for score")
        saved = [json.loads((args.prepared / (p["id"] + ".json")).read_text()) for p in packs]
        if saved != packs:
            parser.error("Saved requests differ from this builder/model; use the frozen version")
        packs = saved
        responses = json.loads(args.responses.read_text())
        rows = [
            score(
                p,
                gold["cluster" if p["id"] == "cluster_missing_candidate" else p["id"]],
                responses.get(p["id"], {}),
            )
            for p in packs
        ]
        report = {
            "version": VERSION,
            "response_sha256": digest(responses),
            "request_hashes": {p["id"]: p["request_sha256"] for p in packs},
            "gold_sha256": digest(gold),
            "repair": "none",
            "replay": "offline",
            "dataset": "fictional_jev_v1",
            "split": "fictional-development",
            "scorer": VERSION,
            "row_policy": "all seven fictional conditions",
            "provider_metadata": "Retain model/runtime/usage with original responses",
            "rows": rows,
            "correct": sum(r["correct"] for r in rows),
            "total": sum(r["total"] for r in rows),
        }
        with args.output.open("x") as stream:
            stream.write(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"correct": report["correct"], "total": report["total"]}))


if __name__ == "__main__":
    main()
