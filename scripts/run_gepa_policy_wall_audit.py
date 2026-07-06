"""Item 7 — GEPA policy-wall audit (zero LLM).

Static analysis of all evolved GEPA seed instructions against dspy's rejected
G30 policy-wall threshold (14,639 chars). dspy rejected G30 GEPA specifically
because its accepted instruction ballooned to 14,639 characters and was gated
behind compact-delta/latency/no-overlap criteria.

For every ``experiments/*.instruction.txt``:
- char count
- tiktoken ``cl100k_base`` token count (the GPT-4 family encoding)
- the repo's own ``approx_tokens`` estimate (~4 chars/token), for consistency
  with ``final_instruction_tokens``
- a heuristic policy-clause count (numbered/lettered list items + lines that
  read as imperatives: start with a verb, end with a period)

Flags any file >= 14,639 chars. The overfit-cue diagnosis is done by hand on
the over-threshold files and written into the audit note.

Also measures the un-evolved baselines (the ``FROM_SCRATCH_SEED_INSTRUCTION``
and sibling seed constants) for comparison.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import tiktoken

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program import (
    FROM_SCRATCH_SEED_INSTRUCTION as EXECTV2_FROM_SCRATCH_SEED,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_sf_verify import (
    GENERATE_SEED as SF_VERIFY_GENERATE_SEED,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_sf_verify import (
    VERIFY_SEED as SF_VERIFY_VERIFY_SEED,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.gepa.program import (
    FROM_SCRATCH_SEED_INSTRUCTION as GAN2026_FROM_SCRATCH_SEED,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
DSPY_POLICY_WALL_CHARS = 14_639


def _approx_tokens(text: str) -> int:
    """Repo's own char-based estimate (~4 chars/token), matching final_instruction_tokens."""
    return (len(text) + 3) // 4


# Heuristic policy-clause counter: numbered/lettered list items, or lines that
# read as imperatives (a leading verb word, capitalized or not, ending with a
# period or colon). Coarse by design — this is a relative-comparison signal,
# not a parse.
_NUMBERED = re.compile(r"^\s*(?:\d+[.)]|\(?[a-z][.)]|[A-Z][.)]|[-*•]\s)", re.MULTILINE)
_IMPERATIVE_VERBS = {
    "use", "return", "do", "never", "always", "if", "when", "ensure", "match",
    "extract", "select", "include", "exclude", "prefer", "avoid", "combine",
    "read", "write", "list", "provide", "check", "treat", "map", "assign",
    "state", "describe", "report", "keep", "skip", "fire", "only", "for",
}
_SENTENCE = re.compile(r"[^.!?\n]+[.!?]")


def _policy_clause_count(text: str) -> int:
    n = len(_NUMBERED.findall(text))
    for s in _SENTENCE.findall(text):
        first = s.strip().split()[0].lower().rstrip(",;:") if s.strip() else ""
        if first in _IMPERATIVE_VERBS:
            n += 1
    return n


def _measure(name: str, text: str, enc: tiktoken.Encoding) -> dict:
    return {
        "name": name,
        "chars": len(text),
        "tiktoken_tokens": len(enc.encode(text)),
        "approx_tokens": _approx_tokens(text),
        "policy_clauses": _policy_clause_count(text),
        "exceeds_dspy_wall": len(text) >= DSPY_POLICY_WALL_CHARS,
    }


def main() -> None:
    enc = tiktoken.get_encoding("cl100k_base")

    evolved = []
    for p in sorted(EXPERIMENTS.glob("*.instruction.txt")):
        text = p.read_text(encoding="utf-8")
        m = _measure(p.name, text, enc)
        m["path"] = str(p.relative_to(ROOT))
        evolved.append(m)

    baselines = [
        _measure("EXECTV2 FROM_SCRATCH_SEED_INSTRUCTION", EXECTV2_FROM_SCRATCH_SEED, enc),
        _measure("SF_VERIFY GENERATE_SEED", SF_VERIFY_GENERATE_SEED, enc),
        _measure("SF_VERIFY VERIFY_SEED", SF_VERIFY_VERIFY_SEED, enc),
        _measure("GAN2026 FROM_SCRATCH_SEED_INSTRUCTION", GAN2026_FROM_SCRATCH_SEED, enc),
    ]

    # Sort evolved by chars desc.
    evolved.sort(key=lambda m: m["chars"], reverse=True)

    over_wall = [m for m in evolved if m["exceeds_dspy_wall"]]

    def _row(m: dict, *, flag_col: bool = False) -> str:
        flag = ""
        if flag_col:
            flag = "YES" if m["exceeds_dspy_wall"] else ""
        return (
            f"{m['name']:<70} {m['chars']:>7} {m['tiktoken_tokens']:>7} "
            f"{m['approx_tokens']:>7} {m['policy_clauses']:>7} {flag:>5}"
        )

    print(f"=== GEPA policy-wall audit — dspy wall = {DSPY_POLICY_WALL_CHARS} chars ===")
    print(f"evolved seeds measured: {len(evolved)}; over wall: {len(over_wall)}")
    print()
    header = f"{'name':<70} {'chars':>7} {'tt_tok':>7} {'approx':>7} {'clauses':>7} {'wall':>5}"
    print(header)
    print("-" * len(header))
    print("OVER-THRESHOLD:")
    for m in over_wall:
        print(_row(m, flag_col=True))
    print()
    print("TOP 10 by chars (rest elided):")
    for m in evolved[:10]:
        print(_row(m, flag_col=True))
    print()
    print("UN-EVOLVED BASELINES:")
    for m in baselines:
        print(_row(m))
    print()

    # Dump full JSON for the note.
    out = {
        "dspy_policy_wall_chars": DSPY_POLICY_WALL_CHARS,
        "evolved_seeds_count": len(evolved),
        "over_wall_count": len(over_wall),
        "over_wall": over_wall,
        "baselines": baselines,
        "all_evolved": evolved,
    }
    out_path = EXPERIMENTS / "gepa_policy_wall_audit_2026-07-06.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[audit] full JSON -> {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
