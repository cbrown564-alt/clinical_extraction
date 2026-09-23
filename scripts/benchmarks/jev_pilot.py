"""Frozen fictional Jev/DeepSeek pilot; no benchmark-corpus access or output repair."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import httpx
from dotenv import dotenv_values

from scripts.benchmarks import prepare_jev_comparison as v1

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "results/letter-benchmarks/gan/jev_fictional_v2"
RUN = ROOT / "runs/jev_fictional_v2"
VERSION = "jev_candidate_comparison_v2"
BUDGET = 2.0
ENDPOINTS = {
    "jev": "https://api.typesafe.ai/v1/systemone",
    "deepseek": "https://api.deepseek.com/chat/completions",
    "review": "https://api.deepseek.com/chat/completions",
}
RATES = {"jev": (0.042, 0), "deepseek": (0.30, 1.20), "review": (1.32, 3.96)}


def now():
    return datetime.now(UTC).isoformat()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def sha(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cases():
    sources = read(v1.FIXTURES / "sources.json")
    keys = read(v1.FIXTURES / "gold.json")
    items = []
    for s in sources:
        items.append(
            {
                "id": s["id"],
                "group": "base",
                "source": s,
                "gold": copy.deepcopy(keys[s["id"]]),
                "omitted": [],
            }
        )
    omission = copy.deepcopy(items[0])
    omission.update(id="cluster_missing_candidate", omitted=["s1"])
    items.append(omission)
    for base, replacements, fields in [
        (
            "cluster",
            [("2 cluster", "5 cluster"), ("6 seizures", "11 seizures")],
            {"outer_value": "5", "inner_value": "11"},
        ),
        ("rate", [("3 seizures per week", "7 seizures per week")], {"outer_value": "7"}),
        ("count", [("3 isolated", "8 isolated")], {"outer_value": "8"}),
    ]:
        item = copy.deepcopy(next(x for x in items if x["id"] == base))
        item.update(id=base + "_quantities", group="quantities")
        for a, b in replacements:
            item["source"]["text"] = item["source"]["text"].replace(a, b)
        item["gold"]["selected"].update(fields)
        items.append(item)
    paraphrases = {
        "cluster": (
            "Earlier records described 9 seizures each week.\nThe present "
            "pattern consists of 2 days of grouped seizures every month, "
            "usually 6 seizures during 24 hours on each such day.\nNo seizures "
            "occur in the gaps between these grouped episodes.\nIf grouped "
            "seizure days rise above 3 monthly, call the clinic.\nThe "
            "prescribed dose is 500 mg twice daily."
        ),
        "rate": (
            "An older pattern was 8 seizures a day.\nThe ongoing pattern is 3 "
            "seizures every week.\nA rise above 5 seizures daily would prompt a"
            " medication increase to 200 mg."
        ),
        "count": (
            "The diary totals 3 isolated seizures during the 2 months since "
            "the preceding visit.\nThe prescription is unchanged at 100 mg "
            "daily."
        ),
        "qualitative": "Seizures remain frequent at present.\nThe daily medication dose is 100 mg.",
    }
    for base, text in paraphrases.items():
        item = copy.deepcopy(next(x for x in items if x["id"] == base))
        item.update(id=base + "_paraphrase", group="paraphrase")
        item["source"]["text"] = text
        items.append(item)
    items.append(
        {
            "id": "competing_current",
            "group": "competing",
            "omitted": [],
            "source": {
                "id": "competing_current",
                "text": "Currently focal aware seizures occur 2 times per week.\n"
                "Currently tonic-clonic seizures occur 1 time per month.\n"
                "Medication is 200 mg daily.",
            },
            "gold": {"primary": "ambiguous", "roles": ["current", "current", "other"]},
        }
    )
    for original in list(items[:7]):
        item = copy.deepcopy(original)
        item.update(id=original["id"] + "_reordered", group="order", reverse=True)
        items.append(item)
    return items


def pack_case(item):
    pack = v1.prepare(item["source"], "jev-1.13.0", item["omitted"])
    pack.update(id=item["id"], version=VERSION, group=item["group"])
    questions = pack["jev"]["questions"]
    for qid, q in questions.items():
        if qid.endswith(".denominator"):
            q["criteria"]["not_established"] = (
                "A rate, grouped rate or qualitative frequency is described but its "
                "recurring denominator is absent or outside the listed units."
            )
            q["criteria"]["not_applicable"] = (
                "An observed count, seizure-free interval or non-frequency statement "
                "does not require a recurring denominator."
            )
    if item.get("reverse"):
        pack["candidates"].reverse()
        questions = dict(reversed(list(questions.items())))
        for q in questions.values():
            q["criteria"] = dict(reversed(list(q["criteria"].items())))
        pack["jev"]["questions"] = questions
    common = {k: pack["jev"][k] for k in ("state", "questions")}
    pack["llm"]["messages"][1]["content"] = json.dumps(common, ensure_ascii=False)
    pack["request_sha256"] = sha(common)
    pack["policy"]["dataset"] = "fictional_jev_v2"
    return pack


def llm_body(messages, review=False):
    return {
        "model": "deepseek-v4-pro" if review else "deepseek-flash",
        "messages": messages,
        "temperature": 0,
        "max_tokens": 24000,
        "thinking": {"type": "enabled"},
        "reasoning_effort": "low",
        "response_format": {"type": "json_object"},
    }


def reservation(provider, body):
    # Byte bound plus framing allowance; output limit includes thinking tokens.
    inp, out = RATES[provider]
    input_bound = len(json.dumps(body, ensure_ascii=False).encode()) + 4096
    return (input_bound * inp + body.get("max_tokens", 0) * out) / 1_000_000


def attempt(provider, rid, body):
    RUN.mkdir(parents=True, exist_ok=True)
    path = RUN / provider / (rid + ".json")
    started = path.with_suffix(".started.json")
    if path.exists():
        saved = read(path)
        if saved["request_hash"] != sha(body):
            raise ValueError("Refusing changed request under an existing attempt ID")
        return saved
    if started.exists():
        raise ValueError("Attempt already started without completion; do not retry automatically")
    settings = dotenv_values(ROOT / ".env")
    names = ["TYPESAFE_API_KEY", "JEV_API_KEY"] if provider == "jev" else ["DEEPSEEK_API_KEY"]
    key = next(
        (os.getenv(n) or settings.get(n) for n in names if os.getenv(n) or settings.get(n)), None
    )
    if not key:
        raise ValueError("API key unavailable for " + provider)
    spent = sum(read(p)["reservation_usd"] for p in RUN.glob("*/*.started.json"))
    reserve = reservation(provider, body)
    if spent + reserve > BUDGET:
        raise ValueError("Pilot US$2 reservation cap exceeded")
    write(
        started,
        {
            "started_at": now(),
            "request_hash": sha(body),
            "reservation_usd": reserve,
            "provider": provider,
            "request": body,
        },
    )
    t = time.monotonic()
    record = {
        "provider": provider,
        "id": rid,
        "request_hash": sha(body),
        "reservation_usd": reserve,
        "raw_response": None,
        "error": None,
    }
    try:
        with httpx.Client(timeout=600, follow_redirects=False) as client:
            response = client.post(
                ENDPOINTS[provider], json=body, headers={"Authorization": "Bearer " + key}
            )
        record.update(http_status=response.status_code, raw_text=response.text)
        try:
            record["raw_response"] = response.json()
        except ValueError:
            record["error"] = "non_json_http_response"
        if response.status_code != 200:
            record["error"] = "http_" + str(response.status_code)
    except httpx.HTTPError as exc:
        # Exception type only: never persist request headers or credentials.
        record["error"] = type(exc).__name__
    record.update(elapsed_seconds=time.monotonic() - t, finished_at=now())
    raw = record["raw_response"] or {}
    usage = raw.get("usage", {})
    record.update(returned_model=raw.get("model"), usage=usage)
    it = usage.get("input_tokens" if provider == "jev" else "prompt_tokens")
    ot = usage.get("output_tokens" if provider == "jev" else "completion_tokens")
    record["peak_charge_upper_usd"] = (
        (it * RATES[provider][0] + ot * RATES[provider][1]) / 1_000_000
        if isinstance(it, int) and isinstance(ot, int)
        else reserve
    )
    write(path, record)
    print(
        json.dumps(
            {
                "provider": provider,
                "id": rid,
                "error": record["error"],
                "seconds": round(record["elapsed_seconds"], 2),
            }
        ),
        flush=True,
    )
    return record


def review():
    # Different model and fresh context; no expected answers or comparison outputs.
    unique = [x for x in cases() if x["group"] != "order" and not x["omitted"]]
    payload = []
    for item in unique:
        pack = pack_case(item)
        payload.append(
            {"id": item["id"], "state": pack["jev"]["state"], "candidates": pack["candidates"]}
        )
    task = """Independently annotate these invented clinical snippets before an experiment.
You are not evaluating another model. No proposed gold or predictions are supplied.
For each case output primary: candidate ID best representing current epileptic burden,
no_current if no current burden is established, or ambiguous if multiple complementary
current seizure types cannot be faithfully represented by one candidate. Exclude treatment,
future conditions and superseded history. Seizure freedom between clusters does not
replace positive overall burden. Classify every sentence role in source order as current,
historical, future, other (treatment/other people/non-epileptic), or unknown.
When primary is a candidate, supply selected with structure (rate, count, cluster,
seizure_free, qualitative, unsupported), outer_value (literal source quantity for
individual recurrence, group recurrence or observed count; not_applicable for freedom;
not_established for qualitative), inner_value (literal individual seizures per group,
not_established if grouped but unstated, not_applicable if not grouped), denominator
(day/week/month/year for outer recurrence; not_applicable for count/freedom/non-frequency;
not_established for qualitative or a rate without a listed denominator).
Do not turn observation windows into rates. Preserve cluster days separately from
individual seizures. Return JSON {"cases": {id: {primary, roles, selected (if applicable),
"rationale": concise source-grounded explanation}}, "ambiguities": [any problems]}.
This is provisional fixture review, not clinical validation."""
    body = llm_body(
        [{"role": "system", "content": task}, {"role": "user", "content": json.dumps(payload)}],
        review=True,
    )
    return attempt("review", "source_only", body)


def decode(record, provider):
    if record.get("error") or record.get("http_status") != 200:
        return {}, record.get("error") or "http_failure"
    raw = record.get("raw_response") or {}
    if provider == "jev":
        return raw, None
    try:
        choice = raw["choices"][0]
        if choice["finish_reason"] != "stop":
            return {}, "finish_" + str(choice["finish_reason"])
        payload = json.loads(choice["message"]["content"])
        if not isinstance(payload, dict):
            return {}, "non_object_output"
        return payload, None
    except (KeyError, IndexError, ValueError, TypeError):
        return {}, "invalid_json_output"


def freeze():
    items = cases()
    reviewed, error = decode(read(RUN / "review/source_only.json"), "review")
    if error:
        raise ValueError("Source-only review failed: " + error)
    agreements = []
    for item in items:
        if item["group"] == "order" or item["omitted"]:
            continue
        proposed = reviewed["cases"][item["id"]]
        actual = {k: proposed[k] for k in ("primary", "roles", "selected") if k in proposed}
        agreements.append(
            {
                "id": item["id"],
                "agree": actual == item["gold"],
                "proposed": actual,
                "author_key": item["gold"],
                "rationale": proposed.get("rationale"),
            }
        )
    write(
        ART / "review_comparison.json",
        {
            "reviewer": "deepseek-v4-pro",
            "review_response_sha256": file_sha(RUN / "review/source_only.json"),
            "independence": "fresh source-only context, no author key or evaluation outputs",
            "cases": agreements,
            "ambiguities": reviewed.get("ambiguities", []),
        },
    )
    if not all(x["agree"] for x in agreements):
        raise ValueError("Review disagreement: adjudicate before freeze")
    packs = [pack_case(item) for item in items]
    for pack, item in zip(packs, items, strict=True):
        key = v1.expected(pack, item["gold"])
        assert v1.score(pack, item["gold"], key)["correct"] == len(key)
        assert v1.score(pack, item["gold"], {})["correct"] == 0
        assert json.loads(pack["llm"]["messages"][1]["content"]) == {
            k: pack["jev"][k] for k in ("state", "questions")
        }
    bodies = []
    for pack in packs:
        bodies.extend(
            [
                {"provider": "jev", "id": pack["id"], "body": pack["jev"]},
                {
                    "provider": "deepseek",
                    "id": pack["id"],
                    "body": llm_body(pack["llm"]["messages"]),
                },
            ]
        )
    total_reserve = sum(reservation(b["provider"], b["body"]) for b in bodies)
    review_reserve = read(RUN / "review/source_only.started.json")["reservation_usd"]
    if total_reserve + review_reserve > BUDGET:
        raise ValueError("Full run reservation exceeds US$2 cap")
    write(ART / "cases.json", items)
    write(ART / "packs.json", packs)
    write(ART / "requests.json", bodies)
    tracked = [
        Path(__file__).resolve(),
        Path(v1.__file__).resolve(),
        ART / "cases.json",
        ART / "packs.json",
        ART / "requests.json",
        ART / "review_comparison.json",
    ]
    write(
        ART / "freeze.json",
        {
            "version": VERSION,
            "frozen_at": now(),
            "dataset": "fictional_jev_v2",
            "split": "fictional-development",
            "row_policy": "all 22 conditions, failures wrong",
            "cases": len(items),
            "scored_decisions": sum(
                len(v1.expected(p, i["gold"])) for p, i in zip(packs, items, strict=True)
            ),
            "budget_usd": BUDGET,
            "full_reservation_usd": total_reserve + review_reserve,
            "retry_policy": "one attempt per provider/case, no automatic retries",
            "repair_policy": "none",
            "timeout_seconds": 600,
            "concurrency": 1,
            "prices_per_million_peak": RATES,
            "price_sources": [
                "https://docs.typesafe.ai/models",
                "https://api-docs.deepseek.com/quick_start/pricing/",
            ],
            "models": {
                "jev": "jev-1.13.0",
                "deepseek": "deepseek-flash",
                "review": "deepseek-v4-pro",
            },
            "model_limit": (
                "DeepSeek alias version recorded on response; no immutable checkpoint guarantee"
            ),
            "go_decision": "No automatic dev750 run. Inspect binding, abstention and robustness "
            "errors; if recurring semantic failures remain, revise on fictional data first. "
            "Even a clean pilot requires reviewed reference, "
            "candidate coverage and native mapping.",
            "files": {str(p.relative_to(ROOT)): file_sha(p) for p in tracked},
        },
    )
    print(json.dumps(read(ART / "freeze.json"), indent=2))


def verify_freeze():
    freeze = read(ART / "freeze.json")
    for path, value in freeze["files"].items():
        if file_sha(ROOT / path) != value:
            raise ValueError("Frozen file changed: " + path)
    return freeze


def run(provider):
    verify_freeze()
    for job in read(ART / "requests.json"):
        if job["provider"] != provider:
            continue
        record = attempt(provider, job["id"], job["body"])
        if record.get("http_status") in (400, 401, 402, 403, 404, 422):
            raise ValueError("Provider rejected request; stopping without retries")


def report():
    freeze = verify_freeze()
    packs, items = read(ART / "packs.json"), read(ART / "cases.json")
    result = {"freeze_sha256": file_sha(ART / "freeze.json"), "freeze": freeze, "providers": {}}
    for provider in ("jev", "deepseek"):
        rows, charges, elapsed, models = [], [], [], set()
        for pack, item in zip(packs, items, strict=True):
            path = RUN / provider / (pack["id"] + ".json")
            record = read(path) if path.exists() else {"error": "not_run"}
            payload, error = decode(record, provider)
            row = v1.score(pack, item["gold"], payload)
            row.update(
                group=item["group"],
                failure=error,
                raw_response_sha256=file_sha(path) if path.exists() else None,
            )
            rows.append(row)
            if path.exists():
                charges.append(record["peak_charge_upper_usd"])
                elapsed.append(record["elapsed_seconds"])
                models.add(str(record.get("returned_model")))
        groups = defaultdict(
            lambda: {
                "selection_correct": 0,
                "complete_correct": 0,
                "correct": 0,
                "total": 0,
                "cases": 0,
            }
        )
        fields = defaultdict(lambda: {"correct": 0, "total": 0})
        for row in rows:
            for group in ("all", row["group"]):
                bucket = groups[group]
                bucket["cases"] += 1
                bucket["selection_correct"] += row["diagnostics"]["primary"]["correct"]
                bucket["complete_correct"] += row["final_selection_and_attributes_correct"]
                bucket["correct"] += row["correct"]
                bucket["total"] += row["total"]
            for qid, d in row["diagnostics"].items():
                field = qid.rsplit(".", 1)[-1]
                fields[field]["total"] += 1
                fields[field]["correct"] += d["correct"]
        result["providers"][provider] = {
            "groups": dict(groups),
            "fields": dict(fields),
            "rows": rows,
            "attempts": len(elapsed),
            "failures": sum(bool(r["failure"]) for r in rows),
            "charge_peak_upper_usd": sum(charges),
            "total_seconds": sum(elapsed),
            "mean_seconds": sum(elapsed) / len(elapsed) if elapsed else None,
            "returned_models": sorted(models),
        }
    # Reports are derived; raw attempts and frozen inputs stay immutable.
    print(json.dumps(result, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["review", "freeze", "run", "report"])
    p.add_argument("--provider", choices=["jev", "deepseek"])
    args = p.parse_args()
    if args.command == "review":
        review()
    elif args.command == "freeze":
        freeze()
    elif args.command == "run":
        if not args.provider:
            p.error("--provider required")
        run(args.provider)
    else:
        report()


if __name__ == "__main__":
    main()
