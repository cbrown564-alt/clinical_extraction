#!/usr/bin/env python3
"""Edit-triggers-predeclaration gate (ExECTv2 pipeline-assumption audit, Phase 4).

Any change to the *measurement instrument* — the scoring layer, a deterministic
projection layer, or the drug lexicon — retroactively moves numbers the
manuscript and dossiers cite. This project already enforces, by convention, that
such a change be predeclared as a hypothesis and validated with a dev140 replay
(see ``PROJECT_STATUS.md`` -> Blocked/Guardrails and the pipeline-assumption
audit plan). This gate makes that convention structural: if a diff touches a
guarded file, the commit/PR message must reference a hypothesis_id that EXISTS in
``experiments/hypothesis_registry.jsonl`` and mention a dev140 replay.

This script never runs git. Feed it the changed paths (positional args or, with
``--stdin``, the output of ``git diff --name-only``) and the commit/PR message
(``--message`` or ``--message-file``). Wiring is documented in
``docs/runbooks/scorer_edit_predeclaration_gate.md``.

Exit codes
----------
0  no guarded files changed, or guarded files changed AND the message satisfies
   the predeclaration requirement.
1  guarded files changed but the message is missing / does not reference a known
   hypothesis_id / does not mention a dev140 replay.
2  usage / input error (e.g. registry not found).

Examples
--------
    git diff --cached --name-only | \\
        python scripts/check_scorer_edit_predeclaration.py --stdin --message-file "$1"

    python scripts/check_scorer_edit_predeclaration.py \\
        --message "rx_future_medication_regex_scope_bug_2026-07-02: dev140 replay ..." \\
        src/.../scoring/prescription.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


DEFAULT_REGISTRY = repo_root() / "experiments" / "hypothesis_registry.jsonl"

# (predicate on a forward-slashed path, human reason) — a file is guarded if any
# predicate matches. Kept as data so the runbook and this list stay in lockstep.
_GUARD_RULES: tuple[tuple[str, str], ...] = (
    ("exectv2/scoring/", "scoring layer (scored key builders)"),
    ("deterministic/conventions/", "deterministic projection: convention layer"),
    ("deterministic/target_projection/", "deterministic projection: target_projection"),
    ("deterministic/sf_state_projection.py", "deterministic projection: sf_state_projection"),
    ("contract/drug_lexicon.py", "contract lexicon (drug canonicalization)"),
)

# A dev140 replay must be mentioned (the corpus token) AND framed as a
# replay/re-score. Both signals required so a bare "dev140" mention in prose is
# not enough.
_DEV140_TOKEN_RE = re.compile(r"\bdev[\s_-]?140\b", re.IGNORECASE)
_REPLAY_TOKEN_RE = re.compile(r"\b(re-?play(?:ed|s)?|re-?scor(?:e|ed|ing)|re-?run)\b", re.IGNORECASE)


def _normalize(path: str) -> str:
    return path.strip().replace("\\", "/")


def guard_reason(path: str) -> str | None:
    """Return the reason ``path`` is guarded, or ``None`` if it is not."""

    normalized = _normalize(path)
    if not normalized:
        return None
    basename = normalized.rsplit("/", 1)[-1]
    for needle, reason in _GUARD_RULES:
        if needle in normalized:
            return reason
    # Generic projection-file convention: any *_projection*.py anywhere.
    if basename.endswith(".py") and "_projection" in basename:
        return "deterministic projection file (*_projection*)"
    return None


def guarded_files(paths: list[str]) -> list[tuple[str, str]]:
    guarded: list[tuple[str, str]] = []
    for path in paths:
        reason = guard_reason(path)
        if reason is not None:
            guarded.append((_normalize(path), reason))
    return guarded


def load_hypothesis_ids(registry_path: Path) -> set[str]:
    ids: set[str] = set()
    for line in registry_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        hid = record.get("hypothesis_id")
        if isinstance(hid, str) and hid:
            ids.add(hid)
    return ids


def referenced_hypothesis_ids(message: str, known_ids: set[str]) -> list[str]:
    return sorted(hid for hid in known_ids if hid in message)


def mentions_dev140_replay(message: str) -> bool:
    return bool(_DEV140_TOKEN_RE.search(message)) and bool(_REPLAY_TOKEN_RE.search(message))


def _read_message(args: argparse.Namespace) -> str:
    if args.message is not None:
        return args.message
    if args.message_file is not None:
        return Path(args.message_file).read_text(encoding="utf-8")
    return ""


def _collect_paths(args: argparse.Namespace) -> list[str]:
    paths = list(args.files)
    if args.stdin or not paths:
        paths.extend(line for line in sys.stdin.read().splitlines() if line.strip())
    return paths


def evaluate(
    paths: list[str],
    message: str,
    known_ids: set[str],
) -> tuple[int, list[str]]:
    """Return ``(exit_code, report_lines)``."""

    guarded = guarded_files(paths)
    if not guarded:
        return 0, ["scorer-edit predeclaration gate: OK (no guarded files changed)"]

    lines = [
        "scorer-edit predeclaration gate: guarded files changed:",
        *(f"  - {path}  [{reason}]" for path, reason in guarded),
    ]

    referenced = referenced_hypothesis_ids(message, known_ids)
    has_replay = mentions_dev140_replay(message)

    problems: list[str] = []
    if not message.strip():
        problems.append(
            "no commit/PR message provided (pass --message or --message-file)"
        )
    if not referenced:
        problems.append(
            "message references no hypothesis_id present in "
            "experiments/hypothesis_registry.jsonl "
            "(predeclare the change and cite its hypothesis_id)"
        )
    if not has_replay:
        problems.append(
            "message does not mention a dev140 replay "
            "(state the dev140 replay result / delta for the moved metric)"
        )

    if problems:
        lines.append("")
        lines.append("BLOCKED — a measurement-instrument edit must be predeclared:")
        lines.extend(f"  * {item}" for item in problems)
        lines.append("")
        lines.append(
            "See docs/runbooks/scorer_edit_predeclaration_gate.md. If this is a pure "
            "refactor with no scored-number change, say so explicitly and reference the "
            "hypothesis_id tracking that assertion + a dev140 no-change replay."
        )
        return 1, lines

    lines.append("")
    lines.append("OK — predeclaration satisfied:")
    lines.append(f"  referenced hypothesis_id(s): {', '.join(referenced)}")
    lines.append("  dev140 replay: mentioned")
    return 0, lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="changed file paths")
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="also read newline-separated changed paths from stdin "
        "(e.g. `git diff --name-only | ...`)",
    )
    parser.add_argument("--message", help="commit/PR message text")
    parser.add_argument("--message-file", help="path to a file holding the commit/PR message")
    parser.add_argument(
        "--registry",
        default=str(DEFAULT_REGISTRY),
        help="path to hypothesis_registry.jsonl",
    )
    args = parser.parse_args(argv)

    registry_path = Path(args.registry)
    if not registry_path.is_file():
        print(f"registry not found: {registry_path}", file=sys.stderr)
        return 2

    known_ids = load_hypothesis_ids(registry_path)
    paths = _collect_paths(args)
    message = _read_message(args)

    exit_code, report = evaluate(paths, message, known_ids)
    stream = sys.stdout if exit_code == 0 else sys.stderr
    for line in report:
        print(line, file=stream)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
