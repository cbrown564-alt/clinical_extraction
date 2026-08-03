"""Compare DeepSeek V4-Flash-0731 llm_only validation750 to the 2026-07-18 cell.

Reads aggregate Markdown only (no sealed holdout rows). Writes a compact JSON
diff under experiments/.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIOR_REPORT = ROOT / (
    "scratch/validation/gan2026_six_model_comparison_20260718/"
    "deepseek_v4_flash/llm_only/validation750.report.md"
)
UPDATE_REPORT = ROOT / (
    "scratch/validation/gan2026_validation750_deepseek_v4_flash_0731_20260803/"
    "llm_only/aggregate.md"
)
OUT = ROOT / "experiments/gan2026_deepseek_v4_flash_0731_llm_only_validation750_vs_20260718.json"

_PURIST = re.compile(
    r"Purist .+?: (?P<acc>0\.\d+) \((?P<correct>\d+) / (?P<total>\d+)\)"
)
_PRAG = re.compile(
    r"Pragmatic .+?: (?P<acc>0\.\d+) \((?P<correct>\d+) / (?P<total>\d+)\)"
)
_CALLS = re.compile(r"Call failures: (?P<n>\d+)")
_PARSE = re.compile(r"Parse/schema/label issues: (?P<n>\d+)")


def _parse(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    purist = _PURIST.search(text)
    prag = _PRAG.search(text)
    if not purist or not prag:
        raise ValueError(f"Could not parse Purist/Pragmatic from {path}")
    calls = _CALLS.search(text)
    parse = _PARSE.search(text)
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "purist_accuracy": float(purist.group("acc")),
        "purist_correct": int(purist.group("correct")),
        "rows": int(purist.group("total")),
        "pragmatic_accuracy": float(prag.group("acc")),
        "pragmatic_correct": int(prag.group("correct")),
        "call_failures": int(calls.group("n")) if calls else None,
        "parse_or_validation_failures": int(parse.group("n")) if parse else None,
    }


def main() -> None:
    if not UPDATE_REPORT.exists():
        raise SystemExit(f"Update aggregate missing: {UPDATE_REPORT}")
    prior = _parse(PRIOR_REPORT)
    update = _parse(UPDATE_REPORT)
    payload = {
        "schema_version": "gan2026.deepseek_v4_flash_0731_llm_only_validation750_vs_20260718.v1",
        "study": "gan2026_deepseek_v4_flash_0731_llm_only_validation750",
        "prompt_version": "gan2026_llm_only_canonical_pipeline_v0.8",
        "split": "validation750",
        "model": "deepseek/deepseek-v4-flash",
        "provider_revision": "DeepSeek-V4-Flash-0731",
        "prior": prior,
        "update_0731": update,
        "delta": {
            "purist_correct": update["purist_correct"] - prior["purist_correct"],
            "purist_accuracy": round(
                update["purist_accuracy"] - prior["purist_accuracy"], 4
            ),
            "pragmatic_correct": update["pragmatic_correct"] - prior["pragmatic_correct"],
            "pragmatic_accuracy": round(
                update["pragmatic_accuracy"] - prior["pragmatic_accuracy"], 4
            ),
        },
        "claim_boundary": (
            "Provider-update development evidence for Gan llm_only validation750. "
            "Not a v0.5 llm_with_rules panel replacement or holdout claim."
        ),
        "protocol": (
            "docs/experiments/gan2026/"
            "gan2026_deepseek_v4_flash_0731_llm_only_validation750_protocol_2026-08-03.md"
        ),
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["delta"], indent=2))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
