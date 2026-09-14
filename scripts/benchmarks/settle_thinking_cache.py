"""Tighten completed-call cost bounds using returned cache usage; never alter responses."""

from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)


def main() -> None:
    path = study.ROOT / "attempts.jsonl"
    events = study.old.read_lines(path)
    started = {e["request_id"] for e in events if e["state"] == "started"}
    finished = {e["request_id"] for e in events if e["state"] == "finished"}
    if started != finished:
        raise ValueError("Wait for the runner to finish; calls are still outstanding")
    latest = {e["request_id"]: e for e in events}
    before = study.old.charged(events)
    count = 0
    for event in latest.values():
        if event["state"] != "finished":
            continue
        usage = event.get("usage") or {}
        hit = usage.get("prompt_cache_hit_tokens")
        miss = usage.get("prompt_cache_miss_tokens")
        completion = usage.get("completion_tokens")
        if not all(type(v) is int and v >= 0 for v in (hit, miss, completion)):
            continue
        if hit + miss != usage.get("prompt_tokens"):
            continue
        # Published peak prices; no off-peak discount assumed.
        charge = (hit * 0.006 + miss * 0.30 + completion * 1.20) / 1_000_000
        if charge > event["charged_upper_usd"]:
            raise ValueError("New bound must not exceed original reservation")
        study.old.append(
            path,
            {
                **event,
                "state": "cache_price_settled",
                "charged_upper_usd": charge,
                "original_charged_upper_usd": event["charged_upper_usd"],
                "accounting": "peak cache-hit .006, cache-miss .30, output 1.20 per million",
                "pricing_url": "https://api-docs.deepseek.com/quick_start/pricing/",
            },
        )
        count += 1
    after = study.old.charged(study.old.read_lines(path))
    report = {
        "settled_calls": count,
        "prior_bound": before,
        "revised_bound": after,
        "released_usd": before - after,
        "unknown_usage": "full original reservation retained",
    }
    study.old.append(study.ROOT / "cache_settlements.jsonl", report)
    print(report)


if __name__ == "__main__":
    main()
